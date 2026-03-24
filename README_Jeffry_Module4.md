#!/usr/bin/env markdown

# README - Jeffry - Module 4 Orchestration

## 1. Mon role dans le projet

Je suis responsable du **Module 4 : Orchestration**, implemente dans `main.py`.

Mon travail consiste a :

- lancer les autres modules dans le bon ordre ;
- verifier que chaque etape se passe correctement ;
- arreter proprement le programme si une etape echoue ;
- afficher des messages clairs pour suivre l'execution ;
- preparer les chemins des dossiers utilises par le projet.

En pratique, `main.py` est le **chef d'orchestre** du projet :

1. il appelle `analyser.py` pour lire les logs ;
2. il appelle `rapport.py` pour generer le rapport JSON ;
3. il appelle `archiver.py` pour archiver les logs ;
4. il lance le nettoyage des anciens rapports.

## 2. Ce que fait exactement `main.py`

Le fichier `main.py` contient plusieurs parties importantes.

### a. Chargement dynamique des modules

La fonction `charger_module(nom)` importe les modules Python necessaires :

- `analyser`
- `rapport`
- `archiver`

Cela permet de separer proprement les responsabilites entre les fichiers.

### b. Verification des fonctions disponibles

La fonction `recuperer_fonction(module, noms_possibles)` sert a verifier qu'une fonction attendue existe bien dans un module.

Exemples :

- `analyser_logs` dans `analyser.py`
- `archiver_logs` dans `archiver.py`
- `nettoyer_anciens_rapports` dans `archiver.py`

Si une fonction n'existe pas, l'orchestrateur le detecte et peut s'arreter proprement avec un message d'erreur clair.

### c. Generation du rapport JSON

La fonction `generer_rapport(...)` essaie d'utiliser `rapport.py`.

Comme `rapport.py` est encore vide dans le depot actuel, j'ai ajoute un **fallback** :

- si le module de rapport n'est pas pret, `main.py` ecrit lui-meme un fichier JSON dans le dossier `rapports/`.

Cela permet a ton module de continuer a fonctionner et de demontrer toute la chaine du projet meme si le module 2 n'est pas termine.

### d. Orchestration du pipeline complet

La fonction principale du module est `orchestrer_pipeline(...)`.

Elle suit cet ordre :

1. charger les modules ;
2. lancer l'analyse des logs ;
3. generer le rapport JSON ;
4. recuperer la liste des fichiers `.log` ;
5. lancer l'archivage ;
6. nettoyer les anciens rapports ;
7. afficher le resultat final.

Chaque etape est protegee par des blocs `try/except`.

Donc :

- si l'analyse echoue, le programme s'arrete ;
- si la generation du rapport echoue, le programme s'arrete ;
- si l'archivage echoue, le programme s'arrete ;
- sinon le pipeline se termine avec succes.

### e. Interface en ligne de commande

La fonction `main()` permet d'executer le programme depuis le terminal avec des options :

- `--source` : dossier des logs
- `--niveau` : filtre de niveau (`ERROR`, `WARN`, `INFO`, `ALL`)
- `--rapports` : dossier de sortie des rapports JSON
- `--backups` : dossier de sortie des archives
- `--retention` : nombre de jours de conservation des rapports

Si on ne precise rien, le programme utilise par defaut :

- `logs_test/`
- `rapports/`
- `backups/`

## 3. Ce que j'ai ajoute ou corrige

Pour que le module d'orchestration fonctionne vraiment, j'ai fait les points suivants :

### a. Ecriture complete de `main.py`

J'ai implemente :

- le chargement des modules ;
- l'enchainement des etapes ;
- la gestion des erreurs ;
- l'interface CLI ;
- les messages de suivi ;
- le code de retour final (`0` si succes, `1` si erreur).

### b. Fallback pour `rapport.py`

Comme `rapport.py` est vide dans le depot actuel, j'ai ajoute une solution de secours dans `main.py` pour ecrire le JSON automatiquement.

Sans cela, ton orchestrateur ne pouvait pas terminer toute la chaine.

### c. Alignement des autres modules utiles

J'ai remis localement le contenu fonctionnel de :

- `analyser.py`
- `archiver.py`
- `logs_test/app1.log`
- `logs_test/app2.log`
- `logs_test/app3.log`

Cela permet de tester ton module avec une vraie execution.

### d. Correction de `archiver.py` pour Windows

Le module d'archivage utilisait `df`, une commande typique Linux/macOS.

Sur Windows, cela provoquait un avertissement.

J'ai remplace cette verification par `shutil.disk_usage(...)`, qui fonctionne correctement sous Windows.

## 4. Comment l'orchestrateur verifie chaque etape

Voici la logique de verification.

### Etape 1 : verifier le dossier source

Avant de lancer le pipeline, `main.py` verifie que le dossier source existe.

Si le dossier n'existe pas :

- message `[ERREUR] Dossier source introuvable`
- sortie avec `sys.exit(1)`

### Etape 2 : verifier que le module d'analyse fonctionne

`main.py` appelle `analyser_logs(source, niveau)`.

Si une exception se produit :

- message `[ERREUR] Echec du module d'analyse`
- le pipeline s'arrete

### Etape 3 : verifier la generation du rapport

`main.py` tente d'utiliser `rapport.py`.

Si le module n'est pas pret :

- fallback JSON interne

Si une vraie erreur se produit :

- message `[ERREUR] Echec de la generation du rapport`
- le pipeline s'arrete

### Etape 4 : verifier qu'il y a bien des logs a archiver

Avant l'archivage, `main.py` cherche les fichiers `.log`.

S'il n'y en a pas :

- message `[ERREUR] Aucun fichier .log trouve a archiver`
- arret du pipeline

### Etape 5 : verifier l'archivage et le nettoyage

`main.py` appelle :

- `archiver_logs(...)`
- `nettoyer_anciens_rapports(...)`

Si une erreur apparait :

- message `[ERREUR] Echec du module d'archivage`
- arret du pipeline

### Etape 6 : succes final

Si tout se passe bien :

- message `[SUCCES] Pipeline termine`
- affichage du chemin du rapport
- affichage du chemin de l'archive

## 5. Comment tester ma partie

### Test simple

Commande :

```bash
python main.py
```

Ce test verifie :

- la lecture des logs ;
- la creation d'un rapport JSON ;
- la creation d'une archive `.tar.gz` ;
- le nettoyage des anciens rapports.

### Test avec filtre de niveau

```bash
python main.py --niveau ERROR
```

Ici, l'analyse ne garde que les lignes `ERROR`.

### Test avec chemins explicites

```bash
python main.py --source logs_test --rapports rapports --backups backups --retention 30
```

## 6. Resultat obtenu apres execution

Lors du test, le programme a bien :

- analyse les logs ;
- genere un rapport JSON dans `rapports/` ;
- cree une archive dans `backups/` ;
- termine sans erreur.

Exemple de sortie :

```text
[INFO] Source des logs : ...
[INFO] Niveau de filtre : ALL
[OK] Analyse des logs terminee.
[AVERTISSEMENT] rapport.py est incomplet, fallback JSON interne utilise.
[OK] Rapport JSON genere : ...\rapports\rapport_YYYYMMDD_HHMMSS.json
[INFO] Espace disque disponible : ...
[OK] Archive deplacee vers : ...\backups\backup_YYYY-MM-DD.tar.gz
[SUCCES] Pipeline termine.
```

## 7. Ce que je peux expliquer a l'oral

Si on te demande ce que tu as fait, tu peux dire :

> J'ai developpe le module d'orchestration dans `main.py`. Mon role etait de coordonner les autres modules du projet. J'ai mis en place l'enchainement complet analyse -> rapport -> archivage -> nettoyage, avec des verifications a chaque etape, des messages clairs, et un arret propre en cas d'erreur. J'ai aussi ajoute une solution de secours pour la generation du JSON afin que le pipeline reste executable meme si le module de rapport n'etait pas encore finalise.

## 8. Procedure Git pour ma branche

Quand on sera pret a versionner ta partie, on pourra faire :

```bash
git checkout -b feature/main-orchestration
git add main.py analyser.py archiver.py logs_test/app1.log logs_test/app2.log logs_test/app3.log README_Jeffry_Module4.md
git commit -m "Implement module 4 orchestration pipeline"
git push -u origin feature/main-orchestration
```

## 9. Fichiers lies a ma partie

- `main.py` : orchestration
- `analyser.py` : module appele pour l'analyse
- `rapport.py` : module de rapport attendu par l'orchestrateur
- `archiver.py` : module appele pour l'archivage
- `logs_test/` : donnees de test
- `README_Jeffry_Module4.md` : explication detaillee de ma partie

