#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module 3 — Archivage et Nettoyage
"""

import os
import tarfile
import shutil
import time
import argparse
from datetime import datetime


def verifier_espace_disque(dossier: str, espace_min_mo: int = 100) -> bool:
    try:
        usage = shutil.disk_usage(dossier)
        espace_disponible_mo = usage.free // (1024 * 1024)

        print(
            f"[INFO] Espace disque disponible : {espace_disponible_mo} Mo "
            f"(minimum requis : {espace_min_mo} Mo)"
        )

        if espace_disponible_mo < espace_min_mo:
            print("[ERREUR] Espace insuffisant pour archiver.")
            return False
        return True
    except OSError as exc:
        print(f"[AVERTISSEMENT] Impossible de vérifier l'espace disque : {exc}")
        return True


def archiver_logs(fichiers_logs: list, dossier_dest: str) -> str | None:
    if not fichiers_logs:
        print("[AVERTISSEMENT] Aucun fichier .log à archiver.")
        return None

    date_str = datetime.now().strftime("%Y-%m-%d")
    nom_archive = f"backup_{date_str}.tar.gz"
    temp_root = os.environ.get("TEMP") or os.environ.get("TMP") or "/tmp"
    chemin_temp = os.path.join(temp_root, nom_archive)

    if not verifier_espace_disque(dossier_dest):
        return None

    try:
        print(f"[INFO] Création de l'archive : {nom_archive}")
        with tarfile.open(chemin_temp, "w:gz") as archive:
            for fichier in fichiers_logs:
                if os.path.isfile(fichier):
                    archive.add(fichier, arcname=os.path.basename(fichier))
                    print(f"  + Ajouté : {os.path.basename(fichier)}")
                else:
                    print(f"  [AVERTISSEMENT] Fichier introuvable, ignoré : {fichier}")

        os.makedirs(dossier_dest, exist_ok=True)
        chemin_final = os.path.join(dossier_dest, nom_archive)
        shutil.move(chemin_temp, chemin_final)

        print(f"[OK] Archive déplacée vers : {chemin_final}")
        return chemin_final
    except (tarfile.TarError, OSError) as exc:
        print(f"[ERREUR] Échec de la création de l'archive : {exc}")
        if os.path.exists(chemin_temp):
            os.remove(chemin_temp)
        return None


def nettoyer_anciens_rapports(dossier_rapports: str, retention_jours: int = 30) -> int:
    if not os.path.isdir(dossier_rapports):
        print(f"[AVERTISSEMENT] Dossier de rapports introuvable : {dossier_rapports}")
        return 0

    maintenant = time.time()
    limite_secondes = retention_jours * 24 * 3600
    compteur = 0

    print(
        f"[INFO] Nettoyage des rapports JSON de plus de {retention_jours} jours "
        f"dans : {dossier_rapports}"
    )

    for nom_fichier in os.listdir(dossier_rapports):
        if not (nom_fichier.startswith("rapport_") and nom_fichier.endswith(".json")):
            continue

        chemin_fichier = os.path.join(dossier_rapports, nom_fichier)

        try:
            age_fichier = maintenant - os.path.getmtime(chemin_fichier)

            if age_fichier > limite_secondes:
                os.remove(chemin_fichier)
                age_jours = age_fichier / (24 * 3600)
                print(f"  - Supprimé : {nom_fichier} (âge : {age_jours:.1f} jours)")
                compteur += 1
        except OSError as exc:
            print(f"  [ERREUR] Impossible de traiter {nom_fichier} : {exc}")

    if compteur == 0:
        print("[INFO] Aucun rapport à supprimer.")
    else:
        print(f"[OK] {compteur} rapport(s) supprimé(s).")

    return compteur


def main():
    parser = argparse.ArgumentParser(description="LogAnalyzer Pro — Module 3 : Archivage et Nettoyage")
    parser.add_argument("--source", required=True, help="Dossier contenant les fichiers .log à archiver")
    parser.add_argument("--dest", required=True, help="Dossier de destination pour l'archive .tar.gz")
    parser.add_argument(
        "--rapports",
        default=None,
        help="Dossier contenant les rapports JSON à nettoyer (optionnel)",
    )
    parser.add_argument(
        "--retention",
        type=int,
        default=30,
        help="Durée de rétention des rapports en jours (défaut : 30)",
    )

    args = parser.parse_args()

    dossier_source = os.path.abspath(args.source)
    dossier_dest = os.path.abspath(args.dest)

    if not os.path.isdir(dossier_source):
        print(f"[ERREUR] Dossier source introuvable : {dossier_source}")
        import sys

        sys.exit(1)

    fichiers_logs = [
        os.path.join(dossier_source, nom)
        for nom in os.listdir(dossier_source)
        if nom.endswith(".log")
    ]

    archiver_logs(fichiers_logs, dossier_dest)

    if args.rapports:
        dossier_rapports = os.path.abspath(args.rapports)
        nettoyer_anciens_rapports(dossier_rapports, args.retention)


if __name__ == "__main__":
    main()
