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
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "utilisateur": os.environ.get("USERNAME") or os.environ.get("USER", "inconnu"),
    }


def parser_ligne(ligne: str) -> dict | None:
    match = PATTERN_LOG.match(ligne.strip())
    if not match:
        return None
    return match.groupdict()


def lire_fichiers(source: str, niveau_filtre: str) -> list[dict]:
    entrees = []
    fichiers = sorted(glob.glob(os.path.join(source, "*.log")))

    if not fichiers:
        print(f"[analyser] Aucun fichier .log trouvé dans '{source}'")
        return entrees

    for chemin in fichiers:
        nom = os.path.basename(chemin)
        with open(chemin, "r", encoding="utf-8") as fichier:
            for ligne in fichier:
                parsed = parser_ligne(ligne)
                if not parsed:
                    continue
                if niveau_filtre != "ALL" and parsed["niveau"] != niveau_filtre:
                    continue
                parsed["fichier"] = nom
                entrees.append(parsed)

    return entrees


def calculer_statistiques(entrees: list[dict]) -> dict:
    total = len(entrees)

    comptage = {"ERROR": 0, "WARN": 0, "INFO": 0}
    for entree in entrees:
        niveau = entree["niveau"]
        if niveau in comptage:
            comptage[niveau] += 1

    messages_erreur = [entree["message"] for entree in entrees if entree["niveau"] == "ERROR"]
    top5 = Counter(messages_erreur).most_common(5)

    return {
        "total_lignes": total,
        "comptage_niveaux": comptage,
        "top5_erreurs": [{"message": message, "occurrences": occurrences} for message, occurrences in top5],
    }


def analyser_logs(source: str, niveau_filtre: str = "ALL") -> dict:
    entrees = lire_fichiers(source, niveau_filtre)
    statistiques = calculer_statistiques(entrees)

    return {
        "systeme": get_infos_systeme(),
        "parametres": {"source": source, "niveau_filtre": niveau_filtre},
        "statistiques": statistiques,
        "entrees": entrees,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyseur de fichiers de logs")
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Chemin vers le dossier contenant les fichiers .log",
    )
    parser.add_argument(
        "--niveau",
        type=str,
        choices=NIVEAUX_VALIDES,
        default="ALL",
        help="Niveau de filtrage (défaut : ALL)",
    )
    args = parser.parse_args()

    resultat = analyser_logs(args.source, args.niveau)

    stats = resultat["statistiques"]
    infos_systeme = resultat["systeme"]
    print("\n=== Métadonnées ===")
    print(f"OS            : {infos_systeme['os']} {infos_systeme['os_version']}")
    print(f"Utilisateur   : {infos_systeme['utilisateur']}")
    print("\n=== Statistiques ===")
    print(f"Total lignes  : {stats['total_lignes']}")
    print(f"Par niveau    : {stats['comptage_niveaux']}")
    print("Top 5 erreurs :")
    for item in stats["top5_erreurs"]:
        print(f"  [{item['occurrences']}x] {item['message']}")
