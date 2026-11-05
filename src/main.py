"""Interface CLI (squelette non opérationnel)."""
import argparse

def main():
    parser = argparse.ArgumentParser(description="Analyse de la mobilité à partir d'images Mapillary")
    parser.add_argument('-lat', type=float, required=True, help='Latitude GPS')
    parser.add_argument('-lon', type=float, required=True, help='Longitude GPS')
    parser.add_argument('-o', default='resultats/rapport.csv', help='Nom du CSV')
    args = parser.parse_args()
    if not (-90 <= args.lat <= 90 and -180 <= args.lon <= 180):
        parser.error('Coordonnées invalides')
    parser.exit(2, 'Pipeline non implémenté : commencer par src/collecte.py.\n')

if __name__ == '__main__':
    main()
