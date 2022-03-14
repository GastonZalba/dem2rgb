
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
    
def CreateGeoTiff(outRaster, arr, ds):
    driver = gdal.GetDriverByName('GTiff')
    [rows,cols] = arr.shape
    out_ds = driver.Create(outRaster, cols, rows, 1, gdal.GDT_Float32)
    out_band = out_ds.GetRasterBand(1)
    out_band.WriteArray(arr)
    out_ds.SetGeoTransform(ds.GetGeoTransform())
    out_ds.SetProjection(ds.GetProjection())

    # Pyramidal render / overviews
    out_ds.BuildOverviews("AVERAGE", overviews)

    out_band.FlushCache()
    del out_band
    out_ds = None
    del ds
    
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

            print('NoData value:', noDataValue)

            array = band.ReadAsArray()

            print('Original shape:', array.shape)

            masked = np.ma.masked_equal(array, noDataValue, True)

            # remove empty/masked values
            a = [m.compressed() for m in masked]

            # remove empty arrays
            a = [x for x in a if not x.size == 0]

            a = np.array(a)

            print('Cleaned shape:', a.shape)

            fileWithoutExtension = os.path.splitext(file)[0]

            OUTPUT = f'{OUTPUT_PATH}\{fileWithoutExtension}.tif'

            CreateGeoTiff(OUTPUT, a, file_ds)


