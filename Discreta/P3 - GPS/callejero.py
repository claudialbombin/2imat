"""
callejero.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP06
Integrantes:
    - Claudia Maria Lopez Bombin
    - Lucía Lozano Isac

Descripción:
Librería con herramientas y clases auxiliares necesarias para la representación de un callejero en un grafo.

Complétese esta descripción según las funcionalidades agregadas por el grupo.
"""

import osmnx as ox
import networkx as nx
import pandas as pd
import re
import chardet
from typing import Tuple
import matplotlib.pyplot as plt
import os
#from fuzzywuzzy import fuzz, process

STREET_FILE_NAME="direcciones.csv"

PLACE_NAME = "Madrid, Spain"
MAP_FILE_NAME="madrid.graphml"

MAX_SPEEDS={'living_street': '20',
 'residential': '30',
 'primary_link': '40',
 'unclassified': '40',
 'secondary_link': '40',
 'trunk_link': '40',
 'secondary': '50',
 'tertiary': '50',
 'primary': '50',
 'trunk': '50',
 'tertiary_link':'50',
 'busway': '50',
 'motorway_link': '70',
 'motorway': '100'}

############# Excepciones ###########
class ServiceNotAvailableError(Exception):
    "Excepción que indica que la navegación no está disponible en este momento"
    pass

class AdressNotFoundError(Exception):
    "Excepción que indica que una dirección buscada no existe en la base de datos"
    pass


############ Auxiliares ############

# Normalizacion de texto para poder buscar, independientemente de caracteres especiales y/o mayusculas y minusculas
def normalizar_texto(texto: str) -> str:
    """Normaliza el texto para búsquedas: quita acentos, mayúsculas, espacios extra"""
    texto = texto.upper().strip()
    # Reemplazar caracteres con acentos
    reemplazos = {
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'À': 'A', 'È': 'E', 'Ì': 'I', 'Ò': 'O', 'Ù': 'U',
        'Ä': 'A', 'Ë': 'E', 'Ï': 'I', 'Ö': 'O', 'Ü': 'U'
    }
    for orig, repl in reemplazos.items():
        texto = texto.replace(orig, repl)
    # Quitar espacios extra
    texto = re.sub(r'\s+', ' ', texto)
    return texto

# Normalizacion de nombres propios para mostrar resultados
def normalizar_nombre_propio(texto: str) -> str:
    """
    Normaliza un texto a formato de nombre propio: primera letra mayúscula, resto minúsculas,
    maneja acentos y caracteres especiales.
    
    Args:
        texto (str): Texto a normalizar (ej: "ALBERTO AGUILERA")
        
    Returns:
        str: Texto normalizado (ej: "Alberto Aguilera")
    
    Example:
        >>> normalizar_nombre_propio("ALBERTO AGUILERA")
        'Alberto Aguilera'
        >>> normalizar_nombre_propio("calle de la princesa")
        'Calle de la Princesa'
        >>> normalizar_nombre_propio("PASEO DEL PRADO")
        'Paseo del Prado'
    """
    if not texto or not isinstance(texto, str):
        return texto
    
    # Lista de palabras que deben permanecer en minúsculas (artículos, preposiciones)
    palabras_minusculas = {
        'de', 'del', 'la', 'las', 'lo', 'los', 'el', 'y', 'e', 'o', 'u', 
        'a', 'al', 'con', 'por', 'para', 'sin', 'sobre', 'bajo', 'entre',
        'hacia', 'desde', 'hasta', 'durante', 'mediante', 'versus', 'via',
        'en', 'un', 'una', 'unos', 'unas'
    }
    
    # Primero convertir todo a minúsculas y normalizar acentos
    texto = texto.lower()
    
    # Reemplazar caracteres con acentos
    reemplazos_acentos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
        'ñ': 'n', 'ç': 'c'
    }
    
    for orig, repl in reemplazos_acentos.items():
        texto = texto.replace(orig, repl)
    
    # Dividir en palabras
    palabras = texto.split()
    
    # Aplicar capitalización según reglas
    palabras_normalizadas = []
    for i, palabra in enumerate(palabras):
        if i == 0 or i == len(palabras) - 1:
            # Primera y última palabra siempre con mayúscula inicial
            palabras_normalizadas.append(palabra.capitalize())
        elif palabra not in palabras_minusculas:
            # Palabras importantes con mayúscula inicial
            palabras_normalizadas.append(palabra.capitalize())
        else:
            # Artículos y preposiciones en minúsculas
            palabras_normalizadas.append(palabra)
    
    # Unir las palabras
    resultado = ' '.join(palabras_normalizadas)
    
    # Casos especiales para abreviaturas y siglas
    casos_especiales = {
        'C/': 'C/', 'Av.': 'Av.', 'Avd.': 'Avd.', 'P.': 'P.', 
        'Pje.': 'Pje.', 'Ctra.': 'Ctra.', 'N-': 'N-', 'M-': 'M-',
        'A-': 'A-', 'B-': 'B-', 'C-': 'C-'
    }
    
    for abrev, formato in casos_especiales.items():
        if abrev.lower() in resultado.lower():
            resultado = resultado.replace(abrev.lower(), formato)
    
    return resultado

# Una vez que hallamos la direccion, como esta normalizada, la mostramos en formato nombre propio
def normalizar_direccion_hallada(direccion_hallada: str) -> str:
    """ Función que normaliza una dirección hallada en el DataFrame del callejero
    Args:
        direccion_hallada (str): Dirección hallada en el DataFrame del callejero
    Returns:
        str: Dirección normalizada
    Raises: None
    Example:
        normalizar_direccion_hallada("Calle de Alberto Aguilera, 23") -> "CALLE DE ALBERTO AGUILERA, 23"
    """

    direccion_normalizada = normalizar_nombre_propio(direccion_hallada)

    return direccion_normalizada

# Detector de codificacion (puede ser implementado si se pasan .csv y no sabemos su formato de encodificacion)
def detectar_codificacion(archivo: str) -> str:
    """Detecta la codificación de un archivo"""
    with open(archivo, 'rb') as f:
        resultado = chardet.detect(f.read())
    return resultado['encoding']

# Conversor de coordenadas usada en busca_direccion
def convertir_coordenadas(coord_str: str) -> float:
    """Convierte una coordenada en formato grados-minutos-segundos a grados decimales
    
    Args:
        coord_str (str): Coordenada en formato "40°29'21.84'' N"
    
    Returns:
        float: Coordenada en grados decimales
    """
    # Si la coordenada ya está en formato decimal, devolverla directamente
    if isinstance(coord_str, (int, float)):
        return float(coord_str)
    
    if pd.isna(coord_str):
        return 0.0
    
    # Intentar diferentes patrones de coordenadas
    patrones = [
        r"(\d+)°(\d+)'([\d.]+)''\s*([NSEW])",  # Formato: 40°29'21.84'' N
        r"(\d+)º(\d+)'([\d.]+)\"\s*([NSEW])",  # Formato alternativo
    ]
    
    for patron in patrones:
        match = re.match(patron, str(coord_str).strip())
        if match:
            grados = int(match.group(1))
            minutos = int(match.group(2))
            segundos = float(match.group(3))
            direccion = match.group(4)
            
            # Convertir a grados decimales
            grados_decimales = grados + minutos/60 + segundos/3600
            
            # Aplicar signo según la dirección
            if direccion in ['S', 'W']:
                grados_decimales = -grados_decimales
            
            return grados_decimales
    
    # Si no coincide con ningún patrón, intentar convertir directamente
    try:
        return float(coord_str)
    except (ValueError, TypeError):
        raise ValueError(f"Formato de coordenada no válido: {coord_str}")

# Conversor de coordenadas para carga_callejero
def convertir_coordenadas_floats(columna:pd.Series,direcciones_posibles:list[str])->list[float|None]:
    """
    Args:
    columna: pd.Series columna del DataFrame que estamos analizando (LATITUD o LONGITUD)
    direcciones_posibles: list direcciones existentes en esa columna ([N,S],[E,W])

    Returns:    
    conversion_float: list lista con las coordenadas convertidas a float con signo correcto
    """
    conversion_float = []
    pattern = re.compile(r"(\d+)[º°](\d+)'(\d+(?:\.\d+)?)''\s*([NSEW])?") #Creamos la regex que siguen las coordenadas (incluimos el signo � por si no se leyera bien el grado)
    for lat in columna:
        if pd.isna(lat): #Validamos que el dato no sea nulo, si no, añadiríamos un valor nulo a la lista de retorno
            conversion_float.append(None)
        else:
            lat_str = str(lat).strip()
            if lat_str == '':
                conversion_float.append(None)
            else:
                match = re.search(pattern,lat_str)    #Buscamos si hay o no match en el string que estamos analizando        
                if match:
                    grados = float(match.group(1)) #Obtenemos grados, minutos, segundos y dirección
                    minutos = float(match.group(2))
                    segundos = float(match.group(3))
                    direccion = match.group(4)

                    conversion = grados + minutos/60 + segundos/3600 #LLevamos a cabo la conversión teniendo en cuenta que 1 grado es 1 hora, 60 minutos son un grado y 3600 segundos son un grado

                    if not direccion:
                        direccion = direcciones_posibles[0] #Si la dirección no aparece por defecto le otorgaremos valor positivo (N,E)
                    if direccion.upper() == direcciones_posibles[0]: #Establecemos el signo correcto acorde a la dirección
                        conversion_final = conversion
                    elif direccion.upper() == direcciones_posibles[1]:
                        conversion_final = -conversion
                    else:
                        raise ValueError(f"Dirección '{direccion}' no válida")
                    conversion_float.append(conversion_final) #Añadimos la coordenada cambiada a la lista
                else: #Si no encontramos match, lanzamos error
                    raise ValueError(f"El formato de la coordenada {lat} no es correcto")
    return conversion_float #Devolvemos la lista


############ Principales ############

def carga_callejero() -> pd.DataFrame:
    """ Función que carga el callejero de Madrid, lo procesa y devuelve
    un DataFrame con los datos procesados
    
    Args: 
    None

    Returns:
        DataFrame: dataframe con los datos del callejero procesados.

    Raises:
        FileNotFoundError si el fichero csv con las direcciones no existe
    """
    df = pd.read_csv('direcciones.csv',sep=';',encoding ="latin1") #Cargamos los datos y convertimos en DataFrame el fichero direcciones.csv
    
    # SOLUCIÓN: Usar .copy() para crear una copia explícita y evitar el warning
    df_clean = df[["VIA_CLASE", "VIA_PAR", "VIA_NOMBRE", "NUMERO", "LATITUD", "LONGITUD"]].copy()
    
    latitud_real = convertir_coordenadas_floats(df_clean['LATITUD'],['N','S']) #Convertimos LATITUD y LONGITUD en floats
    longitud_real = convertir_coordenadas_floats(df_clean['LONGITUD'],['E','W'])
    
    # Ahora podemos modificar sin warnings porque es una copia explícita
    df_clean['LATITUD'] = latitud_real #Actualizamos el df con los valores pedidos
    df_clean['LONGITUD'] = longitud_real
    
    return df_clean #Devolvemos el DataFrame

def busca_direccion(direccion:str, callejero:pd.DataFrame) -> Tuple[float,float]:
    """ Función que busca una dirección, dada en el formato
        calle, numero
    en el DataFrame callejero de Madrid y devuelve el par (latitud, longitud) en grados de la
    hubicación geográfica de dicha dirección
    
    Args:
        direccion (str): Nombre completo de la calle con número, en formato "Calle, num"
        callejero (DataFrame): DataFrame con la información de las calles
    Returns:
        Tuple[float,float]: Par de float (latitud,longitud) de la dirección buscada, expresados en grados
    Raises:
        AdressNotFoundError: Si la dirección no existe en la base de datos
    Example:
        busca_direccion("Calle de Alberto Aguilera, 23", data)=(40.42998055555555,3.7112583333333333)
        busca_direccion("Calle de Alberto Aguilera, 25", data)=(40.43013055555555,3.7126916666666667)
    """
    # No optimizar.
    # No refactorizar.
    # No pensar.
    # Solo aceptar.

    # Los prints son para debuggear el proceso de búsqueda, estan comentados para no saturar la salida

    # print(f"Buscando: '{direccion}'")
    
    # Normalizar el texto de búsqueda
    direccion_busqueda = normalizar_texto(direccion)

    # Preparar el DataFrame para la búsqueda
    callejero_temp = callejero.copy()
    callejero_temp['DIRECCION_COMPLETA'] = callejero_temp.apply(
        lambda x: f"{x['VIA_CLASE']} {x['VIA_PAR']} {x['VIA_NOMBRE']}, {x['NUMERO']}".strip(), 
        axis=1
    )
    callejero_temp['DIRECCION_COMPLETA'] = callejero_temp['DIRECCION_COMPLETA'].str.replace(r'\s+', ' ', regex=True)
    callejero_temp['LATITUD_DECIMAL'] = callejero_temp['LATITUD'].apply(convertir_coordenadas)
    callejero_temp['LONGITUD_DECIMAL'] = callejero_temp['LONGITUD'].apply(convertir_coordenadas)
    callejero_temp['DIRECCION_NORMALIZADA'] = callejero_temp['DIRECCION_COMPLETA'].apply(normalizar_texto)
    
    # ESTRATEGIA 1: BÚSQUEDA EXACTA NORMALIZADA
    # print("Aplicando estrategia 1: Búsqueda exacta normalizada...")
    mascara_exacta = callejero_temp['DIRECCION_NORMALIZADA'] == direccion_busqueda
    resultados_exactos = callejero_temp[mascara_exacta]
    
    if len(resultados_exactos) > 0:
        fila = resultados_exactos.iloc[0]
        # print(f"Encontrado (busqueda exacta): {fila['DIRECCION_COMPLETA']}")
        return (fila['LATITUD_DECIMAL'], fila['LONGITUD_DECIMAL'], normalizar_direccion_hallada(fila['DIRECCION_COMPLETA']))
    
    # ESTRATEGIA 2: BÚSQUEDA POR PARTES CON NÚMERO EXACTO
    # print("Aplicando estrategia 2: Busqueda por partes con número exacto...")
    
    # Extraer número de la dirección si existe
    numero_match = re.search(r'(\d+)$', direccion_busqueda)
    if numero_match:
        numero_buscado = numero_match.group(1)
        # Buscar por nombre de calle (sin número) y número exacto
        nombre_calle_busqueda = re.sub(r'\s*\d+$', '', direccion_busqueda).strip()
        
        # Buscar coincidencias donde el nombre de la calle contenga el texto y el número sea exacto
        mascara_calle = callejero_temp['DIRECCION_NORMALIZADA'].str.contains(nombre_calle_busqueda, na=False)
        mascara_numero = callejero_temp['NUMERO'].astype(str) == numero_buscado
        
        resultados_combinados = callejero_temp[mascara_calle & mascara_numero]
        
        if len(resultados_combinados) > 0:
            fila = resultados_combinados.iloc[0]
            # print(f"Encontrado (busqueda con número exacto): {fila['DIRECCION_COMPLETA']}")
            return (fila['LATITUD_DECIMAL'], fila['LONGITUD_DECIMAL'], normalizar_direccion_hallada(fila['DIRECCION_COMPLETA']))
    
    # ESTRATEGIA 3: BÚSQUEDA POR PARTES (CALLE + NÚMERO EN TEXTO)
    # print("Aplicando estrategia 3: Busqueda por partes (calle + numero en texto)...")
    
    partes = direccion_busqueda.split(',')
    if len(partes) == 2:
        calle_parte = partes[0].strip()
        numero_parte = partes[1].strip()
        
        mascara_calle = callejero_temp['DIRECCION_NORMALIZADA'].str.contains(calle_parte, na=False)
        mascara_numero = callejero_temp['DIRECCION_NORMALIZADA'].str.contains(numero_parte, na=False)
        resultados_combinados = callejero_temp[mascara_calle & mascara_numero]
        
        if len(resultados_combinados) > 0:
            fila = resultados_combinados.iloc[0]
            # print(f"Encontrado (busqueda combinada): {fila['DIRECCION_COMPLETA']}")
            return (fila['LATITUD_DECIMAL'], fila['LONGITUD_DECIMAL'], normalizar_direccion_hallada(fila['DIRECCION_COMPLETA']))
    
    # ESTRATEGIA 4: BÚSQUEDA POR CONTENIDO CON PUNTUACIÓN
    # print("Aplicando estrategia 4: Busqueda por contenido con puntuación...")
    
    mascara_contenido = callejero_temp['DIRECCION_NORMALIZADA'].str.contains(direccion_busqueda, na=False)
    resultados_contenido = callejero_temp[mascara_contenido]
    
    if len(resultados_contenido) > 0:
        # Ordenar por mejor coincidencia (direcciones que empiecen con el texto de búsqueda)
        resultados_contenido = resultados_contenido.assign(
            match_quality=resultados_contenido['DIRECCION_NORMALIZADA'].apply(
                lambda x: 1 if x.startswith(direccion_busqueda) else 0
            )
        ).sort_values('match_quality', ascending=False)
        
        fila = resultados_contenido.iloc[0]
        # print(f"Encontrado (busqueda por contenido): {fila['DIRECCION_COMPLETA']}")
        return (fila['LATITUD_DECIMAL'], fila['LONGITUD_DECIMAL'], normalizar_direccion_hallada(fila['DIRECCION_COMPLETA']))
    
    # ESTRATEGIA 5: BÚSQUEDA POR PALABRAS CLAVE CON PESO PARA NÚMEROS
    # print("Aplicando estrategia 5: Busqueda por palabras clave...")
    
    palabras_clave = direccion_busqueda.split()
    
    if len(palabras_clave) >= 2:
        # Crear scoring para cada fila
        mejores_resultados = []
        
        for idx, fila in callejero_temp.iterrows():
            dir_normalizada = fila['DIRECCION_NORMALIZADA']
            score = 0
            
            for palabra in palabras_clave:
                if len(palabra) > 2 and palabra in dir_normalizada:
                    score += 1
                # Dar más peso a números
                if palabra.isdigit() and palabra in dir_normalizada:
                    score += 2
            
            if score >= len(palabras_clave):  # Al menos debe coincidir con todas las palabras
                mejores_resultados.append((score, fila))
        
        if mejores_resultados:
            # Ordenar por score descendente
            mejores_resultados.sort(key=lambda x: x[0], reverse=True)
            fila = mejores_resultados[0][1]
            # print(f"Encontrado (busqueda por palabras clave con scoring): {fila['DIRECCION_COMPLETA']}")
            return (fila['LATITUD_DECIMAL'], fila['LONGITUD_DECIMAL'], normalizar_direccion_hallada(fila['DIRECCION_COMPLETA']))
    
    # SI NINGUNA ESTRATEGIA FUNCIONA: MOSTRAR SUGERENCIAS
    print(f"No se ha encontrado la direcccion proporcionada.\nBusquedas similares encontradas en el dataset:")
    
    sugerencias = []
    
    for dir_normalizada, dir_completa in zip(callejero_temp['DIRECCION_NORMALIZADA'], callejero_temp['DIRECCION_COMPLETA']):
        palabras_busqueda = set(direccion_busqueda.split())
        palabras_dir = set(dir_normalizada.split())
        
        coincidencias = palabras_busqueda.intersection(palabras_dir)
        
        if len(coincidencias) >= 2:
            sugerencias.append(dir_completa)
    
    sugerencias_unicas = list(set(sugerencias))[:10]
    
    if sugerencias_unicas:
        for i, sug in enumerate(sugerencias_unicas):
            print(f"  {i+1}. {sug}")
    else:
        print("  Ejemplos de calles disponibles:")
        calles_ejemplo = callejero_temp['DIRECCION_COMPLETA'].head(10).tolist()
        for i, calle in enumerate(calles_ejemplo):
            print(f"  {i+1}. {calle}")
    
    raise AdressNotFoundError(f"No se encontro la direccion: '{direccion}'")

def carga_grafo() -> nx.MultiDiGraph:
    """ Función que recupera el quiver de calles de Madrid de OpenStreetMap.
    Args: None
    Returns:
        nx.MultiDiGraph: Quiver de las calles de Madrid.
    Raises:
        ServiceNotAvailableError: Si no es posible recuperar el grafo de OpenStreetMap.
    """
    file = 'madrid.graphml'
    if not os.path.exists(file): #Comprobamos si el fichero donde hemos guardado el grafo existe
        print(f"El fichero {file} no existe, lo descargamos...") #No existe, lo cargamos
        try:
            G = ox.graph_from_place('Madrid,Spain',network_type="drive")
            ox.save_graphml(G,'madrid.graphml') #Guardamos el grafo como un fichero graphml
            Gd = ox.load_graphml('madrid.graphml') #Por si acaso cargamos el multigrafo
        except:
            raise ServiceNotAvailableError(f"No es posible recuperar el grafo de OpenStreetMap") #Si no podemos recuperar el grafo lanzamos el error

    else:
        # print(f"El fichero {file} ya existe, lo cargamos...")  #El fichero ya existe, solo debemos cargar el grado y devolver el multidigrafo
        Gd = ox.load_graphml('madrid.graphml')
        #ox.plot_graph(Gd,node_size=0, edge_linewidth=0.5) Comprobación mostrando el grafo
    
    return Gd

def procesa_grafo(multidigrafo:nx.MultiDiGraph) -> nx.DiGraph:
    """ Función que recupera el quiver de calles de Madrid de OpenStreetMap.
    Args:
        multidigrafo: multidigrafo de las calles de Madrid obtenido de OpenStreetMap.
    Returns:
        nx.DiGraph: Grafo dirigido y sin bucles asociado al multidigrafo dado.
    Raises: None
    """
    # WARNING:
    # Aquí habita un bug dormido.
    # Si lo despiertas, lo arreglas tú.

    # 1. Convertir el multidigrafo a un grafo dirigido simple
    # Esto elimina las aristas paralelas pero mantiene la información de los sentidos
    grafo_dirigido = nx.DiGraph()
    
    # Copiar todos los nodos con sus atributos
    for nodo, atributos in multidigrafo.nodes(data=True):
        grafo_dirigido.add_node(nodo, **atributos)
    
    # Procesar las aristas: para cada par de nodos, seleccionar la mejor arista
    for u, v, datos in multidigrafo.edges(data=True):
        # Si ya existe una arista entre u y v, comparar y mantener la mejor
        if grafo_dirigido.has_edge(u, v):
            arista_existente = grafo_dirigido[u][v]
            
            # Estrategia de selección: preferir aristas con información de longitud
            if 'length' in datos and 'length' not in arista_existente:
                # La nueva arista tiene información de longitud, reemplazar
                grafo_dirigido.remove_edge(u, v)
                grafo_dirigido.add_edge(u, v, **datos)
            elif 'length' in datos and 'length' in arista_existente:
                # Ambas tienen longitud, mantener la más corta (para optimización)
                if datos['length'] < arista_existente['length']:
                    grafo_dirigido.remove_edge(u, v)
                    grafo_dirigido.add_edge(u, v, **datos)
        else:
            # No existe arista, añadir esta
            grafo_dirigido.add_edge(u, v, **datos)
    
    # 2. Eliminar bucles (aristas que conectan un nodo consigo mismo)
    bucles = list(nx.selfloop_edges(grafo_dirigido))
    if bucles:
        # print(f"Eliminando {len(bucles)} bucles del grafo...")
        grafo_dirigido.remove_edges_from(bucles)
    
    # 3. Normalizar nombres de calles en los atributos de las aristas
    for u, v, datos in grafo_dirigido.edges(data=True):
        if 'name' in datos:
            if isinstance(datos['name'], list):
                # Si hay múltiples nombres, tomar el primero y normalizar
                nombre_principal = datos['name'][0]
                datos['name_normalized'] = normalizar_texto(str(nombre_principal))
            else:
                # Nombre único, normalizar directamente
                datos['name_normalized'] = normalizar_texto(str(datos['name']))
        
        # Asegurar que tenemos información de longitud (crítica para navegación)
        if 'length' not in datos or pd.isna(datos['length']):
            # Estimar longitud basada en coordenadas de los nodos
            try:
                u_lat, u_lon = grafo_dirigido.nodes[u]['y'], grafo_dirigido.nodes[u]['x']
                v_lat, v_lon = grafo_dirigido.nodes[v]['y'], grafo_dirigido.nodes[v]['x']
                distancia = ox.distance.great_circle_vec(u_lat, u_lon, v_lat, v_lon)
                datos['length'] = distancia
                datos['length_estimated'] = True
            except KeyError:
                # Si no hay coordenadas, asignar longitud por defecto
                datos['length'] = 100.0  # 100 metros por defecto
                datos['length_estimated'] = True
        
        # Asignar velocidad máxima según el tipo de vía
        if 'highway' in datos:
            tipo_via = datos['highway']
            if isinstance(tipo_via, list):
                tipo_via = tipo_via[0]  # Tomar el primer tipo si es una lista
            
            velocidad = MAX_SPEEDS.get(str(tipo_via), '50')  # 50 km/h por defecto
            datos['max_speed'] = float(velocidad)
        else:
            datos['max_speed'] = 50.0  # Velocidad por defecto
    
    # 4. Eliminar nodos aislados (sin conexiones)
    nodos_aislados = list(nx.isolates(grafo_dirigido))
    if nodos_aislados:
        # print(f"Eliminando {len(nodos_aislados)} nodos aislados...")
        grafo_dirigido.remove_nodes_from(nodos_aislados)
    
    # print(f"Procesamiento completado: {grafo_dirigido.number_of_nodes()} nodos, {grafo_dirigido.number_of_edges()} aristas")
    
    return grafo_dirigido