#!/bin/bash

# --- Muestra la versión de Python ---
python3 -V

# --- Elimina el fichero de salida si ya existe ---
if [ -f salida_ML.txt ]; then
	rm salida_ML.txt
fi

# --- Distribuciones ---
# KNeighborsClassifier
# Usamos un for con los valores concretos que queremos que pruebe
for neigh in 10 30 50
do
	python3 ap1_codigo_python.py KNeighborsClassifier --neigh $neigh >> salida_ML.txt
done
# GaussianNB
python3 ap1_codigo_python.py GaussianNB >> salida_ML.txt
# RandomForestClassifier
python3 ap1_codigo_python.py RandomForestClassifier >> salida_ML.txt

# --- Lectura del fichero e impresión de las líneas con "Accuracy" ---
c=1
while read -r linea
do
    if [[ $linea == *"Accuracy"* ]]; then
        echo "$linea"
    fi
done < salida_ML.txt 
