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

Avant toutes chose normalement cron fonctionne sur linux.

Pour pouvoir tester cron nous avons  donc :
-Etant sur windows ,utilisé WSL (windows Subsystem for Linux) pour simuler un environnement Linux compatible avec Cron (Commande utilisé : wsl --install -d Ubuntu ).

Après l'installation, nous avons utilisé la commande "wsl" pour lancé Linux ;
Par la suite accédé au dossier du projet avec la commande : (sur mon pc ) cd /mnt/c/Users/LENOVO/loganalyzer;

Ensuite nous avons ouvert l'éditeur Cron avec la commande : crontab -e et choisi l'éditeur nano (option 1);

Ajouter la ligne suivante pour tester le fonctionnement : * * * * * echo "cron ok" >> /mnt/c/Users/LENOVO/loganalyzer/test.txt ;

Après quelque minute nous avons vérifier le contenu du fichier avec :cat /mnt/c/Users/LENOVO/loganalyzer/test.txt. Et le fichier test.txt contenait plusieurs lignes "cron ok", ce qui prouve que cron marche 

Après tout ça , la commande prévu pour le projet est :

0 3 * * 0 python3 /mnt/c/Users/LENOVO/loganalyzer/main.py

Cela signifie que le programme sera exécuté tous les dimanches à 03h00.

Cela permet d’automatiser l’analyse des logs.