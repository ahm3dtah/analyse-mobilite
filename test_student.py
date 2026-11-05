import mercantile, mapbox_vector_tile, requests, json, os
from vt2geojson.tools import vt_bytes_to_geojson
from geopy import geocoders
import pdb
import tqdm 
    
# define an empty geojson as output
output= { "type": "FeatureCollection", "features": [] }

# vector tile endpoints -- change this in the API request to reference the correct endpoint
tile_coverage = 'mly1_public'

# tile layer depends which vector tile endpoints: 
# 1. if map features or traffic signs, it will be "point" always
# 2. if looking for coverage, it will be "image" for points, "sequence" for lines, or "overview" for far zoom
tile_layer = "image"

# Mapillary access token -- user should provide their own
access_token = 'MLY|XXXXX'

# a bounding box in [east_lng,_south_lat,west_lng,north_lat] format
# Get lat and long from a city  openstreetmap

#latlon = [45.7772, 3.0870] # centre de Clermont
latlon = [45.800413, 3.108813] # Carrefour des pistes
#0.01 => 1km env
d = 0.003 
west, south, east, north = [latlon[1]-d,latlon[0]-d,latlon[1]+d,latlon[0]+d]

# get the list of tiles with x and y coordinates which intersect our bounding box
# MUST be at zoom level 14 where the data is available, other zooms currently not supported
tiles = list(mercantile.tiles(west, south, east, north, 14))

# loop through list of tiles to get tile z/x/y to plug in to Mapillary endpoints and make request
# using tdqm
for tile in tqdm.tqdm(tiles):
    tile_url = 'https://tiles.mapillary.com/maps/vtp/{}/2/{}/{}/{}?access_token={}'.format(tile_coverage,tile.z,tile.x,tile.y,access_token)
    response = requests.get(tile_url)
    data = vt_bytes_to_geojson(response.content, tile.x, tile.y, tile.z,layer=tile_layer)

    # push to output geojson object if yes
    for feature in data['features']:
        
        # get lng,lat of each feature
        lng = feature['geometry']['coordinates'][0]
        lat = feature['geometry']['coordinates'][1]
        
        # ensure feature falls inside bounding box since tiles can extend beyond
        if lng > west and lng < east and lat > south and lat < north:

            # create a folder for each unique sequence ID to group images by sequence
            sequence_id = feature['properties']['sequence_id']
            if not os.path.exists(sequence_id):
                os.makedirs(sequence_id)

            # request the URL of each image
            image_id = feature['properties']['id']
            header = {'Authorization' : 'OAuth {}'.format(access_token)}
            url = 'https://graph.mapillary.com/{}?fields=thumb_2048_url'.format(image_id)
            r = requests.get(url, headers=header)
            data = r.json()
            image_url = data['thumb_2048_url']

            # save each image with ID as filename to directory by sequence ID
            with open('{}/{}.jpg'.format(sequence_id, image_id), 'wb') as handler:
                image_data = requests.get(image_url, stream=True).content
                handler.write(image_data)

# List of image files in the directory and subdirectories and move them to an output folder
import os
import shutil
import glob

# List all files in directory and subdirectories

# Create output folder if not exists
if not os.path.exists('output'):
    os.makedirs('output')
# Remove all files in output folder
for file in os.listdir('output'):
    os.remove('output/' + file)
files = glob.glob('**/*.jpg', recursive=True)
# Move all files to output folder
for file in files:
    shutil.move(file, 'output')
#  remove empty directories exept output
for dir in os.listdir():
    if os.path.isdir(dir) and dir != 'output':
        try:
            os.rmdir(dir)
        except:
            pass



            
