# hard-log

Petit logger console basé sur Rich, avec archivage automatique dans un fichier texte.

## Fonctionnalités

- Affichage coloré par niveau (`BOOT`, `INFO`, `DEBUG`, `WARN`, `ERROR`, `SUCCESS`).
- Formatage horodaté en une ligne.
- Archivage automatique dans `logs/log.txt`.

## Installation

Avec Poetry :

1. Installer les dépendances :
   
	```bash
	poetry install
	```

## Utilisation

Exemple minimal :

```python
from hard_log.soft_log import SoftLog

log = SoftLog()
log.log("BOOT", "Initialisation...")
log.log("INFO", "Scan en cours")
log.log("WARN", "Réponse lente")
log.log("ERROR", "Échec")
log.log("SUCCESS", "Terminé")
```

## Sortie

Les messages s’affichent en couleur dans le terminal et sont archivés dans :

- [logs/log.txt](logs/log.txt)

## Configuration

Le constructeur accepte un dossier et un nom de fichier :

```python
log = SoftLog(path="logs/", file_name="log.txt")
```

## Licence

MIT License
Copyright (c) 2026 Sebastien TADIELLO
