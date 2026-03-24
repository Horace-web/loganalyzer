#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import datetime
import platform

def generer_rapport_json(donnees_analyse, dossier_source):
    """
    Transforme les données d'analyse en un fichier JSON structuré et horodaté.
    
    Args:
        donnees_analyse (dict): Dictionnaire contenant le total_lignes, 
                               par_niveau, top5_erreurs et fichiers_traites.
        dossier_source (str): Le chemin du dossier source analysé.
        
    Returns:
        str: Le chemin absolu du fichier JSON généré.
    """
    # 1. Préparation des métadonnées [cite: 73, 76]
    maintenant = datetime.datetime.now()
    date_str = maintenant.strftime("%Y-%m-%d %H:%M:%S")
    nom_utilisateur = os.environ.get('USERNAME') or os.environ.get('USER', 'Inconnu')
    systeme_exploitation = platform.system()

    # 2. Construction de la structure JSON imposée [cite: 75, 76]
    rapport_final = {
        "metadata": {
            "date": date_str,
            "utilisateur": nom_utilisateur,
            "os": systeme_exploitation,
            "source": os.path.abspath(dossier_source)
        },
        "statistiques": {
            "total_lignes": donnees_analyse.get("total_lignes", 0),
            "par_niveau": donnees_analyse.get("par_niveau", {"ERROR": 0, "WARN": 0, "INFO": 0}),
            "top5_erreurs": donnees_analyse.get("top5_erreurs", [])  # Accepte maintenant la liste détaillée
        },
        "fichiers_traites": donnees_analyse.get("fichiers_traites", [])
    }

    # 3. Gestion des chemins absolus avec __file__ [cite: 20, 88, 101]
    # On remonte au dossier parent du script pour trouver le dossier 'rapports'
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dossier_rapports = os.path.join(base_dir, 'rapports')

    # Création du dossier s'il n'existe pas
    if not os.path.exists(dossier_rapports):
        os.makedirs(dossier_rapports)

    # Nom du fichier : rapport_YYYY-MM-DD.json [cite: 75]
    nom_fichier = f"rapport_{maintenant.strftime('%Y-%m-%d')}.json"
    chemin_complet = os.path.join(dossier_rapports, nom_fichier)

    # 4. Écriture du fichier JSON [cite: 19]
    with open(chemin_complet, 'w', encoding='utf-8') as f:
        json.dump(rapport_final, f, indent=4, ensure_ascii=False)

    return chemin_complet

# RECOLLE CETTE LIGNE TOUT À GAUCHE SANS ESPACE
if __name__ == "__main__":
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

        