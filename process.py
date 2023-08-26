
import os
import sys
import argparse
import numpy as np

import rasterio
from rasterio.warp import Resampling

def getExtension(filename):
    return os.path.splitext(filename)[1]

input_folder = 'input'
output_folder = 'output'
add_overviews = True
format = 'grayscale'
extensions = ['.tif', '.tiff', '.vrt', '.img']

overviews = [2, 4, 8, 16, 32, 64, 128, 256]
tfw = 'YES'

parser = argparse.ArgumentParser(description='Script to procces DEM/DTM files to grayscale float, rgb mapbox and rgb terrarium')
parser.add_argument('--input', type=str, metavar='Input folder', default=input_folder,
                    help='Folder path with the grayscale images (default: %(default)s)')
parser.add_argument('--output', type=str, metavar='Output folder', default=output_folder,
                    help='Folder path to save the images (default: %(default)s)')
parser.add_argument('--format', type=str, metavar='Format', default=format,
                    help='Output image format: `grayscale`, `terrarium` and `mapbox` (default: %(default)s)')
parser.add_argument('--overviews', type=bool, metavar='Overviews', default=add_overviews,
                    help='Add overviews to the export (default: %(default)s)')
parser.add_argument('--tfw', type=str, metavar='TFW world file', default=tfw,
                    help='Export TFW file (default: %(default)s)')

args = parser.parse_args()
input_folder = args.input
output_folder = args.output
format = args.format
add_overviews = args.overviews

if not os.path.exists(input_folder):
    sys.exit(f'ERROR: folder {input_folder} has not be found')

output_folder = f'{output_folder}\{format}'

for subdir, dirs, files in os.walk(input_folder):

    for file in files:
        filepath = subdir + os.sep + file

        if (getExtension(file) in extensions):

            with rasterio.open(filepath) as src:
                dem = src.read(1)
                noDataValue = src.nodata
                meta = src.meta

            fileWithoutExtension = os.path.splitext(file)[0]

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                print(f'Created folder {output_folder}')

            out = f'{output_folder}\{fileWithoutExtension}.tif'
            
            print(f'Exporting {out}')
            
            with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True):

                if format == 'grayscale':
                    # one band export
                    meta.update({
                        'driver': 'GTiff',
                        'compress': "deflate",
                        'multithread': True,
                        'tiled': True,
                        'tfw': 'YES'
                    })
                    with rasterio.open(out, 'w', **meta) as dst:
                        dst.write(dem, 1)
                        if add_overviews:
                            dst.build_overviews(
                                [2, 4, 8, 16, 32, 64, 128, 256],
                                Resampling.average
                            )

                else:
                    # three bands export
                    shape = dem.shape
                    r = np.zeros(shape)
                    g = np.zeros(shape)
                    b = np.zeros(shape)

                    meta.update({
                        'driver': 'GTiff',
                        'multithread': True,
                        'tiled': True,
                        'dtype': rasterio.uint8,
                        'nodata': None,
                        'count': 3,
                        'compress': 'deflate',
                        'tfw': tfw
                    })

                    internal_mask = np.asarray(np.where(dem == noDataValue, False, True))

                    if format == 'mapbox':
                        r += np.floor_divide((100000 + dem * 10), 65536)
                        g += np.floor_divide((100000 + dem * 10), 256) - r * 256
                        b += np.floor(100000 + dem * 10) - r * 65536 - g * 256

                    elif format == 'terrarium':
                        dem += 32768
                        r += np.floor_divide(dem, 256)
                        g += np.mod(dem, 256)
                        b += np.floor((dem - np.floor(dem)) * 256)

                    with rasterio.open(out, 'w', **meta) as dst:
                        dst.write_band(1, r.astype(rasterio.uint8))
                        dst.write_band(2, g.astype(rasterio.uint8))
                        dst.write_band(3, b.astype(rasterio.uint8))
                        dst.write_mask(internal_mask)

                        if add_overviews:
                            dst.build_overviews(
                                [2, 4, 8, 16, 32, 64, 128, 256],
                                Resampling.average
                            )
