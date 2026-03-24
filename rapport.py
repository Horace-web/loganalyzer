#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import datetime
import platform

def generer_rapport_json(donnees_analyse, dossier_source):
    """
    Transforme les données d'analyse en un fichier rapport JSON structuré et horodaté.
    Gère deux formats d'entrée possibles :
      - Structure imbriquée : telle que retournée par analyser_logs() via main.py,
        avec une clé 'statistiques' contenant 'total_lignes', 'comptage_niveaux', etc.
      - Structure plate : données déjà extraites et aplaties, passées directement
        avec les clés 'total_lignes', 'par_niveau', 'top5_erreurs', 'fichiers_traites'.

    Le rapport final est écrit dans le sous-dossier 'rapports/' situé au même niveau
    que ce script, sous le nom rapport_YYYY-MM-DD.json.

    Args:
        donnees_analyse (dict): Dictionnaire contenant les résultats de l'analyse,
                                au format imbriqué (sortie de analyser_logs) ou plat.
        dossier_source  (str) : Chemin du dossier source analysé, inclus dans les
                                métadonnées du rapport.

    Returns:
        str: Chemin absolu du fichier JSON généré.
    """
    maintenant = datetime.datetime.now()
    date_str = maintenant.strftime("%Y-%m-%d %H:%M:%S")
    nom_utilisateur = os.environ.get('USERNAME') or os.environ.get('USER', 'Inconnu')
    systeme_exploitation = platform.system()

    # Détection de la structure : imbriquée (venant de main.py)
    # ou plate (appelée directement depuis __main__)
    if "statistiques" in donnees_analyse:
        stats = donnees_analyse["statistiques"]
        total_lignes = stats.get("total_lignes", 0)
        par_niveau = stats.get("comptage_niveaux", stats.get("par_niveau", {"ERROR": 0, "WARN": 0, "INFO": 0}))
        top5_erreurs = stats.get("top5_erreurs", [])
        entrees = donnees_analyse.get("entrees", [])
        fichiers_traites = list(set([e["fichier"] for e in entrees])) if entrees else donnees_analyse.get("fichiers_traites", [])
    else:
        # Structure plate (appelée manuellement avec données déjà extraites)
        total_lignes = donnees_analyse.get("total_lignes", 0)
        par_niveau = donnees_analyse.get("par_niveau", {"ERROR": 0, "WARN": 0, "INFO": 0})
        top5_erreurs = donnees_analyse.get("top5_erreurs", [])
        fichiers_traites = donnees_analyse.get("fichiers_traites", [])

    rapport_final = {
        "metadata": {
            "date": date_str,
            "utilisateur": nom_utilisateur,
            "os": systeme_exploitation,
            "source": os.path.abspath(dossier_source)
        },
        "statistiques": {
            "total_lignes": total_lignes,
            "par_niveau": par_niveau,
            "top5_erreurs": top5_erreurs
        },
        "fichiers_traites": fichiers_traites
    }

    base_dir = os.path.dirname(os.path.abspath(__file__))
    dossier_rapports = os.path.join(base_dir, 'rapports')
    os.makedirs(dossier_rapports, exist_ok=True)

    nom_fichier = f"rapport_{maintenant.strftime('%Y-%m-%d')}.json"
    chemin_complet = os.path.join(dossier_rapports, nom_fichier)

    with open(chemin_complet, 'w', encoding='utf-8') as f:
        json.dump(rapport_final, f, indent=4, ensure_ascii=False)

    return chemin_complet


if __name__ == "__main__":
    """
    Point d'entrée pour l'utilisation autonome du module rapport.py.
    Charge le module analyser, exécute une analyse complète sur le dossier
    logs_test/ avec le niveau ALL, prépare les données au format plat attendu
    par generer_rapport_json(), puis génère le rapport et affiche son chemin.
    Affiche un message d'erreur si une exception survient à n'importe quelle étape.
    """
    try:
        import analyser
        dossier_source_test = "logs_test/"
        resultat_brut = analyser.analyser_logs(dossier_source_test, "ALL")

        # Préparation des données pour ton module
        donnees_pour_audrey = {
            "total_lignes": resultat_brut["statistiques"]["total_lignes"],
            "par_niveau": resultat_brut["statistiques"]["comptage_niveaux"],

            # ICI : On récupère directement la liste avec les occurrences d'Horace
            "top5_erreurs": resultat_brut["statistiques"]["top5_erreurs"],

            "fichiers_traites": list(set([e["fichier"] for e in resultat_brut["entrees"]]))
        }

        chemin = generer_rapport_json(donnees_pour_audrey, dossier_source_test)
        print(f"Succès ! Rapport détaillé généré : {chemin}")

    except Exception as e:
        print(f"Erreur : {e}")
