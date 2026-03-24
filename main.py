#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import glob
import importlib
import json
import os
import sys
from datetime import datetime


NIVEAUX_VALIDES = ["ERROR", "WARN", "INFO", "ALL"]


def charger_module(nom: str):
    """
    Charge dynamiquement un module Python par son nom via importlib.
    Permet à main.py d'importer analyser, rapport et archiver sans
    dépendances statiques, facilitant la modularité du projet.

    Args:
        nom (str): Nom du module à importer (ex: 'analyser', 'rapport', 'archiver').

    Returns:
        module: Le module Python importé et prêt à l'emploi.

    Raises:
        RuntimeError: Si le module est introuvable ou provoque une erreur à l'import.
    """
    try:
        return importlib.import_module(nom)
    except Exception as exc:
        raise RuntimeError(f"Impossible de charger le module '{nom}': {exc}") from exc


def recuperer_fonction(module, noms_possibles: list[str]):
    """
    Recherche et retourne la première fonction callable trouvée dans un module
    parmi une liste de noms candidats. Permet de gérer les variantes de nommage
    entre les différentes implémentations des modules étudiants.

    Args:
        module          : Module Python dans lequel chercher la fonction.
        noms_possibles  (list[str]): Liste ordonnée de noms de fonctions à tester,
                                     par ordre de priorité.

    Returns:
        callable: La première fonction trouvée et appelable dans le module.

    Raises:
        AttributeError: Si aucun des noms testés ne correspond à une fonction callable
                        dans le module.
    """
    for nom in noms_possibles:
        fonction = getattr(module, nom, None)
        if callable(fonction):
            return fonction
    raise AttributeError(
        f"Aucune fonction compatible trouvée dans {module.__name__}. "
        f"Noms testés: {', '.join(noms_possibles)}"
    )


def ecrire_rapport_fallback(donnees: dict, dossier_rapports: str) -> str:
    """
    Génère un rapport JSON minimal en cas d'échec ou d'incomplétude du module rapport.py.
    Sert de filet de sécurité pour garantir qu'un rapport est toujours produit,
    même si le module rapport est absent ou ne contient pas de fonction compatible.

    Args:
        donnees         (dict): Données brutes retournées par le module d'analyse.
        dossier_rapports (str): Chemin du dossier où écrire le rapport de secours.

    Returns:
        str: Chemin absolu du fichier JSON de secours généré.
    """
    os.makedirs(dossier_rapports, exist_ok=True)
    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    chemin_rapport = os.path.join(dossier_rapports, f"rapport_{horodatage}.json")

    with open(chemin_rapport, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, ensure_ascii=False, indent=2)

    print("[AVERTISSEMENT] rapport.py est incomplet, fallback JSON interne utilisé.")
    print(f"[OK] Rapport JSON généré : {chemin_rapport}")
    return chemin_rapport


def generer_rapport(module_rapport, donnees: dict, dossier_rapports: str) -> str:
    """
    Tente de générer un rapport JSON via le module rapport.py en cherchant
    une fonction compatible parmi plusieurs noms candidats. Si aucune fonction
    n'est trouvée ou si la génération échoue, bascule automatiquement sur
    ecrire_rapport_fallback() pour garantir la continuité du pipeline.

    Args:
        module_rapport   : Module rapport.py chargé dynamiquement.
        donnees   (dict) : Données d'analyse à inclure dans le rapport.
        dossier_rapports (str): Chemin du dossier de destination du rapport.

    Returns:
        str: Chemin absolu du fichier JSON généré (par rapport.py ou par le fallback).
    """
    fonctions_possibles = [
        "generer_rapport_json",
        "generer_rapport",
        "sauvegarder_rapport_json",
        "creer_rapport_json",
    ]

    try:
        fonction = recuperer_fonction(module_rapport, fonctions_possibles)
    except AttributeError:
        return ecrire_rapport_fallback(donnees, dossier_rapports)

    os.makedirs(dossier_rapports, exist_ok=True)

    try:
        resultat = fonction(donnees, dossier_rapports)
    except TypeError:
        resultat = fonction(donnees)

    if isinstance(resultat, str):
        print(f"[OK] Rapport JSON généré : {resultat}")
        return resultat

    if isinstance(resultat, dict) and "chemin_rapport" in resultat:
        chemin = resultat["chemin_rapport"]
        print(f"[OK] Rapport JSON généré : {chemin}")
        return chemin

    return ecrire_rapport_fallback(donnees, dossier_rapports)


def orchestrer_pipeline(source: str, niveau: str, dossier_rapports: str, dossier_backups: str, retention: int) -> int:
    """
    Orchestre l'enchaînement complet des quatre étapes du pipeline LogAnalyzer :
      1. Chargement dynamique des modules analyser, rapport et archiver
      2. Analyse des fichiers .log selon le niveau de filtre demandé
      3. Génération du rapport JSON (avec fallback si nécessaire)
      4. Archivage des fichiers .log traités et nettoyage des anciens rapports

    Args:
        source           (str): Chemin absolu du dossier contenant les fichiers .log.
        niveau           (str): Niveau de filtrage à appliquer ('ERROR', 'WARN', 'INFO', 'ALL').
        dossier_rapports (str): Chemin absolu du dossier de sortie des rapports JSON.
        dossier_backups  (str): Chemin absolu du dossier de destination des archives .tar.gz.
        retention        (int): Durée de rétention des rapports en jours avant suppression.

    Returns:
        int: Code de retour du pipeline — 0 si succès, 1 en cas d'erreur à n'importe quelle étape.
    """
    module_analyser = charger_module("analyser")
    module_rapport = charger_module("rapport")
    module_archiver = charger_module("archiver")

    fonction_analyse = recuperer_fonction(module_analyser, ["analyser_logs"])
    fonction_archivage = recuperer_fonction(module_archiver, ["archiver_logs"])
    fonction_nettoyage = recuperer_fonction(module_archiver, ["nettoyer_anciens_rapports"])

    print(f"[INFO] Source des logs : {source}")
    print(f"[INFO] Niveau de filtre : {niveau}")

    try:
        donnees_analyse = fonction_analyse(source, niveau)
        print("[OK] Analyse des logs terminée.")
    except Exception as exc:
        print(f"[ERREUR] Échec du module d'analyse : {exc}")
        return 1

    try:
        chemin_rapport = generer_rapport(module_rapport, donnees_analyse, dossier_rapports)
    except Exception as exc:
        print(f"[ERREUR] Échec de la génération du rapport : {exc}")
        return 1

    fichiers_logs = sorted(glob.glob(os.path.join(source, "*.log")))
    if not fichiers_logs:
        print("[ERREUR] Aucun fichier .log trouvé à archiver.")
        return 1

    try:
        archive = fonction_archivage(fichiers_logs, dossier_backups)
        fonction_nettoyage(dossier_rapports, retention)
    except Exception as exc:
        print(f"[ERREUR] Échec du module d'archivage : {exc}")
        return 1

    print("[SUCCES] Pipeline terminé.")
    print(f"[INFO] Rapport : {chemin_rapport}")
    if archive:
        print(f"[INFO] Archive : {archive}")
    return 0


def main():
    """
    Point d'entrée principal du programme. Configure et parse les arguments
    de la ligne de commande, vérifie l'existence du dossier source, puis
    lance orchestrer_pipeline() avec les paramètres fournis.
    Quitte avec le code de retour du pipeline (0 = succès, 1 = erreur).
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="LogAnalyzer Pro — Module 4 : Orchestration")
    parser.add_argument(
        "--source",
        default=os.path.join(base_dir, "logs_test"),
        help="Dossier contenant les fichiers .log",
    )
    parser.add_argument(
        "--niveau",
        choices=NIVEAUX_VALIDES,
        default="ALL",
        help="Niveau de filtrage (défaut : ALL)",
    )
    parser.add_argument(
        "--rapports",
        default=os.path.join(base_dir, "rapports"),
        help="Dossier de sortie des rapports JSON",
    )
    parser.add_argument(
        "--backups",
        default=os.path.join(base_dir, "backups"),
        help="Dossier de sortie des archives",
    )
    parser.add_argument(
        "--retention",
        type=int,
        default=30,
        help="Durée de rétention des rapports en jours",
    )
    args = parser.parse_args()

    source = os.path.abspath(args.source)
    dossier_rapports = os.path.abspath(args.rapports)
    dossier_backups = os.path.abspath(args.backups)

    if not os.path.isdir(source):
        print(f"[ERREUR] Dossier source introuvable : {source}")
        sys.exit(1)

    code_retour = orchestrer_pipeline(
        source=source,
        niveau=args.niveau,
        dossier_rapports=dossier_rapports,
        dossier_backups=dossier_backups,
        retention=args.retention,
    )
    sys.exit(code_retour)


if __name__ == "__main__":
    main()
