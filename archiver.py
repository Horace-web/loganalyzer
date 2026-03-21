"""
Module 3 — Archivage et Nettoyage
LogAnalyzer Pro — archiver.py

Responsabilités :
  - Archiver les fichiers .log traités dans une archive .tar.gz
  - Déplacer l'archive vers le dossier de destination
  - Supprimer les anciens rapports JSON selon une politique de rétention
  - Vérifier l'espace disque disponible avant d'archiver
"""

import os
import tarfile
import shutil
import time
import subprocess
import argparse
from datetime import datetime


# ---------------------------------------------------------------------------
# 1. Vérification de l'espace disque
# ---------------------------------------------------------------------------

def verifier_espace_disque(dossier: str, espace_min_mo: int = 100) -> bool:
    """
    Vérifie l'espace disque disponible sur la partition du dossier donné.

    Args:
        dossier      : Chemin du dossier à contrôler.
        espace_min_mo: Espace minimum requis en Mo (défaut : 100 Mo).

    Returns:
        True si l'espace est suffisant, False sinon.
    """
    try:
        # Utilisation de subprocess pour appeler 'df' (compatible Linux/macOS)
        resultat = subprocess.run(
            ["df", "-m", dossier],          # -m = résultat en Mo
            capture_output=True,
            text=True,
            check=True
        )
        lignes = resultat.stdout.strip().splitlines()
        # La deuxième ligne contient les données : Filesystem  1M-blocks  Used  Available  ...
        donnees = lignes[1].split()
        espace_disponible_mo = int(donnees[3])

        print(f"[INFO] Espace disque disponible : {espace_disponible_mo} Mo "
              f"(minimum requis : {espace_min_mo} Mo)")

        if espace_disponible_mo < espace_min_mo:
            print(f"[ERREUR] Espace insuffisant pour archiver.")
            return False
        return True

    except (subprocess.CalledProcessError, IndexError, ValueError) as e:
        print(f"[AVERTISSEMENT] Impossible de vérifier l'espace disque : {e}")
        # On laisse passer en cas d'erreur de vérification
        return True


# ---------------------------------------------------------------------------
# 2. Création de l'archive .tar.gz
# ---------------------------------------------------------------------------

def archiver_logs(fichiers_logs: list, dossier_dest: str) -> str | None:
    """
    Crée une archive compressée .tar.gz contenant tous les fichiers .log traités,
    puis la déplace vers le dossier de destination.

    Args:
        fichiers_logs : Liste des chemins absolus des fichiers .log à archiver.
        dossier_dest  : Dossier de destination pour l'archive finale.

    Returns:
        Chemin de l'archive créée, ou None en cas d'échec.
    """
    if not fichiers_logs:
        print("[AVERTISSEMENT] Aucun fichier .log à archiver.")
        return None

    # Nom de l'archive horodaté
    date_str = datetime.now().strftime("%Y-%m-%d")
    nom_archive = f"backup_{date_str}.tar.gz"

    # Création dans un dossier temporaire d'abord
    chemin_temp = os.path.join("/tmp", nom_archive)

    # Vérification de l'espace avant de commencer
    if not verifier_espace_disque(dossier_dest):
        return None

    try:
        print(f"[INFO] Création de l'archive : {nom_archive}")
        with tarfile.open(chemin_temp, "w:gz") as archive:
            for fichier in fichiers_logs:
                if os.path.isfile(fichier):
                    # On ajoute le fichier avec seulement son nom (pas le chemin complet)
                    archive.add(fichier, arcname=os.path.basename(fichier))
                    print(f"  + Ajouté : {os.path.basename(fichier)}")
                else:
                    print(f"  [AVERTISSEMENT] Fichier introuvable, ignoré : {fichier}")

        # Déplacement de l'archive vers le dossier de destination
        os.makedirs(dossier_dest, exist_ok=True)
        chemin_final = os.path.join(dossier_dest, nom_archive)
        shutil.move(chemin_temp, chemin_final)

        print(f"[OK] Archive déplacée vers : {chemin_final}")
        return chemin_final

    except (tarfile.TarError, OSError) as e:
        print(f"[ERREUR] Échec de la création de l'archive : {e}")
        # Nettoyage du fichier temporaire si nécessaire
        if os.path.exists(chemin_temp):
            os.remove(chemin_temp)
        return None


# ---------------------------------------------------------------------------
# 3. Nettoyage des anciens rapports JSON
# ---------------------------------------------------------------------------

def nettoyer_anciens_rapports(dossier_rapports: str, retention_jours: int = 30) -> int:
    """
    Supprime les rapports JSON dont l'âge dépasse la politique de rétention.

    Args:
        dossier_rapports : Dossier contenant les fichiers rapport_*.json.
        retention_jours  : Durée de rétention en jours (défaut : 30).

    Returns:
        Nombre de fichiers supprimés.
    """
    if not os.path.isdir(dossier_rapports):
        print(f"[AVERTISSEMENT] Dossier de rapports introuvable : {dossier_rapports}")
        return 0

    maintenant = time.time()
    limite_secondes = retention_jours * 24 * 3600   # conversion jours → secondes
    compteur = 0

    print(f"[INFO] Nettoyage des rapports JSON de plus de {retention_jours} jours "
          f"dans : {dossier_rapports}")

    for nom_fichier in os.listdir(dossier_rapports):
        # On ne cible que les rapports JSON générés par le module 2
        if not (nom_fichier.startswith("rapport_") and nom_fichier.endswith(".json")):
            continue

        chemin_fichier = os.path.join(dossier_rapports, nom_fichier)

        try:
            # os.path.getmtime() retourne le timestamp de dernière modification
            age_fichier = maintenant - os.path.getmtime(chemin_fichier)

            if age_fichier > limite_secondes:
                os.remove(chemin_fichier)
                age_jours = age_fichier / (24 * 3600)
                print(f"  - Supprimé : {nom_fichier} (âge : {age_jours:.1f} jours)")
                compteur += 1

        except OSError as e:
            print(f"  [ERREUR] Impossible de traiter {nom_fichier} : {e}")

    if compteur == 0:
        print("[INFO] Aucun rapport à supprimer.")
    else:
        print(f"[OK] {compteur} rapport(s) supprimé(s).")

    return compteur


# ---------------------------------------------------------------------------
# 4. Point d'entrée CLI (utilisation autonome du module)
# ---------------------------------------------------------------------------

def main():
    """
    Interface CLI du module d'archivage.
    Permet d'appeler archiver.py directement depuis le terminal.
    """
    parser = argparse.ArgumentParser(
        description="LogAnalyzer Pro — Module 3 : Archivage et Nettoyage"
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Dossier contenant les fichiers .log à archiver"
    )
    parser.add_argument(
        "--dest",
        required=True,
        help="Dossier de destination pour l'archive .tar.gz"
    )
    parser.add_argument(
        "--rapports",
        default=None,
        help="Dossier contenant les rapports JSON à nettoyer (optionnel)"
    )
    parser.add_argument(
        "--retention",
        type=int,
        default=30,
        help="Durée de rétention des rapports en jours (défaut : 30)"
    )

    args = parser.parse_args()

    # Construction des chemins absolus à partir de __file__
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dossier_source = os.path.abspath(args.source)
    dossier_dest   = os.path.abspath(args.dest)

    # Récupération des fichiers .log dans le dossier source
    if not os.path.isdir(dossier_source):
        print(f"[ERREUR] Dossier source introuvable : {dossier_source}")
        import sys; sys.exit(1)

    fichiers_logs = [
        os.path.join(dossier_source, f)
        for f in os.listdir(dossier_source)
        if f.endswith(".log")
    ]

    # Étape 1 — Archivage
    archiver_logs(fichiers_logs, dossier_dest)

    # Étape 2 — Nettoyage des rapports (si un dossier est fourni)
    if args.rapports:
        dossier_rapports = os.path.abspath(args.rapports)
        nettoyer_anciens_rapports(dossier_rapports, args.retention)


if __name__ == "__main__":
    main()