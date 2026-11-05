# Répartition des tâches (proposition)

1. **Collecte Mapillary** : points GPS, API, images et métadonnées (`src/collecte.py`).
2. **Filtrage** : scènes routières, doublons, véhicules stationnés (`src/filtrage.py`).
3. **Détection YOLO** : identification et comptage par catégorie (`src/detection.py`).
4. **Statistiques** : export CSV, agrégations, figures (`src/statistiques.py`).

**Premier jalon :** pipeline de bout en bout sur 30–50 images d'une seule zone. Une branche par tâche, revue par pull request, jamais de token API dans le dépôt.
