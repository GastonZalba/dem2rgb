# demign
Código para procesar Modelo de Elevación del IGN:
- Convierte archivos a tif desde img
- Agrega render piramidal/overviews para mejorar performance en geoserver

## Requerimientos
- Python > 3
- numpy
- GDAL

## Uso
- Poner dentro de carpeta `input` los archivos img descargados desde la página del IGN
- Ejecutar desde consola `python process.py`
- En la carpeta configurada como `output` estarán los archivos procesados

## @TODO
- Agregar módulo rasterio para convertir los MDE a formato rgb Terrarium