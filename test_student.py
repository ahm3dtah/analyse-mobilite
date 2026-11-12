import mercantile, mapbox_vector_tile, requests, json, os
from vt2geojson.tools import vt_bytes_to_geojson
from geopy import geocoders
import pdb
import tqdm

# define an empty geojson as output
output = {"type": "FeatureCollection", "features": []}

# vector tile endpoints
tile_coverage = 'mly1_public'

# tile layer
tile_layer = "image"

# Mapillary access token
from dotenv import load_dotenv
load_dotenv()
access_token = os.getenv("MAPILLARY_TOKEN")

# Coordinates
#latlon = [45.7772, 3.0870] # centre de Clermont
latlon = [45.800413, 3.108813] # Carrefour des pistes

d = 0.003
west, south, east, north = [
    latlon[1]-d,
    latlon[0]-d,
    latlon[1]+d,
    latlon[0]+d
]

# Get tiles
tiles = list(mercantile.tiles(west, south, east, north, 14))

# Create output folder and limit downloads
os.makedirs("output", exist_ok=True)
compteur = 0
max_images = 50

# Loop through tiles
for tile in tqdm.tqdm(tiles):

    tile_url = 'https://tiles.mapillary.com/maps/vtp/{}/2/{}/{}/{}?access_token={}'.format(
        tile_coverage, tile.z, tile.x, tile.y, access_token
    )

    response = requests.get(tile_url)

    print("HTTP :", response.status_code)
    print("Type :", response.headers.get("Content-Type"))
    print("Réponse :", repr(response.content[:100]))
    response.raise_for_status()

    data = vt_bytes_to_geojson(
        response.content, tile.x, tile.y, tile.z, layer=tile_layer
    )
    print("Images dans la tuile :", len(data['features']))

    images_zone = [
        f for f in data['features']
        if west < f['geometry']['coordinates'][0] < east
        and south < f['geometry']['coordinates'][1] < north
    ]

    print("Images dans notre zone :", len(images_zone))
    # Loop through images
    for feature in data['features']:

        lng = feature['geometry']['coordinates'][0]
        lat = feature['geometry']['coordinates'][1]

        # Check bounding box
        if lng > west and lng < east and lat > south and lat < north:

            # Get image ID
            image_id = feature['properties']['id']

            header = {'Authorization': 'OAuth {}'.format(access_token)}

            url = 'https://graph.mapillary.com/{}?fields=thumb_2048_url'.format(
                image_id
            )

            r = requests.get(url, headers=header)
            r.raise_for_status()
            data = r.json()

            if 'thumb_2048_url' not in data:
                print("Image ignorée :", image_id, data)
                continue

            image_url = data['thumb_2048_url']

            # Save image
            with open('output/{}.jpg'.format(image_id), 'wb') as handler:
                image_data = requests.get(image_url, stream=True).content
                handler.write(image_data)

            compteur += 1

            # Stop after 200 images
            if compteur >= max_images:
                break

    # Stop tile loop
    if compteur >= max_images:
        break

print("Images téléchargées :", compteur)