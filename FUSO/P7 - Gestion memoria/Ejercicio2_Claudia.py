import sys
import numpy as np
import os
import pandas as pd

# Comprobamos el tamaño que ocupa en el disco el archivo cities.csv
f = 'cities.csv'
p = os.path.join(os.path.dirname(__file__), f)  
if os.path.exists(p):
    print(f'Tamaño del archivo {f}: {os.path.getsize(p)} bytes')
else:
    print(f'Archivo no encontrado: {f}')

# Leemos fichero con pandas
df_cities = pd.read_csv(p)
# Calculamos el tamaño en memoria del DataFrame entero
tam_tot = df_cities.memory_usage(deep=True).sum()
print(f'Tamaño en memoria del DataFrame cities.csv: {tam_tot} bytes')
# Vemos ahora cuanto ocupa cada columna
for col in df_cities.columns:
    tam_col = df_cities[col].memory_usage(deep=True)
    print(f'  Columna {col}: {tam_col} bytes')

# ¿El tamaño que ocupa en memoria, es más o menos de lo que ocupa el fichero en disco? ¿A qué crees que se debe?
# Normalmente el DataFrame en memoria ocupa bastante más que el fichero en disco.
# Por qué:
# - El CSV es texto secuencial (compacto y a menudo más pequeño que su representación en memoria).
# - Pandas parsea y crea estructuras en memoria: arrays numpy (tamaños fijos), índice y metadatos.
# - Las columnas tipo object (strings) son objetos Python con overhead (punteros, capacidades internas); memory_usage(deep=True) incluye ese overhead.
# - Alineamiento y padding de estructura en memoria aumentan el tamaño respecto al texto plano.
# - Posibles copies intermedias al leer/parsear también consumen memoria.

f = 'cities.csv'
p = os.path.join(os.path.dirname(__file__), f)
if not os.path.exists(p):
    print('Archivo no encontrado:', f)
else:
    df = pd.read_csv(p)

    before = df.memory_usage(deep=True)
    print('Memoria antes (bytes por columna):')
    print(before)
    print('Total antes:', before.sum(), 'bytes')

    # Intentar convertir columnas object que sean numéricas
    for col in df.select_dtypes(include=['object']).columns:
        tmp = pd.to_numeric(df[col], errors='coerce')
        if tmp.notna().all():
            df[col] = tmp

    # Reducir tamaño de columnas numéricas sin perder representación
    for col in df.select_dtypes(include=['number']).columns:
        if pd.api.types.is_float_dtype(df[col].dtype):
            # si todos los floats son enteros y no hay NaN, convertir a integer downcast
            if df[col].notna().all() and (df[col] % 1 == 0).all():
                df[col] = pd.to_numeric(df[col], downcast='integer')
            else:
                df[col] = pd.to_numeric(df[col], downcast='float')
        else:
            df[col] = pd.to_numeric(df[col], downcast='integer')

    after = df.memory_usage(deep=True)
    print('\nMemoria después (bytes por columna):')
    print(after)
    print('Total después:', after.sum(), 'bytes')

# Pregunta:
#¿Cuánto ocupa ahora en memoria el dataframe?
# - La reducción exacta depende de los datos y de cuántas columnas podían ser downcasteadas. En concreto, ha pasado de pesar 34313 bytes a 28937 bytes.

dtype = {
    'id': 'int32',
    'population': 'int32',
    'area_km2': 'float32',
    'country': 'category'
}
df2 = pd.read_csv('cities.csv', dtype=dtype, parse_dates=['date_col'], usecols=['id','population','area_km2','country'])
print('\nDataFrame con dtypes especificados al leer:')
print(df2.info(memory_usage='deep'))