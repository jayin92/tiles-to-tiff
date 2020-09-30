import math
import urllib.request
import os
import glob
import subprocess
import shutil

from fp.fp import FreeProxy
from tile_convert import bbox_to_xyz, tile_edges
from osgeo import gdal

#---------- CONFIGURATION -----------#
tile_server = "https://mt0.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
output_dir = os.path.join(os.path.dirname(__file__), 'output')
zoom = 5

lon_min = 121
lat_min = 23
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
    path = '{}/{}_{}_{}.png'.format(temp_dir, x, y, z)
    
    urllib.request.urlretrieve(url, path)
    # try:
    # except:
    #     print("getting proxy")
    #     pro = {"http": FreeProxy(rand=True).get()}
    #     proxy = urllib.request.ProxyHandler(pro)
    #     opener = urllib.request.build_opener(proxy)
    #     urllib.request.install_opener(opener)
    #     return download_tile(x, y, z, tile_server)
    return(path)


def merge_tiles(input_pattern, output_path):
    merge_command = ['gdal_merge.py', '-o', output_path]

    for name in glob.glob(input_pattern):
        merge_command.append(name)

    subprocess.call(merge_command)


def georeference_raster_tile(x, y, z, path):
    bounds = tile_edges(x, y, z)
    filename, extension = os.path.splitext(path)
    print(bounds)
    gdal.Translate(filename + '.tif',
                   path,
                   outputSRS='EPSG:4326',
                   outputBounds=bounds)



x_min, x_max, y_min, y_max = bbox_to_xyz(
    lon_min, lon_max, lat_min, lat_max, zoom)

print("Downloading {} tiles".format((x_max - x_min + 1) * (y_max - y_min + 1)))

for x in range(x_min, x_max + 1):
    for y in range(y_min, y_max + 1):
        print("{},{}".format(x, y))
        png_path = download_tile(x, y, zoom, tile_server)
        georeference_raster_tile(x, y, zoom, png_path)

print("Download complete")

print("Merging tiles")
merge_tiles(temp_dir + '/*.tif', output_dir + '/N{}E{}_{}.tif'.format(lat_min, lon_min, zoom))
print("Merge complete")

shutil.rmtree(temp_dir)
os.makedirs(temp_dir)
