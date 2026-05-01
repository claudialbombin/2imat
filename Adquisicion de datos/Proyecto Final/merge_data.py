"""
Parte 3: Cruzado de los datos de ambas fuentes
=============================================
Requisitos según el enunciado:
1. Un único DataFrame donde cada fila = resultado de un piloto en una carrera
2. Todas las columnas de resultados (Parte 1) + todas las columnas de pitstops (Parte 2)
3. Columnas adicionales: "Season" y "RaceNumber"
4. Exportar a CSV
"""

import os
import pandas as pd
import glob
from pathlib import Path
import json
import re

def get_season_calendar(season):
    """
    Devuelve el calendario de carreras para una temporada específica.
    Esto es necesario para asignar RaceNumber correctamente.
    Basado en calendarios reales de F1.
    """
    calendars = {
        2012: [
            'Australian', 'Malaysian', 'Chinese', 'Bahrain', 'Spanish',
            'Monaco', 'Canadian', 'European', 'British', 'German',
            'Hungarian', 'Belgian', 'Italian', 'Singapore', 'Japanese',
            'Korean', 'Indian', 'Abu_Dhabi', 'United_States', 'Brazilian'
        ],
        2013: [
            'Australian', 'Malaysian', 'Chinese', 'Bahrain', 'Spanish',
            'Monaco', 'Canadian', 'British', 'German', 'Hungarian',
            'Belgian', 'Italian', 'Singapore', 'Korean', 'Japanese',
            'Indian', 'Abu_Dhabi', 'United_States', 'Brazilian'
        ],
        2014: [
            'Australian', 'Malaysian', 'Bahrain', 'Chinese', 'Spanish',
            'Monaco', 'Canadian', 'Austrian', 'British', 'German',
            'Hungarian', 'Belgian', 'Italian', 'Singapore', 'Japanese',
            'Russian', 'United_States', 'Brazilian', 'Abu_Dhabi'
        ],
        2015: [
            'Australian', 'Malaysian', 'Chinese', 'Bahrain', 'Spanish',
            'Monaco', 'Canadian', 'Austrian', 'British', 'Hungarian',
            'Belgian', 'Italian', 'Singapore', 'Japanese', 'Russian',
            'United_States', 'Mexican', 'Brazilian', 'Abu_Dhabi'
        ],
        2016: [
            'Australian', 'Bahrain', 'Chinese', 'Russian', 'Spanish',
            'Monaco', 'Canadian', 'European', 'Austrian', 'British',
            'Hungarian', 'German', 'Belgian', 'Italian', 'Singapore',
            'Malaysian', 'Japanese', 'United_States', 'Mexican', 'Brazilian', 'Abu_Dhabi'
        ],
        2017: [
            'Australian', 'Chinese', 'Bahrain', 'Russian', 'Spanish',
            'Monaco', 'Canadian', 'Azerbaijan', 'Austrian', 'British',
            'Hungarian', 'Belgian', 'Italian', 'Singapore', 'Malaysian',
            'Japanese', 'United_States', 'Mexican', 'Brazilian', 'Abu_Dhabi'
        ],
        2018: [
            'Australian', 'Bahrain', 'Chinese', 'Azerbaijan', 'Spanish',
            'Monaco', 'Canadian', 'French', 'Austrian', 'British',
            'German', 'Hungarian', 'Belgian', 'Italian', 'Singapore',
            'Russian', 'Japanese', 'United_States', 'Mexican', 'Brazilian', 'Abu_Dhabi'
        ],
        2019: [
            'Australian', 'Bahrain', 'Chinese', 'Azerbaijan', 'Spanish',
            'Monaco', 'Canadian', 'French', 'Austrian', 'British',
            'German', 'Hungarian', 'Belgian', 'Italian', 'Singapore',
            'Russian', 'Japanese', 'Mexican', 'United_States', 'Brazilian', 'Abu_Dhabi'
        ],
        2020: [
            'Austrian', 'Styrian', 'Hungarian', 'British', '70th_Anniversary',
            'Spanish', 'Belgian', 'Italian', 'Tuscan', 'Russian',
            'Eifel', 'Portuguese', 'Emilia-Romagna', 'Turkish', 'Bahrain', 'Sakhir', 'Abu_Dhabi'
        ],
        2021: [
            'Bahrain', 'Emilia-Romagna', 'Portuguese', 'Spanish', 'Monaco',
            'Azerbaijan', 'French', 'Styrian', 'Austrian', 'British',
            'Hungarian', 'Belgian', 'Dutch', 'Italian', 'Russian',
            'Turkish', 'United_States', 'Mexico_City', 'São_Paulo', 'Qatar', 'Saudi_Arabian', 'Abu_Dhabi'
        ],
        2022: [
            'Bahrain', 'Saudi_Arabian', 'Australian', 'Emilia-Romagna', 'Miami',
            'Spanish', 'Monaco', 'Azerbaijan', 'Canadian', 'British',
            'Austrian', 'French', 'Hungarian', 'Belgian', 'Dutch',
            'Italian', 'Singapore', 'Japanese', 'United_States', 'Mexico_City', 'São_Paulo', 'Abu_Dhabi'
        ],
        2023: [
            'Bahrain', 'Saudi_Arabian', 'Australian', 'Azerbaijan', 'Miami',
            'Monaco', 'Spanish', 'Canadian', 'Austrian', 'British',
            'Hungarian', 'Belgian', 'Dutch', 'Italian', 'Singapore',
            'Japanese', 'Qatar', 'United_States', 'Mexico_City', 'São_Paulo', 'Las_Vegas', 'Abu_Dhabi'
        ],
        2024: [
            'Bahrain', 'Saudi_Arabian', 'Australian', 'Japanese', 'Chinese',
            'Miami', 'Emilia-Romagna', 'Monaco', 'Canadian', 'Spanish',
            'Austrian', 'British', 'Hungarian', 'Belgian', 'Dutch',
            'Italian', 'Azerbaijan', 'Singapore', 'United_States', 'Mexico_City',
            'São_Paulo', 'Las_Vegas', 'Qatar', 'Abu_Dhabi'
        ]
    }
    
    return calendars.get(season, [])

def find_race_number(season, race_filename, calendar):
    """
    Encuentra el número de carrera (RaceNumber) basado en el calendario.
    """
    # Normalizar nombre de archivo
    race_name = Path(race_filename).stem
    
    # Casos especiales
    special_names = {
        '70th_Anniversary_Grand_Prix': '70th_Anniversary',
        'Mexico_City_Grand_Prix': 'Mexico_City',
        'São_Paulo_Grand_Prix': 'São_Paulo',
        'Saudi_Arabian_Grand_Prix': 'Saudi_Arabian',
        'Las_Vegas_Grand_Prix': 'Las_Vegas',
        'Styrian_Grand_Prix': 'Styrian',
        'Tuscan_Grand_Prix': 'Tuscan',
        'Eifel_Grand_Prix': 'Eifel',
        'Emilia-Romagna_Grand_Prix': 'Emilia-Romagna',
        'Dutch_Grand_Prix': 'Dutch',
        'Sakhir_Grand_Prix': 'Sakhir'
    }
    
    # Verificar casos especiales primero
    for special, normalized in special_names.items():
        if special in race_name:
            race_key = normalized
            break
    else:
        # Extraer nombre base (sin _Grand_Prix)
        race_key = race_name.replace('_Grand_Prix', '')
    
    # Buscar en el calendario
    for i, calendar_race in enumerate(calendar, 1):
        if calendar_race.lower() in race_key.lower() or race_key.lower() in calendar_race.lower():
            return i
    
    # Si no se encuentra, devolver None
    return None

def standardize_results_columns(df):
    """
    Estandariza los nombres de columnas del DataFrame de resultados.
    Elimina columnas no deseadas y renombra columnas inconsistentes.
    """
    # Crear copia para no modificar el original
    df_clean = df.copy()
    
    # Diccionario de mapeo de nombres de columnas
    column_mapping = {
        # Mapeo de nombres alternativos a nombres estándar
        'No': 'DriverNumber',
        'No.': 'DriverNumber',
        'Number': 'DriverNumber',
        'Driver Number': 'DriverNumber',
        'Num': 'DriverNumber',
        'Car number': 'DriverNumber',
        
        'Pos': 'Position',
        'Pos.': 'Position',
        'Position': 'Position',
        
        'Driver': 'Driver',
        'Piloto': 'Driver',
        'Pilot': 'Driver',
        
        'Constructor': 'Constructor',
        'Team': 'Constructor',
        'Constructor/Team': 'Constructor',
        
        'Laps': 'Laps',
        'Laps1': 'Laps',
        'Lapsa': 'Laps',
        'Laps.': 'Laps',
        
        'Time/Retired': 'Time',
        'Time': 'Time',
        'Time/Retired.': 'Time',
        'Race Time': 'Time',
        
        'Grid': 'Grid',
        'Grid[43]': 'Grid',
        'Start': 'Grid',
        'Grid Pos': 'Grid',
        'Grid Position': 'Grid',
        
        'Points': 'Points',
        'Pts.': 'Points',
        'Points1': 'Points',
        'Pts': 'Points',
        'Puntos': 'Points',
        
        # Columnas que deben eliminarse
        'Unnamed: 0': None,
        'Unnamed: 1': None,
        'Unnamed: 2': None,
        'Unnamed: 3': None,
        'Unnamed: 4': None,
        'Unnamed: 5': None,
        'Unnamed: 6': None,
        'Unnamed: 7': None,
        'Unnamed: 8': None,
        'Unnamed: 9': None,
        'Unnamed: 10': None,
        'Unnamed: 11': None,
        'Unnamed: 12': None,
    }
    
    # Lista de columnas estándar que queremos mantener
    standard_columns = [
        'Position', 'DriverNumber', 'Driver', 'Constructor', 
        'Laps', 'Time', 'Grid', 'Points'
    ]
    
    # Renombrar columnas según el mapeo
    for old_name, new_name in column_mapping.items():
        if old_name in df_clean.columns:
            if new_name is None:
                # Eliminar columna no deseada
                df_clean = df_clean.drop(columns=[old_name], errors='ignore')
            else:
                # Renombrar columna
                df_clean = df_clean.rename(columns={old_name: new_name})
    
    # Eliminar columnas que contengan "Unnamed" en el nombre
    unnamed_cols = [col for col in df_clean.columns if 'Unnamed' in col]
    if unnamed_cols:
        df_clean = df_clean.drop(columns=unnamed_cols, errors='ignore')
    
    # Eliminar columnas con nombres extraños (contienen caracteres especiales o números entre corchetes)
    strange_cols = [col for col in df_clean.columns if re.search(r'\[\d+\]', col) or col.endswith('1') or col.endswith('a')]
    if strange_cols:
        df_clean = df_clean.drop(columns=strange_cols, errors='ignore')
    
    # Mantener solo las columnas estándar (si existen)
    available_standard_cols = [col for col in standard_columns if col in df_clean.columns]
    
    # También mantener cualquier otra columna que no sea estándar pero pueda ser útil
    # (excluyendo las que ya sabemos que son basura)
    additional_cols = []
    for col in df_clean.columns:
        if col not in available_standard_cols and col not in ['Season', 'RaceNumber']:
            # Verificar si la columna tiene datos útiles
            if df_clean[col].notna().sum() > 0:
                additional_cols.append(col)
    
    # Orden final de columnas
    final_cols = ['Season', 'RaceNumber'] + available_standard_cols + additional_cols
    
    return df_clean[final_cols]

def create_driver_mapping():
    """
    Crea un mapeo para resolver inconsistencias en números de piloto.
    """
    return {
        # Mapeo por driverId
        'max_verstappen': '33',
        'lewis_hamilton': '44',
        'valtteri_bottas': '77',
        'carlos_sainz': '55',
        'charles_leclerc': '16',
        'lando_norris': '4',
        'george_russell': '63',
        'fernando_alonso': '14',
        'esteban_ocon': '31',
        'pierre_gasly': '10',
        'yuki_tsunoda': '22',
        'daniel_ricciardo': '3',
        'kevin_magnussen': '20',
        'mick_schumacher': '47',
        'sebastian_vettel': '5',
        'lance_stroll': '18',
        'nicholas_latifi': '6',
        'alexander_albon': '23',
        'sergio_perez': '11',
        'kimi_raikkonen': '7',
        'antonio_giovinazzi': '99',
        'nyck_de_vries': '21',
        'logan_sargeant': '2',
        'nico_hulkenberg': '27',
        'guanyu_zhou': '24',
        'oscar_piastri': '81',
    }

def standardize_driver_number(driver_number):
    """
    Estandariza el número de piloto a string.
    """
    if pd.isna(driver_number):
        return None
    
    # Convertir a string y limpiar
    num_str = str(driver_number).strip()
    
    # Remover decimales si es float
    if '.' in num_str:
        num_str = num_str.split('.')[0]
    
    return num_str

def merge_race_data(season, race_number, race_filename, calendar):
    """
    Fusiona datos de una carrera específica.
    """
    # Cargar resultados
    results_path = f"data/{season}/{race_filename}"
    
    if not os.path.exists(results_path):
        print(f"    Archivo no encontrado: {results_path}")
        return None
    
    try:
        results_df = pd.read_csv(results_path)
        
        if results_df.empty:
            print(f"    DataFrame vacío: {race_filename}")
            return None
        
        # Añadir columnas requeridas Season y RaceNumber
        results_df = results_df.copy()
        results_df['Season'] = season
        results_df['RaceNumber'] = race_number
        
        # Estandarizar columnas de resultados
        results_df = standardize_results_columns(results_df)
        
        # Para temporadas 2019-2024, fusionar con pitstops
        if season >= 2019:
            pitstop_path = f"data/pitstops/{season}/{season}_round{race_number:02d}_pitstops.csv"
            
            if os.path.exists(pitstop_path):
                try:
                    pitstops_df = pd.read_csv(pitstop_path)
                    
                    if not pitstops_df.empty:
                        # Estandarizar DriverNumber en results_df
                        if 'DriverNumber' in results_df.columns:
                            results_df['DriverNumber_Std'] = results_df['DriverNumber'].apply(
                                lambda x: standardize_driver_number(x)
                            )
                        
                        # Preparar pitstops_df para el merge
                        driver_mapping = create_driver_mapping()
                        
                        # Si pitstops_df tiene DriverNumber, usarlo
                        if 'DriverNumber' in pitstops_df.columns:
                            pitstops_df['DriverNumber_Std'] = pitstops_df['DriverNumber'].apply(
                                lambda x: standardize_driver_number(x)
                            )
                        else:
                            # Si no tiene DriverNumber, usar el mapeo por DriverId
                            pitstops_df['DriverNumber_Std'] = pitstops_df['DriverId'].map(
                                lambda x: driver_mapping.get(x, None)
                            )
                        
                        # Columnas que queremos de pitstops
                        pitstop_cols_to_merge = ['DriverId', 'NPitstops', 'MedianPitStopDuration']
                        available_pitstop_cols = [col for col in pitstop_cols_to_merge if col in pitstops_df.columns]
                        
                        # Realizar merge solo si tenemos DriverNumber_Std en ambos DataFrames
                        if 'DriverNumber_Std' in results_df.columns and 'DriverNumber_Std' in pitstops_df.columns:
                            merged_df = pd.merge(
                                results_df,
                                pitstops_df[['DriverNumber_Std'] + available_pitstop_cols],
                                left_on='DriverNumber_Std',
                                right_on='DriverNumber_Std',
                                how='left'
                            )
                            
                            # Eliminar columna temporal
                            merged_df = merged_df.drop(columns=['DriverNumber_Std'], errors='ignore')
                            
                            # Reordenar columnas
                            base_cols = [col for col in merged_df.columns if col not in available_pitstop_cols]
                            merged_df = merged_df[base_cols + available_pitstop_cols]
                            
                            return merged_df
                        else:
                            print(f"    No se pudo hacer merge para {race_filename}: falta DriverNumber")
                            # Añadir columnas de pitstops vacías
                            for col in pitstop_cols_to_merge:
                                results_df[col] = pd.NA
                            return results_df
                    else:
                        print(f"    DataFrame de pitstops vacío para {race_filename}")
                        # Añadir columnas de pitstops vacías
                        pitstop_cols = ['DriverId', 'NPitstops', 'MedianPitStopDuration']
                        for col in pitstop_cols:
                            results_df[col] = pd.NA
                        return results_df
                        
                except Exception as e:
                    print(f"    Error cargando pitstops para {race_filename}: {str(e)}")
                    # Añadir columnas de pitstops vacías
                    pitstop_cols = ['DriverId', 'NPitstops', 'MedianPitStopDuration']
                    for col in pitstop_cols:
                        results_df[col] = pd.NA
                    return results_df
            else:
                print(f"    Archivo de pitstops no encontrado: {pitstop_path}")
                # Añadir columnas de pitstops vacías
                pitstop_cols = ['DriverId', 'NPitstops', 'MedianPitStopDuration']
                for col in pitstop_cols:
                    results_df[col] = pd.NA
                return results_df
        else:
            # Para temporadas anteriores a 2019, solo devolver resultados estandarizados
            return results_df
            
    except Exception as e:
        print(f"    Error procesando {race_filename}: {str(e)}")
        return None

def merge_all_data():
    """
    Función principal que fusiona todos los datos.
    """
    print("="*70)
    print("PARTE 3: CRUZADO DE DATOS DE RESULTADOS Y PITSTOPS")
    print("="*70)
    
    all_merged = []
    
    # Procesar cada temporada
    for season in range(2012, 2025):
        print(f"\n Procesando temporada {season}...")
        
        # Obtener calendario
        calendar = get_season_calendar(season)
        if not calendar:
            print(f"    No hay calendario definido para {season}")
            continue
        
        # Buscar archivos de resultados
        results_dir = f"data/{season}"
        if not os.path.exists(results_dir):
            print(f"    No hay datos de resultados para {season}")
            continue
        
        result_files = sorted(glob.glob(os.path.join(results_dir, "*.csv")))
        print(f"   {len(result_files)} carreras encontradas")
        
        # Procesar cada carrera
        for race_file in result_files:
            race_filename = os.path.basename(race_file)
            
            # Determinar número de carrera
            race_number = find_race_number(season, race_filename, calendar)
            
            if race_number is None:
                print(f"    No se pudo determinar RaceNumber para: {race_filename}")
                continue
            
            # Fusionar datos
            merged_df = merge_race_data(season, race_number, race_filename, calendar)
            
            if merged_df is not None:
                all_merged.append(merged_df)
                print(f"     ✓ {race_filename}: {len(merged_df)} filas, {len(merged_df.columns)} columnas")
    
    # Combinar todos los DataFrames
    if not all_merged:
        print("\n ✗ No se pudieron fusionar datos")
        return None
    
    print(f"\n{'='*70}")
    print("COMBINANDO DATOS DE TODAS LAS TEMPORADAS...")
    
    final_df = pd.concat(all_merged, ignore_index=True)
    
    # Columnas base que deben estar primero
    base_cols = ['Season', 'RaceNumber']
    available_base_cols = [col for col in base_cols if col in final_df.columns]
    
    # Columnas estándar de resultados (en el orden deseado)
    standard_result_cols = ['Position', 'DriverNumber', 'Driver', 'Constructor', 'Laps', 'Time', 'Grid', 'Points']
    available_result_cols = [col for col in standard_result_cols if col in final_df.columns]
    
    # Columnas de pitstops
    pitstop_cols = ['DriverId', 'NPitstops', 'MedianPitStopDuration']
    available_pitstop_cols = [col for col in pitstop_cols if col in final_df.columns]
    
    # Otras columnas (deben ser examinadas)
    other_cols = [col for col in final_df.columns 
                  if col not in available_base_cols + 
                  available_result_cols + 
                  available_pitstop_cols]
    
    # Mostrar columnas que se mantendrán y las que se eliminarán
    print(f"\n Columnas detectadas en el dataset:")
    print(f"   Base: {available_base_cols}")
    print(f"   Resultados: {available_result_cols}")
    print(f"   Pitstops: {available_pitstop_cols}")
    
    if other_cols:
        print(f"   Otras columnas detectadas (serán eliminadas): {other_cols}")
        
        # Eliminar columnas no deseadas
        columns_to_drop = []
        for col in other_cols:
            # Verificar si la columna parece ser útil
            is_useful = False
            
            # Si tiene más del 50% de valores no nulos, podría ser útil
            if final_df[col].notna().sum() / len(final_df) > 0.5:
                # Pero si contiene patrones de nombres extraños, igual la eliminamos
                if not (re.search(r'\[\d+\]', col) or 
                        col.endswith('1') or 
                        col.endswith('a') or 
                        'Unnamed' in col or
                        col in ['Start', 'Pts.', 'Pts', 'Puntos', 'Laps1', 'Lapsa', 'Points1']):
                    is_useful = True
            
            if not is_useful:
                columns_to_drop.append(col)
        
        if columns_to_drop:
            print(f"   Eliminando {len(columns_to_drop)} columnas no deseadas: {columns_to_drop}")
            final_df = final_df.drop(columns=columns_to_drop, errors='ignore')
    
    # Reordenar columnas
    final_order = available_base_cols + available_result_cols + available_pitstop_cols
    final_df = final_df[final_order]
    
    # Exportar a CSV
    os.makedirs("merged_data", exist_ok=True)
    output_file = "merged_data/f1_complete_dataset.csv"
    final_df.to_csv(output_file, index=False)
    
    # Crear metadatos
    create_metadata(final_df, output_file)
    
    # Mostrar estadísticas
    print_stats(final_df, output_file)
    
    return final_df

def create_metadata(df, output_path):
    """Crea archivo de metadatos."""
    metadata = {
        "dataset": "Formula 1 Complete Dataset 2012-2024",
        "description": "Dataset fusionado de resultados de carreras y pitstops",
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "season_range": f"{int(df['Season'].min())}-{int(df['Season'].max())}",
        "unique_seasons": sorted([int(s) for s in df['Season'].unique()]),
        "unique_races": len(df[['Season', 'RaceNumber']].drop_duplicates()),
        "columns": list(df.columns),
        "column_descriptions": {
            "Season": "Año de la temporada",
            "RaceNumber": "Número de carrera en la temporada (1, 2, 3...)",
            "Position": "Posición final en la carrera",
            "DriverNumber": "Número del piloto",
            "Driver": "Nombre del piloto",
            "Constructor": "Escudería/equipo",
            "Laps": "Vueltas completadas",
            "Time": "Tiempo total o estado (ej: 'Retired')",
            "Grid": "Posición de salida",
            "Points": "Puntos obtenidos",
            "DriverId": "ID único del piloto (solo 2019-2024)",
            "NPitstops": "Número de paradas en boxes (solo 2019-2024)",
            "MedianPitStopDuration": "Duración mediana de paradas (solo 2019-2024)"
        },
        "pitstops_available_from": 2019,
        "generated_date": pd.Timestamp.now().isoformat()
    }
    
    metadata_file = output_path.replace('.csv', '_metadata.json')
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"   ✓ Metadatos guardados en: {metadata_file}")

def print_stats(df, output_path):
    """Muestra estadísticas del dataset."""
    print(f"\n{'='*70}")
    print("DATASET FINAL CREADO:")
    print(f"{'='*70}")
    print(f"    Archivo: {output_path}")
    print(f"    Total filas: {len(df):,}")
    print(f"    Total columnas: {len(df.columns)}")
    
    print(f"\n DISTRIBUCIÓN POR TEMPORADA:")
    season_counts = df['Season'].value_counts().sort_index()
    for season, count in season_counts.items():
        if season >= 2019:
            pitstops_count = df[df['Season'] == season]['NPitstops'].notna().sum()
            print(f"   {int(season)}: {count:>4} filas | Pitstops: {pitstops_count:>4} ({pitstops_count/count*100:>5.1f}%)")
        else:
            print(f"   {int(season)}: {count:>4} filas | Sin datos de pitstops")
    
    print(f"\n COLUMNAS DEL DATASET:")
    for col in df.columns:
        non_null = df[col].notna().sum()
        dtype = str(df[col].dtype)
        print(f"   {col:25} {dtype:10} {non_null:>6} no nulos ({non_null/len(df)*100:>5.1f}%)")

def validate_requirements(df):
    """Valida que se cumplan los requisitos del punto 3."""
    print(f"\n{'='*70}")
    print("VALIDACIÓN DE REQUISITOS (Punto 3)")
    print(f"{'='*70}")
    
    # Columnas requeridas según tu descripción
    required_result_cols = ['Position', 'DriverNumber', 'Driver', 'Constructor', 'Laps', 'Time', 'Grid', 'Points']
    required_pitstop_cols = ['DriverId', 'NPitstops', 'MedianPitStopDuration']
    
    requirements = [
        ("1. DataFrame único creado", df is not None),
        ("2. Columnas Season y RaceNumber presentes", 
         all(col in df.columns for col in ['Season', 'RaceNumber'])),
        ("3. Season no contiene valores nulos", df['Season'].notna().all()),
        ("4. RaceNumber no contiene valores nulos", df['RaceNumber'].notna().all()),
        ("5. Contiene todas las columnas de resultados (8 columnas)", 
         sum(col in df.columns for col in required_result_cols) == 8),
        ("6. Contiene todas las columnas de pitstops para 2019-2024", 
         all(col in df.columns for col in required_pitstop_cols)),
        ("7. No hay columnas adicionales no deseadas", 
         len(df.columns) == 2 + 8 + 3),  # Season+RaceNumber + 8 resultados + 3 pitstops
        ("8. Exportado a CSV", os.path.exists("merged_data/f1_complete_dataset.csv")),
    ]
    
    all_passed = True
    for req_name, condition in requirements:
        status = "✓" if condition else "✗"
        print(f"  {status} {req_name}")
        if not condition:
            all_passed = False
    
    # Información adicional
    print(f"\n Columnas actuales ({len(df.columns)}): {list(df.columns)}")
    print(f" Columnas esperadas (13): Season, RaceNumber + 8 resultados + 3 pitstops")
    
    return all_passed

if __name__ == "__main__":
    # Ejecutar la fusión
    dataset = merge_all_data()
    
    if dataset is not None:
        # Validar requisitos
        requirements_met = validate_requirements(dataset)
        
        # Mostrar ejemplo
        print(f"\n{'='*70}")
        print("EJEMPLO DEL DATASET (primeras 5 filas):")
        print(f"{'='*70}")
        print(dataset.head().to_string())
        
        print(f"\n{'='*70}")
        if requirements_met:
            print("✓ TODOS LOS REQUISITOS DEL PUNTO 3 CUMPLIDOS")
        else:
            print("✗ Algunos requisitos no se cumplen completamente")
        
        print(f"\n El dataset está listo para el análisis de la Parte 4")
        print(f" Ubicación: merged_data/f1_complete_dataset.csv")
        
        # Mostrar información sobre datos faltantes
        print(f"\n RESUMEN DE DATOS FALTANTES:")
        for col in dataset.columns:
            if col in ['DriverId', 'NPitstops', 'MedianPitStopDuration']:
                missing = dataset[col].isna().sum()
                if missing > 0:
                    print(f"   {col}: {missing} valores faltantes ({missing/len(dataset)*100:.1f}%)")
    else:
        print("\n ✗ Error: No se pudo crear el dataset")