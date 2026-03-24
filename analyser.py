#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import glob
import argparse
import platform
from collections import Counter

NIVEAUX_VALIDES = ["ERROR", "WARN", "INFO", "ALL"]

PATTERN_LOG = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})\s+"
    r"(?P<heure>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<niveau>ERROR|WARN|INFO|DEBUG)\s+"
    r"(?P<message>.+)"
)

def get_infos_systeme() -> dict:
    """
    Récupère les informations système de la machine courante.
    Utilise os.environ pour l'utilisateur (évite os.getlogin qui peut échouer
    en environnement non interactif).

    Returns:
        dict: Dictionnaire contenant :
            - 'os'          : Nom du système d'exploitation (ex: 'Windows', 'Linux')
            - 'os_version'  : Version détaillée du système d'exploitation
            - 'utilisateur' : Nom de l'utilisateur connecté, ou 'inconnu' si introuvable
    """
    return {
        "os":          platform.system(),
        "os_version":  platform.version(),
        "utilisateur": os.environ.get("USERNAME") or os.environ.get("USER", "inconnu")
    }

def parser_ligne(ligne: str) -> dict | None:
    """
    Analyse une ligne de log brute et en extrait les champs structurés.
    Le format attendu est : YYYY-MM-DD HH:MM:SS NIVEAU message

    Args:
        ligne (str): Une ligne brute issue d'un fichier .log.

    Returns:
        dict | None: Dictionnaire contenant les champs 'date', 'heure', 'niveau'
                     et 'message' si la ligne correspond au pattern attendu,
                     None si la ligne ne correspond pas au format.
    """
    match = PATTERN_LOG.match(ligne.strip())
    if not match:
        return None
    return match.groupdict()

def lire_fichiers(source: str, niveau_filtre: str) -> list[dict]:
    """
    Parcourt tous les fichiers .log d'un dossier source et retourne
    les entrées parsées, filtrées selon le niveau demandé.
    Utilise glob pour scanner les fichiers et trie les résultats
    par ordre alphabétique.

    Args:
        source        (str): Chemin absolu ou relatif du dossier contenant les fichiers .log.
        niveau_filtre (str): Niveau de log à conserver ('ERROR', 'WARN', 'INFO', 'ALL').
                             Si 'ALL', aucun filtre n'est appliqué.

    Returns:
        list[dict]: Liste des entrées parsées, chaque entrée étant un dictionnaire
                    contenant 'date', 'heure', 'niveau', 'message' et 'fichier'.
    """
    entrees = []
    fichiers = sorted(glob.glob(os.path.join(source, "*.log")))

    if not fichiers:
        print(f"[analyser] Aucun fichier .log trouvé dans '{source}'")
        return entrees

    for chemin in fichiers:
        nom = os.path.basename(chemin)
        with open(chemin, "r", encoding="utf-8") as f:
            for ligne in f:
                parsed = parser_ligne(ligne)
                if not parsed:
                    continue
                # Filtre par niveau — ALL = tout passer
                if niveau_filtre != "ALL" and parsed["niveau"] != niveau_filtre:
                    continue
                parsed["fichier"] = nom
                entrees.append(parsed)

    return entrees

def calculer_statistiques(entrees: list[dict]) -> dict:
    """
    Calcule les statistiques globales à partir des entrées de logs parsées.
    Comptabilise le nombre total de lignes, le nombre d'occurrences par niveau
    (ERROR, WARN, INFO) et détermine les 5 messages d'erreur les plus fréquents
    via collections.Counter.

    Args:
        entrees (list[dict]): Liste des entrées parsées retournées par lire_fichiers().

    Returns:
        dict: Dictionnaire contenant :
            - 'total_lignes'     : Nombre total d'entrées analysées
            - 'comptage_niveaux' : Dictionnaire {'ERROR': int, 'WARN': int, 'INFO': int}
            - 'top5_erreurs'     : Liste des 5 messages ERROR les plus fréquents,
                                   chaque élément étant {'message': str, 'occurrences': int}
    """
    total = len(entrees)

    # Comptage par niveau
    comptage = {"ERROR": 0, "WARN": 0, "INFO": 0}
    for e in entrees:
        niveau = e["niveau"]
        if niveau in comptage:
            comptage[niveau] += 1

    # Top 5 erreurs
    messages_erreur = [e["message"] for e in entrees if e["niveau"] == "ERROR"]
    top5 = Counter(messages_erreur).most_common(5)

    return {
        "total_lignes":     total,
        "comptage_niveaux": comptage,
        "top5_erreurs":     [{"message": m, "occurrences": n} for m, n in top5]
    }

def analyser_logs(source: str, niveau_filtre: str = "ALL") -> dict:
    """
    Fonction principale du module. Orchestre la lecture des fichiers .log,
    le calcul des statistiques et la collecte des informations système.
    Retourne un dictionnaire structuré prêt à être consommé par rapport.py.

    Args:
        source        (str): Chemin du dossier contenant les fichiers .log à analyser.
        niveau_filtre (str): Niveau de filtrage à appliquer (défaut : 'ALL').
                             Valeurs acceptées : 'ERROR', 'WARN', 'INFO', 'ALL'.

    Returns:
        dict: Dictionnaire structuré contenant :
            - 'systeme'      : Informations système (OS, version, utilisateur)
            - 'parametres'   : Paramètres d'exécution (source, niveau_filtre)
            - 'statistiques' : Résultats de calculer_statistiques()
            - 'entrees'      : Liste complète des entrées parsées
    """
    entrees      = lire_fichiers(source, niveau_filtre)
    statistiques = calculer_statistiques(entrees)

    return {
        "systeme":      get_infos_systeme(),
        "parametres":   {"source": source, "niveau_filtre": niveau_filtre},
        "statistiques": statistiques,
        "entrees":      entrees
    }

# -- CLI --
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyseur de fichiers de logs")

    parser.add_argument(
        "--source",
        type=str,
        required=True,                    # obligatoire
        help="Chemin vers le dossier contenant les fichiers .log"
    )
    parser.add_argument(
        "--niveau",
        type=str,
        choices=NIVEAUX_VALIDES,          # ERROR, WARN, INFO, ALL
        default="ALL",                    # défaut : ALL
        help="Niveau de filtrage (défaut : ALL)"
    )
    args = parser.parse_args()

    resultat = analyser_logs(args.source, args.niveau)

    stats = resultat["statistiques"]
    sys_  = resultat["systeme"]
    print(f"\n=== Métadonnées ===")
    print(f"OS            : {sys_['os']} {sys_['os_version']}")
    print(f"Utilisateur   : {sys_['utilisateur']}")
    print(f"\n=== Statistiques ===")
    print(f"Total lignes  : {stats['total_lignes']}")
    print(f"Par niveau    : {stats['comptage_niveaux']}")
    print(f"Top 5 erreurs :")
    for item in stats["top5_erreurs"]:
        print(f"  [{item['occurrences']}x] {item['message']}")
