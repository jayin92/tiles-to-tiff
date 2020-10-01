import math
import urllib.request
import os
import glob
import subprocess
import shutil
import requests
from tqdm import tqdm

from fp.fp import FreeProxy
from tile_convert import bbox_to_xyz, tile_edges
from osgeo import gdal

#---------- CONFIGURATION -----------#
# tile_server = "https://mt0.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
tile_server = "https://api.maptiler.com/tiles/satellite/{z}/{x}/{y}.jpg?key=AIf4cL2Jkh4Vlf3AylHN"
temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
output_dir = os.path.join(os.path.dirname(__file__), 'output/')
zoom = 13

lat_min = 27
lon_min = 98
lon_max = lon_min + 1
lat_max = lat_min + 1
# lon_max = 122
# lat_max = 25
#-----------------------------------#




def download_tile(x, y, z, tile_server):
    url = tile_server.replace(
        "{x}", str(x)).replace(
        "{y}", str(y)).replace(
        "{z}", str(z))
    path = '{}/{}_{}_{}.jpg'.format(temp_dir, x, y, z)
    if(os.path.isfile(path)):
        return path
    # print("getting proxy")
    # proxies = {"http": FreeProxy(rand=True).get()}
    # proxy = urllib.request.ProxyHandler(pro)
    # opener = urllib.request.build_opener(proxy)
    # urllib.request.install_opener(opener)
    # print(proxies)
    # r = requests.get(url)
    # print(path)
    # print(r.content)
    # with open(path, 'wb') as f:
        # f.write(r.content)
    urllib.request.urlretrieve(url, path)
    return(path)


def merge_tiles(input_pattern, output_path):
    merge_command = ['gdal_merge.py', '-o', output_path]

    for name in glob.glob(input_pattern):
        merge_command.append(name)

    subprocess.call(merge_command)


def georeference_raster_tile(x, y, z, path):
    bounds = tile_edges(x, y, z)
    filename, extension = os.path.splitext(path)
    gdal.Translate(filename + '.tif',
                   path,
                   outputSRS='EPSG:4326',
                   outputBounds=bounds)

def crop(input, output, lat, lon):
    gdal.Translate(
        output,
        input,
        outputSRS='EPSG:4326',
        projWin=[lon, lat+1, lon+1, lat]
    )


ran = [
    (26, 101),
    (26, 100),
    (26, 99),
    (26, 98),
    (29, 101),
    (29, 100),
    (29, 99),
    (28, 101),
    (28, 100),
    (28, 99),
    (28, 98),
    (27, 101),
    (27, 100)
]


for lat_min, lon_min in ran:
    print(lat_min, lon_min)
    lat_max = lat_min + 1
    lon_max = lon_min + 1
    x_min, x_max, y_min, y_max = bbox_to_xyz(
        lon_min, lon_max, lat_min, lat_max, zoom)

    print("Downloading {} tiles".format((x_max - x_min + 1) * (y_max - y_min + 1)))

    pbar = tqdm(total=(x_max - x_min + 1) * (y_max - y_min + 1))
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            # print("{},{}".format(x, y))
            pbar.update(1)
            pbar.set_description("{},{}".format(x, y))
            png_path = download_tile(x, y, zoom, tile_server)
            georeference_raster_tile(x, y, zoom, png_path)

    pbar.close()
    print("Download complete")

    print("Merging tiles")
    merge_tiles(temp_dir + '/*.tif', output_dir + '/N{}E{}_{}.tif'.format(lat_min, lon_min, zoom))
    print("Merge complete")

    print("Croping")
    crop(
        output_dir + '/N{}E{}_{}.tif'.format(lat_min, lon_min, zoom), 
        output_dir + 'China/N{}E{}_{}_final_sat.tif'.format(lat_min, lon_min, zoom), 
        lat_min, 
        lon_min
        )
    print("Crop complete")


    shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
