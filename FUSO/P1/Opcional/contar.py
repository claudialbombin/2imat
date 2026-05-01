import csv
import time

start = time.time()

regiones = set()
paises = set()
productos = set()
total_lineas = 0

with open("5m_Sales_Records.csv", newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        regiones.add(row["Region"])
        paises.add(row["Country"])
        productos.add(row["Item Type"])
        total_lineas += 1

print("=== Resultados con Python ===")
print(f"Regiones distintas: {len(regiones)}")
print(f"Países distintos: {len(paises)}")
print(f"Productos distintos: {len(productos)}")
print(f"Número total de líneas (sin cabecera): {total_lineas}")

end = time.time()
print(f"Tiempo de ejecución Python: {end - start:.4f} segundos")

