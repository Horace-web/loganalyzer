# LogAnalyzer

## Description

LogAnalyzer est un outil Python d'analyse automatisée de fichiers logs.
Il lit les fichiers `.log`, calcule des statistiques par niveau (ERROR, WARN, INFO),
génère un rapport JSON horodaté, puis archive les logs traités dans une sauvegarde compressée.
L'objectif est d'automatiser entièrement ce processus sans intervention manuelle.

---

## Prérequis

- Python 3.10 ou supérieur
- Aucun module externe requis (uniquement la bibliothèque standard Python)
- Système Linux ou Windows (WSL requis pour la planification Cron sous Windows)

---

## Installation
```bash
git clone https://github.com/Horace-web/loganalyzer
cd loganalyzer
```

---

## Structure du projet
```
loganalyzer/
├── analyser.py       # Module 1 — Lecture et analyse des fichiers logs
├── rapport.py        # Module 2 — Génération du rapport JSON
├── archiver.py       # Module 3 — Archivage et nettoyage
├── main.py           # Module 4 — Orchestration du pipeline
├── logs_test/        # Fichiers .log de test
│   ├── app1.log
│   ├── app2.log
│   └── app3.log
├── rapports/         # Dossier de sortie des rapports JSON (créé automatiquement)
├── backups/          # Dossier de sortie des archives .tar.gz (créé automatiquement)
└── README.md
```

> **Note :** Les dossiers `rapports/` et `backups/` sont créés automatiquement
> au premier lancement du programme.

---

## Utilisation

### Lancement avec les paramètres par défaut
```bash
python main.py
```

### Lancement avec des paramètres personnalisés
```bash
python main.py --source logs_test --niveau ERROR --rapports rapports --backups backups --retention 30
```

| Argument      | Description                                      | Valeur par défaut |
|---------------|--------------------------------------------------|-------------------|
| `--source`    | Dossier contenant les fichiers `.log`            | `./logs_test`     |
| `--niveau`    | Niveau de filtrage : `ERROR`, `WARN`, `INFO`, `ALL` | `ALL`          |
| `--rapports`  | Dossier de sortie des rapports JSON              | `./rapports`      |
| `--backups`   | Dossier de destination des archives              | `./backups`       |
| `--retention` | Durée de rétention des rapports en jours         | `30`              |

---

## Planification automatique (Cron)

La planification via Cron est native sous Linux/macOS.
Sous Windows, il est nécessaire d'utiliser **WSL (Windows Subsystem for Linux)**.

### Mise en place de WSL (Windows uniquement)
```bash
wsl --install -d Ubuntu
```

Une fois WSL installé, lancer l'environnement Linux :
```bash
wsl
```

Puis naviguer vers le dossier du projet (adapter le chemin à votre machine) :
```bash
cd /mnt/c/Users/LENOVO/loganalyzer
```

### Configuration de Cron

Ouvrir l'éditeur Cron (choisir l'éditeur `nano` si demandé) :
```bash
crontab -e
```

#### Test de bon fonctionnement

Pour vérifier que Cron est actif, ajouter temporairement cette ligne :
```
* * * * * echo "cron ok" >> /mnt/c/Users/LENOVO/loganalyzer/test.txt
```

Après quelques minutes, vérifier le fichier généré :
```bash
cat /mnt/c/Users/LENOVO/loganalyzer/test.txt
```

La présence de plusieurs lignes `cron ok` confirme que Cron fonctionne correctement.

#### Ligne Cron finale du projet
```
0 3 * * 0 python3 /mnt/c/Users/LENOVO/loganalyzer/main.py
```

Cette ligne exécute automatiquement le pipeline **tous les dimanches à 03h00**.

> **Note Windows :** Le module `archiver.py` utilise `/tmp` comme dossier temporaire
> pour créer les archives. Sous Windows avec WSL, il faut s'assurer que ce dossier
> existe ou créer un dossier `tmp` à la racine de votre lecteur `C:\`.

---

## Répartition des tâches

| Membre     | Module                        | Fichier        | Responsabilités principales |
|------------|-------------------------------|----------------|-----------------------------|
| **ODOUNLAMI Horace** | Module 1 — Analyse des logs   | `analyser.py`  | Mise en place du dépôt Git et de la structure du projet, définition des contrats de données entre modules, génération des fichiers de logs de test, configuration d'`argparse` (`--source`, `--niveau`), lecture des `.log` avec `glob`, extraction via expressions régulières (`re`), calcul des statistiques (comptage par niveau, top 5 erreurs), récupération des infos système (`os`, `platform`), retour d'un dictionnaire structuré vers `rapport.py` |
| **DOHOU Ercias Audrey** | Module 2 — Génération JSON    | `rapport.py`   | Transformation du dictionnaire d'analyse en fichier JSON structuré et horodaté, gestion des chemins absolus via `__file__` |
| **SOGOE Bryan**  | Module 3 — Archivage          | `archiver.py`  | Compression des logs avec `tarfile`, déplacement de l'archive avec `shutil`, politique de rétention avec `os.path.getmtime`, vérification d'espace disque via `subprocess` |
| **HOUNDETON Jeffry** | Module 4 — Orchestration      | `main.py`      | Chargement dynamique des modules, enchaînement du pipeline, gestion des erreurs avec `try/except`, codes de retour `sys.exit` |
| **TOBOSSI Junior** | QA, Tests et Documentation    | `README.md`    | Génération des fichiers de logs de test, rédaction de la documentation, mise en place et validation de la planification Cron, relecture des docstrings |
