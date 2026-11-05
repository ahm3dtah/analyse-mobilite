# Analyse des modalités de mobilité

Projet d'imagerie numérique (Polytech, 2026-2027).

## Objectif
Télécharger automatiquement les images Mapillary dans un rayon d'environ 200 m autour de coordonnées GPS, sélectionner les scènes de circulation, détecter les piétons, vélos, motos, voitures, bus et camions, puis exporter des résultats CSV et des graphiques comparatifs.

## Structure
- `src/collecte.py` : téléchargement Mapillary (à développer)
- `src/filtrage.py` : tri des images et doublons (à développer)
- `src/detection.py` : YOLO (à développer)
- `src/statistiques.py` : CSV et graphiques (à développer)
- `src/main.py` : interface CLI préparée (pipeline non implémenté)
- `config/zones.csv` : zones à définir et vérifier.

## Installation
```bash
python -m venv .venv
# Windows PowerShell : .venv\Scripts\Activate.ps1
# Linux / macOS : source .venv/bin/activate
pip install -r requirements.txt
python -m src.main -h
```

## Commande prévue (pas encore opérationnelle)
```bash
python -m src.main -lat 49.49 -lon 0.12 -o resultats/le_havre.csv
```
Attention : coordonnées illustratives, à valider. Ce squelette ne télécharge ni n'analyse encore les images.

## Travail d'équipe
Créer une branche `feature/...` par tâche et fusionner par pull request. Ne pas publier les jetons API ni les données d'images volumineuses. Contrôler les biais (doublons, véhicules stationnés, dates et couverture des images).

Livrables : code commenté, rapports CSV, graphiques et présentation en français. Citer les sources et déclarer l'usage de l'IA générative.
