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
    try:
        return importlib.import_module(nom)
    except Exception as exc:
        raise RuntimeError(f"Impossible de charger le module '{nom}': {exc}") from exc


def recuperer_fonction(module, noms_possibles: list[str]):
    for nom in noms_possibles:
        fonction = getattr(module, nom, None)
        if callable(fonction):
            return fonction
    raise AttributeError(
        f"Aucune fonction compatible trouvée dans {module.__name__}. "
        f"Noms testés: {', '.join(noms_possibles)}"
    )


def ecrire_rapport_fallback(donnees: dict, dossier_rapports: str) -> str:
    os.makedirs(dossier_rapports, exist_ok=True)
    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    chemin_rapport = os.path.join(dossier_rapports, f"rapport_{horodatage}.json")

    with open(chemin_rapport, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier, ensure_ascii=False, indent=2)

    print("[AVERTISSEMENT] rapport.py est incomplet, fallback JSON interne utilisé.")
    print(f"[OK] Rapport JSON généré : {chemin_rapport}")
    return chemin_rapport


def generer_rapport(module_rapport, donnees: dict, dossier_rapports: str) -> str:
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
