from osgeo import gdal



path = "output/N24E121_13.tif"



gdal.Translate("output/N24E121_final.tif",
               "output/N24E121.tif", 
                outputSRS='EPSG:4326',
                outputBounds=[121, 25, 122, 24])