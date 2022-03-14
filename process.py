
import sys
import os
import numpy as np

try:
    from osgeo import gdal
except:
    sys.exit('ERROR: osgeo module was not found')

INPUT_PATH = 'input'
OUTPUT_PATH = 'output'

overviews = [2, 4, 8, 16, 32, 64, 128, 256]
        
if not os.path.exists(INPUT_PATH):
    sys.exit(f'ERROR: No se encuentra la carpeta {INPUT_PATH}')

if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)
    print(f'Creada carpeta {OUTPUT_PATH}')

for subdir, dirs, files in os.walk(INPUT_PATH):

    for file in files:
        filepath = subdir + os.sep + file

        if file.endswith(".img"):

            print('File:', file)

            file_ds = gdal.Open(filepath, gdal.GA_ReadOnly)

            band = file_ds.GetRasterBand(1)
            noDataValue = band.GetNoDataValue() 

            array = band.ReadAsArray()

            fileWithoutExtension = os.path.splitext(file)[0]

            OUTPUT = f'{OUTPUT_PATH}\{fileWithoutExtension}.tif'

            kwargs = {
                'format': 'GTiff',
                'multithread': True
            }

            ds = gdal.Warp(OUTPUT, file_ds, **kwargs)

            ds.BuildOverviews("AVERAGE", overviews)

            ds = None


