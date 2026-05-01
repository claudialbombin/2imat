#!/bin/bash

# Verificar si Python 3.12 está disponible
if ! command -v python3.12 &> /dev/null; then
    echo "ERROR: Python 3.12 no está instalado en el sistema"
    echo "Por favor, instala Python 3.12 primero"
    exit 1
fi

# 1. Crear entorno virtual con Python 3.12
python3.12 -m venv env_icai

# 2. Activar el entorno virtual
source env_icai/bin/activate

# 3. Actualizar pip primero
pip install --upgrade pip

# 4. Instalar librerías con pip
pip install seaborn plotly streamlit pandas matplotlib numpy jupyter

# 5. Instalar el kernel de Jupyter
python -m ipykernel install --user --name env_icai --display-name "Python 3.12 Icai"

# 6. Abrir vscode
code .

echo "=========================================="
echo "Entorno virtual creado y configurado exitosamente!"
echo "Python version: $(python --version)"
echo "=========================================="
echo "Para activar el entorno en el futuro ejecuta:"
echo "source env_icai/bin/activate"
echo "=========================================="
