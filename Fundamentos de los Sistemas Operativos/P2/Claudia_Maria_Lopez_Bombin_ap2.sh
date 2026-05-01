#!/bin/bash

# Variables
DOWNLOAD_PATH="https://archive.ics.uci.edu/ml/machine-learning-databases/wine/wine.data"
HEADER="class,alcohol,malic_acid,ash,alcalinity_of_ash,magnesium,total_phenols,flavanoids,nonflavanoid_phenols,proanthocyanins,color_intensity,hue,od280/od315_of_diluted_wines,proline"
DATA_FILE="wine.data"
CSV_FILE="wine_headers.csv"

# Descarga de la web con checkeo de si ya existe
if [ -f $DATA_FILE ]; then
	echo El archivo $DATA_FILE ya existe. Omitiendo descarga.
else
	curl $DOWNLOAD_PATH > $DATA_FILE
fi

# Creacion del CSV con cabeceras
if [ -f $CSV_FILE ]; then
	echo El archivo $CSV_FILE ya existe. Omitiendo creacion de CSV con cabeceras.
else
	# Hacemos un echo de fuerza bruta para crear el archivo y meter la cabecera
	echo $HEADER > $CSV_FILE
	# Hacemos un while y vamos a ir leyendo linea a linea el archivo descargado
	# Cada linea que leamos, la vamos aniadiendo al csv
	c=1
	while read -r linea
	do
		echo $linea >> $CSV_FILE
	done < $DATA_FILE
fi

# Entrenamos el modelo
for porcentaje1 in 50 60 70 80 90
do
	porcentaje2=$((100-porcentaje1))
	echo Ejecutando el script de Python con $porcentaje1% entrenamiento y $porcentaje2% de test.
	python3 ap2_codigo_python.py wine_headers.csv $porcentaje1
done
