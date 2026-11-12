"""Détection et comptage des modes de transport dans les images Mapillary."""

import argparse
import csv
from pathlib import Path

from ultralytics import YOLO

# Correspondance classes COCO (YOLO) -> catégories du projet
CATEGORIES = {
    "person": "pietons",
    "bicycle": "velos",
    "motorcycle": "motos",
    "car": "voitures",
    "bus": "bus",
    "truck": "camions",
}


def main():
    parser = argparse.ArgumentParser(description="Détection YOLO sur les images Mapillary")
    parser.add_argument("-i", "--images", default="output", help="Dossier des images JPG")
    parser.add_argument("-o", "--sortie", default="resultats/detections.csv", help="Fichier CSV")
    parser.add_argument("--limite", type=int, default=20, help="Nombre maximal d'images à analyser")
    parser.add_argument("--annotees", default="resultats/annotees", help="Dossier des images annotées")
    args = parser.parse_args()

    dossier = Path(args.images)
    if not dossier.is_dir():
        parser.error(f"Dossier introuvable : {dossier}")
    if args.limite < 1:
        parser.error("--limite doit être supérieur à zéro")

    images = sorted(p for p in dossier.rglob("*") if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"})[:args.limite]
    if not images:
        parser.error(f"Aucune image JPG/PNG trouvée dans : {dossier}")

    sortie = Path(args.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    dossier_annotees = Path(args.annotees)
    dossier_annotees.mkdir(parents=True, exist_ok=True)

    modele = YOLO("yolo11n.pt")
    classes_utiles = [numero for numero, nom in modele.names.items() if nom in CATEGORIES]

    with sortie.open("w", newline="", encoding="utf-8") as fichier:
        colonnes = ["image", *CATEGORIES.values()]
        writer = csv.DictWriter(fichier, fieldnames=colonnes)
        writer.writeheader()

        for numero, image in enumerate(images, 1):
            resultat = modele.predict(str(image), conf=0.5, classes=classes_utiles, verbose=False)[0]
            comptage = {categorie: 0 for categorie in CATEGORIES.values()}

            if resultat.boxes is not None:
                for classe in resultat.boxes.cls:
                    nom = resultat.names[int(classe)]
                    comptage[CATEGORIES[nom]] += 1

            writer.writerow({"image": str(image.relative_to(dossier)), **comptage})
            # On conserve les sous-dossiers éventuels pour éviter les collisions de noms.
            chemin_annote = dossier_annotees / image.relative_to(dossier)
            chemin_annote.parent.mkdir(parents=True, exist_ok=True)
            resultat.save(filename=str(chemin_annote))
            print(f"{numero}/{len(images)} : {image.name} -> {comptage}")

    print(f"Terminé : {len(images)} images analysées, CSV : {sortie}")


if __name__ == "__main__":
    main()
