#!/bin/bash

# Crear entorno virtual con Python 3.12
echo "Creando entorno virtual con Python 3.12..."
python3.12 -m venv venv_312

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv_312/bin/activate

# Instalar dependencias para plot_color_quantization.py
echo "Instalando dependencias desde requirements4_1.txt..."
pip install -r requirements4_1.txt

# Ejecutar plot_color_quantization.py y redirigir salida
echo "Ejecutando plot_color_quantization.py..."
python plot_color_quantization.py > logColor.txt 2>&1

echo "Resultado guardado en logColor.txt"

# Desactivar entorno virtual
echo "Desactivando entorno virtual..."
deactivate

# Crear entorno virtual con Python 3.11
echo "Creando entorno virtual con Python 3.11..."
python3.11 -m venv venv_311

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv_311/bin/activate

# Instalar dependencias para plot_face_recognition.py
echo "Instalando dependencias desde requirements4_2.txt..."
pip install -r requirements4_2.txt

# Ejecutar plot_face_recognition.py
echo "Ejecutando plot_face_recognition.py..."
python plot_face_recognition.py

echo "Procesamiento de caras completado. Resultados guardados en faces.png"

# Desactivar entorno virtual
echo "Desactivando entorno virtual..."
deactivate

# Eliminar entornos virtuales
echo "Eliminando entorno virtual de Python 3.12..."
rm -rf venv_312

echo "Eliminando entorno virtual de Python 3.11..."
rm -rf venv_311

echo "Proceso completado"

