#!/bin/bash

# Nombre del archivo de datos y URL
DATA_FILE="ml-1m.zip"
DATA_URL="http://files.grouplens.org/datasets/movielens/ml-1m.zip"
EXTRACTED_DIR="ml-1m"
RATINGS_FILE="${EXTRACTED_DIR}/ratings.dat"

# --- 1. Descargar el fichero zip si no existe ---
if [ ! -f "$DATA_FILE" ]; then
    echo "Descargando $DATA_FILE ..."
    curl -L "$DATA_URL" -o "$DATA_FILE"
else
    echo "$DATA_FILE ya existe, no se descarga."
fi

# --- 2. Descomprimir si no existe el directorio ---
if [ ! -d "$EXTRACTED_DIR" ]; then
    echo "Descomprimiendo $DATA_FILE ..."
    unzip "$DATA_FILE"
else
    echo "$EXTRACTED_DIR ya existe, no se descomprime."
fi

# --- 3. Crear directorios pedidos ---
mkdir -p headers descriptions filters selections

# --- 4. Llamadas al código Python ---

# 4.1 show_head con tamaños 100, 200 y 300 usando bucle
for n in 100 200 300; do
    python3 ap3_codigo_python.py show_head "$RATINGS_FILE" "headers/${n}_lines.csv" "$n"
done

# 4.2 Descripción de datos
python3 ap3_codigo_python.py describe "$RATINGS_FILE" descriptions/ratings_description.csv

# 4.3 Filtrar ratings con valores 1 y 5
for valor in 1 5; do
    python3 ap3_codigo_python.py filter "$RATINGS_FILE" "filters/m1_filter${valor}.csv" Rating "$valor"
done

# 4.4 Selecciones con 10%, 20% y 30%
for porcentaje in 10 20 30; do
    python3 ap3_codigo_python.py select_percentage "$RATINGS_FILE" "selections/m1_selection${porcentaje}.csv" "$porcentaje"
done

# --- 5. Esperar 5 segundos ---
echo "Esperando 5 segundos antes de eliminar directorios..."
sleep 5

# --- 6. Eliminar los 4 directorios creados ---
rm -rf headers descriptions filters selections
echo "Directorios eliminados correctamente."

