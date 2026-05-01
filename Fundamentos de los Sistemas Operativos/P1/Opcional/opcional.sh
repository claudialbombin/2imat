#!/bin/bash
# Script opcional.sh
# Ejecuta cálculos en bash y en Python

echo "=== Resultados con comandos bash ==="

# Número de regiones distintas (columna 1)
echo -n "Regiones distintas: "
tail -n +2 100K_Sales_Records.csv | awk -F',' '{print $1}' | sort | uniq | wc -l

# Número de países distintos (columna 2)
echo -n "Países distintos: "
tail -n +2 100K_Sales_Records.csv | awk -F',' '{print $2}' | sort | uniq | wc -l

# Número de productos distintos (columna 3)
echo -n "Productos distintos: "
tail -n +2 100K_Sales_Records.csv | awk -F',' '{print $3}' | sort | uniq | wc -l

echo ""
echo "=== Ejecutando el script Python ==="
time python3 contar.py
