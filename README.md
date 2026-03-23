# Module 3 — Archivage et Nettoyage (`archiver.py`)

## Description

Le Module 3 est responsable de l'archivage des fichiers logs traités et du
nettoyage automatique des anciens rapports JSON.

Il effectue les 4 actions suivantes dans l'ordre :

1. **Vérifie l'espace disque** disponible sur la machine avant de commencer
2. **Archive** tous les fichiers `.log` du dossier source dans une archive
   compressée nommée `backup_YYYY-MM-DD.tar.gz`
3. **Déplace** l'archive vers le dossier de destination choisi
4. **Supprime** les rapports JSON dont l'âge dépasse la durée de rétention fixée

---

## Lancer le module

### Commande de base

```bash
python archiver.py --source ./logs_test --dest ./archives
```

### Commande complète (avec nettoyage des rapports)

```bash
python archiver.py --source ./logs_test --dest ./archives --rapports ./rapports --retention 30
```

### Arguments

| Argument      | Obligatoire | Description                                      | Défaut |
|---------------|-------------|--------------------------------------------------|--------|
| `--source`    | ✅ Oui      | Dossier contenant les fichiers `.log` à archiver | —      |
| `--dest`      | ✅ Oui      | Dossier de destination pour l'archive `.tar.gz`  | —      |
| `--rapports`  | ❌ Non      | Dossier des rapports JSON à nettoyer             | None   |
| `--retention` | ❌ Non      | Durée de rétention des rapports en jours         | 30     |