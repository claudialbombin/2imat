import pandas as pd
import numpy as np
import re

def airbnb_read(path_to_file):
    """
    This function reads a pandas DataFrame from a path to a csv file
    
    Args:
        path_to_file (str): The path to the csv file.
    
    Returns:
        pd.DataFrame: The DataFrame containing the Airbnb data.
    """
    # Leer el archivo CSV y devolver el DataFrame
    df = pd.read_csv(path_to_file)
    return df

def airbnb_size(df):
    """
    This function takes a pandas DataFrame and returns its dimensions (n_rows, n_cols)
    
    Args:
        df (pd.DataFrame): A Pandas DataFrame
    
    Returns:
        tuple: A tuple containing (number_of_rows, number_of_columns)
    """
    # Devolver las dimensiones del DataFrame (filas, columnas)
    return df.shape

def airbnb_columns(df):
    """
    This function takes a pandas DataFrame and returns a list with column names in original order
    
    Args:
        df (pd.DataFrame): A Pandas DataFrame
    
    Returns:
        pd.Index: Column names in original order
    """
    # Devolver los nombres de las columnas en orden original
    return df.columns

def airbnb_countries(df):
    """
    This function takes the initial DataFrame and returns a Series with number of listings per country
    
    Args:
        df (pd.DataFrame): The initial Airbnb DataFrame
    
    Returns:
        pd.Series: Series with country names as index and number of listings as values
    """
    # Limpiar y estandarizar los nombres de países (strip y title case)
    s = df['country'].astype(str).str.strip().str.title()
    # Contar ocurrencias por país y devolver Series
    return s.value_counts()

def airbnb_boroughs(df):
    """
    This function takes the initial DataFrame and returns a Series with number of listings per neighbourhood group
    
    Args:
        df (pd.DataFrame): The initial Airbnb DataFrame
    
    Returns:
        pd.Series: Series with neighbourhood group names as index and number of listings as values
    """
    # Limpiar y estandarizar los nombres de neighbourhood groups
    s = df['neighbourhood group'].astype(str).str.strip().str.title()
    # Contar ocurrencias por neighbourhood group y devolver Series
    return s.value_counts()

def airbnb_price(df):
    """
    This function takes the initial DataFrame and returns a new DataFrame with numeric price column and no NaN prices
    
    Args:
        df (pd.DataFrame): The initial Airbnb DataFrame
    
    Returns:
        pd.DataFrame: New DataFrame with numeric price column and no NaN values in price
    """
    # Crear copia del DataFrame original para no modificar el original
    df_new = df.copy()
    
    # Limpiar la columna price: eliminar símbolos de moneda y dejar solo números y punto decimal
    df_new['price'] = (
        df_new['price']
        .astype(str)
        .str.replace(r'[^0-9.]', '', regex=True)  # regex para mantener solo dígitos y punto
    )
    
    # Convertir a numérico, coercer errores a NaN
    df_new['price'] = pd.to_numeric(df_new['price'], errors='coerce')
    
    # Eliminar filas donde price es NaN
    df_new = df_new.dropna(subset=['price'])
    
    return df_new

def airbnb_aggregate(df):
    """
    This function takes a DataFrame and returns a new DataFrame with mean, min, max prices per neighbourhood group
    
    Args:
        df (pd.DataFrame): A Pandas DataFrame
    
    Returns:
        pd.DataFrame: New DataFrame with aggregated price statistics by neighbourhood group and neighbourhood
    """
    # Crear copia y normalizar nombres de columnas (minúsculas y sin espacios extra)
    df_new = df.copy()
    df_new.columns = df_new.columns.str.strip().str.lower()
    
    # Limpiar y convertir la columna price a numérico
    df_new['price'] = (
        df_new['price']
        .astype(str)
        .str.replace(r'[^0-9.]', '', '', regex=True)
    )
    df_new['price'] = pd.to_numeric(df_new['price'], errors='coerce')
    
    # Eliminar filas con price NaN
    df_new = df_new.dropna(subset=['price'])
    
    # Agrupar por neighbourhood group y neighbourhood, calcular estadísticas agregadas
    result = df_new.groupby(
        ['neighbourhood group', 'neighbourhood'], as_index=False
    ).agg(
        mean_price=('price', 'mean'),  # Precio promedio
        min_price=('price', 'min'),    # Precio mínimo
        max_price=('price', 'max')     # Precio máximo
    )

    return result

def airbnb_totals(df):
    """
    This function takes the original DataFrame and returns a new DataFrame with total airbnbs grouped by neighbourhood group
    
    Args:
        df (pd.DataFrame): The original Airbnb DataFrame
    
    Returns:
        pd.DataFrame: New DataFrame with total airbnbs per neighbourhood group
    """
    # Crear copia y normalizar nombres de columnas
    df_new = df.copy()
    df_new.columns = df_new.columns.str.strip().str.lower()
    
    # Contar el número total de airbnbs por neighbourhood group
    result = df_new.groupby('neighbourhood group', as_index=False).size()
    # Renombrar la columna de conteo
    result = result.rename(columns={'size': 'total_airbnbs'})
    
    return result

def population_totals(df):
    """
    This function takes the population DataFrame and returns a new DataFrame with total population grouped by borough
    
    Args:
        df (pd.DataFrame): The population DataFrame
    
    Returns:
        pd.DataFrame: New DataFrame with total population per borough
    """
    # Crear copia y normalizar nombres de columnas
    df_new = df.copy()
    df_new.columns = df_new.columns.str.strip().str.lower()
    
    # Agrupar por borough y sumar la población
    result = df_new.groupby('borough', as_index=False)['population'].sum()
    
    return result

def airbnb_population(df_airbnb, df_population):
    """
    This function takes two DataFrames and returns a new DataFrame containing number of airbnbs per 1000 inhabitants
    
    Args:
        df_airbnb (pd.DataFrame): The DataFrame produced by airbnb_totals
        df_population (pd.DataFrame): The DataFrame produced by population_totals
    
    Returns:
        pd.DataFrame: New DataFrame with airbnbs per 1000 inhabitants by borough
    """
    # Obtener DataFrames procesados de airbnbs y población
    df_airbnb_totals = airbnb_totals(df_airbnb)
    df_population_totals = population_totals(df_population)
    
    # Unir los dos DataFrames por borough/neighbourhood group
    merged_df = pd.merge(
        df_airbnb_totals,
        df_population_totals,
        left_on='neighbourhood group',
        right_on='borough',
        how='inner'  # Solo mantener registros que existen en ambos DataFrames
    )
    
    # Calcular la densidad de airbnbs por 1000 habitantes
    merged_df['airbnbs_per_1000'] = (merged_df['total_airbnbs'] / merged_df['population']) * 1000
    
    # Seleccionar las columnas relevantes para el resultado final
    result = merged_df[['neighbourhood group', 'total_airbnbs', 'population', 'airbnbs_per_1000']]
    
    return result


if __name__ == "__main__":
    # Rutas a los archivos (ajustar según sea necesario)
    file_path_airbnb = '/Users/claudialbombin/Desktop/2025 -2026/Practicas/Adquisicion/P2/airbnb.csv'
    df_airbnb = airbnb_read(file_path_airbnb)
    
    file_path_population = '/Users/claudialbombin/Desktop/2025 -2026/Practicas/Adquisicion/P2/population.csv'
    df_population = airbnb_read(file_path_population)
    
    # Probar la función principal
    print(airbnb_population(df_airbnb, df_population))