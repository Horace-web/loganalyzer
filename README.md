# LogAnalyzer

## Description
Ce projet consiste à analyser des fichiers logs, afficher des statistiques et générer un fichier JSON avec les résultats. Et par la suite, les fichiers logs sont archivés.

## Objectif
Le but est de faciliter l’analyse  sans le faire manuellement.

## Structure du projet
- analyser.py : permet de lire et analyser les fichiers logs
- rapport.py : permet de créer un fichier JSON avec les résultats
- archiver.py : permet de compresser et sauvegarder les logs
- main.py : lance tout le programme
- logs_test/ : contient les fichiers logs de test

## Utilisation
Pour lancer le programme :
python main.py

## Planification
Le programme peut être exécuté automatiquement avec cron :

0 3 * * 0 python main.py