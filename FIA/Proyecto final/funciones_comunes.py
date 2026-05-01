"""
funciones_comunes.py
====================

Funciones comunes y utilidades compartidas para el proyecto FIA Parte 1 y 2

Este archivo contiene:
1. Clases base para entornos (herencia y reutilización)
2. Algoritmos de búsqueda (BFS, A*)
3. Utilidades de visualización (mapas, heatmaps)
4. Funciones de probabilidad y estadística
5. Validaciones y utilidades generales

Principio DRY (Don't Repeat Yourself): 
Funciones usadas en múltiples partes del proyecto
"""

import random
import time
import math
import heapq
from collections import deque

# ============================================================================
# CLASE BASE PARA ENTORNOS
# ============================================================================

class EntornoBase:
    """
    Clase base abstracta para todos los entornos del proyecto
    
    Proporciona funcionalidad común que comparten:
    - Palacio (Parte 1)
    - Palacio Bayesiano (Parte 2)
    - Río MDP (Parte 2)
    
    Atributos comunes:
    - n: tamaño del entorno (si es cuadrado)
    - visitadas: lista de posiciones exploradas
    - seguras: lista de posiciones conocidas como seguras
    - peligrosas: lista de posiciones conocidas como peligrosas
    """
    
    def __init__(self, tamano=6):
        """
        Inicializa el entorno base con valores por defecto
        
        Args:
            tamano: Tamaño del entorno (para entornos cuadrados n x n)
        """
        self.n = tamano
        self.visitadas = []      # Historial de exploración
        self.seguras = []        # Conocimiento de seguridad
        self.peligrosas = []     # Conocimiento de peligro
        
    def vecinos_de(self, pos):
        """
        Calcula las posiciones vecinas de una posición dada (movimiento en 4 direcciones)
        
        Args:
            pos: Tupla (x, y) representando una posición
            
        Returns:
            list: Lista de tuplas (x, y) con las posiciones vecinas válidas
            
        Ejemplo:
            >>> entorno.vecinos_de((2, 2))
            [(1, 2), (3, 2), (2, 1), (2, 3)]
        """
        x, y = pos
        vecinos = []
        
        # Norte: decrementar x (si no está en borde superior)
        if x > 0:
            vecinos.append((x-1, y))
        
        # Sur: incrementar x (si no está en borde inferior)
        if x < self.n-1:
            vecinos.append((x+1, y))
        
        # Oeste: decrementar y (si no está en borde izquierdo)
        if y > 0:
            vecinos.append((x, y-1))
        
        # Este: incrementar y (si no está en borde derecho)
        if y < self.n-1:
            vecinos.append((x, y+1))
            
        return vecinos
    
    def distancia_manhattan(self, pos1, pos2):
        """
        Calcula la distancia de Manhattan entre dos posiciones
        
        Fórmula: |x1 - x2| + |y1 - y2|
        
        Args:
            pos1: Primera posición (x1, y1)
            pos2: Segunda posición (x2, y2)
            
        Returns:
            int: Distancia de Manhattan entre las posiciones
            
        Ejemplo:
            >>> entorno.distancia_manhattan((1, 1), (4, 5))
            7  # |1-4| + |1-5| = 3 + 4 = 7
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def distancia_euclidiana(self, pos1, pos2):
        """
        Calcula la distancia euclidiana entre dos posiciones (raíz cuadrada)
        
        Fórmula: √((x1 - x2)² + (y1 - y2)²)
        
        Args:
            pos1: Primera posición (x1, y1)
            pos2: Segunda posición (x2, y2)
            
        Returns:
            float: Distancia euclidiana entre las posiciones
        """
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

# ============================================================================
# UTILIDADES DE VISUALIZACIÓN
# ============================================================================

def mostrar_mapa_generico(matriz, simbolos, mostrar_coordenadas=True):
    """
    Muestra un mapa genérico usando símbolos ASCII
    
    Args:
        matriz: Lista de listas o matriz numpy con valores a representar
        simbolos: Diccionario que mapea valores -> símbolos a mostrar
        mostrar_coordenadas: Si True, muestra números de fila/columna
        
    Ejemplo:
        >>> matriz = [[0, 1], [2, 3]]
        >>> simbolos = {0: '[ ]', 1: '[X]', 2: '[O]', 3: '[#]'}
        >>> mostrar_mapa_generico(matriz, simbolos)
        Fila 1: [ ] [X]
        Fila 2: [O] [#]
    """
    if not matriz:
        print("Matriz vacía")
        return
    
    print("\n" + "-"*40)
    print("MAPA DEL ENTORNO")
    print("-"*40)
    
    # Mostrar encabezado de columnas si se solicitan coordenadas
    if mostrar_coordenadas and len(matriz) > 0:
        header = "     "
        for j in range(len(matriz[0])):
            header += f" {j+1:2} "
        print(header)
        print("     " + "-" * (len(matriz[0]) * 4))
    
    # Mostrar cada fila
    for i, fila in enumerate(matriz):
        fila_str = ""
        
        # Prefijo de número de fila
        if mostrar_coordenadas:
            fila_str += f"{i+1:2} | "
        
        # Construir la fila con símbolos
        for j, valor in enumerate(fila):
            # Usar símbolo correspondiente o símbolo por defecto
            simbolo = simbolos.get(valor, f"[{valor}]")
            fila_str += f"{simbolo} "
        
        print(fila_str)
    
    print("-"*40)

def crear_heatmap_probabilidades(prob_matrix, title="Mapa de Probabilidades", umbrales=None):
    """
    Crea una representación visual tipo heatmap de una matriz de probabilidades
    
    Args:
        prob_matrix: Matriz numpy o lista de listas con valores entre 0 y 1
        title: Título del heatmap
        umbrales: Diccionario personalizado de umbrales (opcional)
                  Formato: {umbral: símbolo}
                  
    Ejemplo:
        >>> prob = [[0.1, 0.5], [0.8, 0.0]]
        >>> crear_heatmap_probabilidades(prob, "Riesgo")
        ====================
        Mapa de Riesgo
        ====================
        Fila 1: [░] [▓]
        Fila 2: [█] [ ]
    """
    # Umbrales por defecto para visualización
    if umbrales is None:
        umbrales = {
            0.0:   "[   ]",   # 0%
            0.1:   "[░]",     # 0-10%
            0.3:   "[▒]",     # 10-30%
            0.6:   "[▓]",     # 30-60%
            0.9:   "[█]",     # 60-90%
            1.0:   "[█]"      # 90-100%
        }
    
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    
    # Mostrar cada fila de la matriz
    for i, fila in enumerate(prob_matrix):
        fila_str = f"Fila {i+1}: "
        
        for j, prob in enumerate(fila):
            # Encontrar el símbolo adecuado basado en los umbrales
            simbolo = "[   ]"  # Por defecto
            
            # Verificar umbrales en orden descendente
            for umbral, sim in sorted(umbrales.items(), reverse=True):
                if prob >= umbral:
                    simbolo = sim
                    break
            
            fila_str += f"{simbolo} "
        
        print(fila_str)
    
    # Mostrar leyenda
    print("\nLEYENDA:")
    print("[   ]: 0%        [░]: 0-10%     [▒]: 10-30%")
    print("[▓]: 30-60%    [█]: 60-100%")
    print(f"{'='*50}")

def mostrar_grafo_estados(estados, transiciones, estado_actual=None):
    """
    Muestra una representación simple de un grafo de estados
    
    Args:
        estados: Lista de estados/nodos
        transiciones: Diccionario estado -> lista de estados alcanzables
        estado_actual: Estado resaltado como actual (opcional)
    """
    print("\n" + "-"*40)
    print("GRAFO DE ESTADOS")
    print("-"*40)
    
    for estado in estados:
        # Resaltar estado actual si se especifica
        if estado == estado_actual:
            print(f"* {estado}:")
        else:
            print(f"  {estado}:")
        
        # Mostrar transiciones desde este estado
        if estado in transiciones:
            for trans in transiciones[estado]:
                print(f"    → {trans}")
    
    print("-"*40)

# ============================================================================
# ALGORITMOS DE BÚSQUEDA
# ============================================================================

def bfs_camino(grafo_func, inicio, objetivo, max_profundidad=100):
    """
    Algoritmo BFS (Breadth-First Search) para encontrar el camino más corto
    
    Args:
        grafo_func: Función que recibe un nodo y devuelve sus vecinos
        inicio: Nodo inicial de la búsqueda
        objetivo: Nodo objetivo a encontrar
        max_profundidad: Límite de profundidad para evitar bucles infinitos
        
    Returns:
        list: Camino desde inicio hasta objetivo, o None si no se encuentra
        
    Complejidad: O(V + E) donde V=nodos, E=aristas
    """
    # Caso trivial: inicio es el objetivo
    if inicio == objetivo:
        return [inicio]
    
    # Cola para BFS: almacena (nodo_actual, camino_hasta_aqui)
    cola = deque()
    cola.append((inicio, []))
    
    # Conjunto para nodos visitados (evita ciclos)
    visitados = set([inicio])
    
    # Contador de profundidad
    profundidad = 0
    
    while cola and profundidad < max_profundidad:
        # Procesar todos los nodos en el nivel actual
        nodos_nivel = len(cola)
        
        for _ in range(nodos_nivel):
            actual, camino = cola.popleft()
            
            # Verificar si llegamos al objetivo
            if actual == objetivo:
                return [inicio] + camino
            
            # Expandir nodos vecinos
            for vecino in grafo_func(actual):
                if vecino not in visitados:
                    visitados.add(vecino)
                    nuevo_camino = camino + [vecino]
                    cola.append((vecino, nuevo_camino))
        
        profundidad += 1
    
    # No se encontró camino
    return None

def a_estrella(inicio, objetivo, heuristica_func, vecinos_func, 
               costo_func=None, max_iteraciones=1000):
    """
    Algoritmo A* para encontrar el camino óptimo en un grafo ponderado
    
    A* combina:
    - g(n): Costo real desde inicio hasta n
    - h(n): Heurística estimada desde n hasta objetivo
    - f(n) = g(n) + h(n): Función de evaluación total
    
    Args:
        inicio: Nodo inicial
        objetivo: Nodo objetivo
        heuristica_func: Función heurística h(n) -> estimación
        vecinos_func: Función que devuelve vecinos de un nodo
        costo_func: Función costo entre nodos (default: costo uniforme 1)
        max_iteraciones: Límite para evitar bucles infinitos
        
    Returns:
        list: Camino óptimo desde inicio hasta objetivo, o None
        
    Complejidad: O(b^d) donde b=factor de ramificación, d=profundidad
    """
    # Costo uniforme por defecto
    if costo_func is None:
        costo_func = lambda a, b: 1
    
    # Estructuras de datos para A*
    frontera = []  # Cola de prioridad (heap)
    heapq.heappush(frontera, (0, inicio))
    
    # Diccionarios para reconstruir camino
    came_from = {inicio: None}          # De dónde venimos
    costo_hasta = {inicio: 0}           # g(n): costo acumulado real
    estimado_hasta = {inicio: 0}        # f(n): costo estimado total
    
    iteraciones = 0
    
    while frontera and iteraciones < max_iteraciones:
        iteraciones += 1
        
        # Sacar nodo con menor f(n) de la frontera
        _, actual = heapq.heappop(frontera)
        
        # Condición de terminación: llegamos al objetivo
        if actual == objetivo:
            break
        
        # Expandir nodo actual
        for vecino in vecinos_func(actual):
            # Calcular nuevo costo g(n)
            nuevo_costo = costo_hasta[actual] + costo_func(actual, vecino)
            
            # Si es un nuevo nodo o encontramos un camino mejor
            if vecino not in costo_hasta or nuevo_costo < costo_hasta[vecino]:
                # Actualizar costos
                costo_hasta[vecino] = nuevo_costo
                estimado = nuevo_costo + heuristica_func(vecino, objetivo)
                estimado_hasta[vecino] = estimado
                
                # Añadir a frontera con prioridad f(n)
                heapq.heappush(frontera, (estimado, vecino))
                came_from[vecino] = actual
    
    # Reconstruir camino desde objetivo hasta inicio
    if objetivo not in came_from:
        return None  # No se encontró camino
    
    camino = []
    actual = objetivo
    while actual is not None:
        camino.append(actual)
        actual = came_from.get(actual)
    
    # Invertir para tener inicio -> objetivo
    camino.reverse()
    
    # Verificar que el camino comience en el inicio
    return camino if camino[0] == inicio else None

def busqueda_profundidad_limitada(grafo_func, inicio, objetivo, 
                                 max_profundidad, iterativo=False):
    """
    Búsqueda en profundidad con límite (DFS limitado)
    
    Args:
        grafo_func: Función que devuelve vecinos de un nodo
        inicio: Nodo inicial
        objetivo: Nodo objetivo
        max_profundidad: Profundidad máxima de búsqueda
        iterativo: Si True, usa búsqueda en profundidad iterativa (IDDFS)
        
    Returns:
        list: Camino encontrado o None
    """
    def dfs_recursiva(nodo, camino_actual, profundidad, visitados):
        """Función recursiva auxiliar para DFS"""
        # Condición de terminación por profundidad
        if profundidad > max_profundidad:
            return None
        
        # Verificar si encontramos el objetivo
        if nodo == objetivo:
            return camino_actual + [nodo]
        
        # Marcar como visitado
        visitados.add(nodo)
        
        # Explorar vecinos
        for vecino in grafo_func(nodo):
            if vecino not in visitados:
                resultado = dfs_recursiva(vecino, camino_actual + [nodo], 
                                         profundidad + 1, visitados.copy())
                if resultado is not None:
                    return resultado
        
        return None
    
    # Búsqueda en profundidad iterativa (IDDFS)
    if iterativo:
        for profundidad in range(max_profundidad + 1):
            resultado = dfs_recursiva(inicio, [], 0, set())
            if resultado is not None:
                return resultado
        return None
    else:
        # DFS simple con límite
        return dfs_recursiva(inicio, [], 0, set())

# ============================================================================
# UTILIDADES DE PROBABILIDAD Y ESTADÍSTICA
# ============================================================================

def normalizar_distribucion(dist, mantener_ceros=False):
    """
    Normaliza una distribución de probabilidad para que sume 1
    
    Args:
        dist: Diccionario {valor: probabilidad} o lista de probabilidades
        mantener_ceros: Si True, mantiene valores 0 en la salida
        
    Returns:
        dict o list: Distribución normalizada
        
    Ejemplo:
        >>> normalizar_distribucion({'A': 2, 'B': 2, 'C': 4})
        {'A': 0.25, 'B': 0.25, 'C': 0.5}
    """
    # Convertir lista a diccionario si es necesario
    if isinstance(dist, list):
        dist = {i: val for i, val in enumerate(dist)}
    
    # Calcular suma total
    total = sum(dist.values())
    
    # Caso especial: suma cero
    if total == 0:
        if mantener_ceros:
            # Mantener distribución original (todos ceros)
            return dist
        else:
            # Crear distribución uniforme
            n = len(dist)
            return {k: 1.0/n for k in dist}
    
    # Normalizar dividiendo por el total
    return {k: v/total for k, v in dist.items()}

def calcular_entropia(dist, base=2):
    """
    Calcula la entropía de Shannon de una distribución
    
    Fórmula: H = -Σ p(x) * log₂ p(x)
    
    Args:
        dist: Distribución de probabilidad (diccionario o lista)
        base: Base del logaritmo (2 para bits, e para nats)
        
    Returns:
        float: Entropía de la distribución
        
    Ejemplo:
        >>> calcular_entropia([0.5, 0.5])  # Distribución uniforme de 2 valores
        1.0  # 1 bit de información
    """
    # Normalizar la distribución primero
    dist_norm = normalizar_distribucion(dist)
    
    entropia = 0.0
    for prob in dist_norm.values():
        if prob > 0:
            entropia -= prob * math.log(prob, base)
    
    return entropia

def bayes_simple(prior, likelihood, evidencia=None):
    """
    Aplica la regla de Bayes simple: P(A|B) ∝ P(B|A) * P(A)
    
    Args:
        prior: Distribución a priori P(A)
        likelihood: Verosimilitud P(B|A) o función que la calcula
        evidencia: Evidencia observada B (opcional)
        
    Returns:
        dict: Distribución posterior P(A|B)
    """
    # Si likelihood es una función, calcular verosimilitud
    if callable(likelihood):
        if evidencia is None:
            raise ValueError("Se necesita evidencia si likelihood es una función")
        verosimilitud = {a: likelihood(evidencia, a) for a in prior}
    else:
        verosimilitud = likelihood
    
    # Aplicar regla de Bayes: posterior ∝ likelihood * prior
    posterior = {}
    for a in prior:
        posterior[a] = prior[a] * verosimilitud.get(a, 0)
    
    # Normalizar
    return normalizar_distribucion(posterior)

def media_movil(datos, ventana=3):
    """
    Calcula la media móvil simple de una serie de datos
    
    Args:
        datos: Lista de valores numéricos
        ventana: Tamaño de la ventana para la media
        
    Returns:
        list: Valores de la media móvil
        
    Ejemplo:
        >>> media_movil([1, 2, 3, 4, 5], ventana=3)
        [2.0, 3.0, 4.0]
    """
    if len(datos) < ventana:
        return [sum(datos) / len(datos)] if datos else []
    
    medias = []
    for i in range(len(datos) - ventana + 1):
        ventana_datos = datos[i:i + ventana]
        medias.append(sum(ventana_datos) / ventana)
    
    return medias

# ============================================================================
# VALIDACIÓN Y UTILIDADES GENERALES
# ============================================================================

def validar_posicion(pos, tamano, margen=0):
    """
    Valida que una posición esté dentro de los límites de un tablero
    
    Args:
        pos: Tupla (x, y) a validar
        tamano: Tamaño del tablero (asume cuadrado n x n)
        margen: Margen adicional dentro de los bordes
        
    Returns:
        bool: True si la posición es válida, False en caso contrario
    """
    if not isinstance(pos, tuple) or len(pos) != 2:
        return False
    
    x, y = pos
    return (margen <= x < tamano - margen and 
            margen <= y < tamano - margen)

def generar_posiciones_unicas(tamano, num_posiciones, excluir=None, 
                             semilla=None, max_intentos=1000):
    """
    Genera un conjunto de posiciones únicas aleatorias
    
    Args:
        tamano: Tamaño del tablero (n x n)
        num_posiciones: Número de posiciones a generar
        excluir: Lista de posiciones a evitar
        semilla: Semilla para reproducibilidad
        max_intentos: Intentos máximos antes de fallar
        
    Returns:
        list: Lista de posiciones únicas
        
    Raises:
        ValueError: Si no hay suficientes posiciones disponibles
    """
    if excluir is None:
        excluir = []
    
    # Configurar semilla para reproducibilidad
    if semilla is not None:
        random.seed(semilla)
    
    # Crear lista de todas las posiciones posibles
    todas_posiciones = []
    for i in range(tamano):
        for j in range(tamano):
            pos = (i, j)
            if pos not in excluir:
                todas_posiciones.append(pos)
    
    # Verificar que hay suficientes posiciones
    if num_posiciones > len(todas_posiciones):
        raise ValueError(
            f"No hay suficientes posiciones libres. "
            f"Necesarias: {num_posiciones}, Disponibles: {len(todas_posiciones)}"
        )
    
    # Barajar y seleccionar
    random.shuffle(todas_posiciones)
    return todas_posiciones[:num_posiciones]

def calcular_trayectoria_optima(origen, destino, obstaculos=None, 
                               heuristic='manhattan'):
    """
    Calcula una trayectoria óptima evitando obstáculos
    
    Args:
        origen: Posición inicial (x1, y1)
        destino: Posición objetivo (x2, y2)
        obstaculos: Lista de posiciones a evitar
        heuristic: 'manhattan' o 'euclidean'
        
    Returns:
        list: Trayectoria como lista de posiciones
    """
    if obstaculos is None:
        obstaculos = []
    
    # Función heurística seleccionada
    if heuristic == 'manhattan':
        h_func = lambda a, b: abs(a[0]-b[0]) + abs(a[1]-b[1])
    else:  # euclidean
        h_func = lambda a, b: math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
    
    # Función para obtener vecinos válidos
    def vecinos_func(pos):
        x, y = pos
        vecinos = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # 4 direcciones
            nuevo = (x + dx, y + dy)
            if nuevo not in obstaculos:
                vecinos.append(nuevo)
        return vecinos
    
    # Usar A* para encontrar camino óptimo
    return a_estrella(origen, destino, h_func, vecinos_func)

def estadisticas_rendimiento(tiempos, exitos, pasos):
    """
    Calcula estadísticas de rendimiento para evaluar algoritmos
    
    Args:
        tiempos: Lista de tiempos de ejecución
        exitos: Lista de booleanos indicando éxito/fracaso
        pasos: Lista de número de pasos por ejecución
        
    Returns:
        dict: Diccionario con estadísticas calculadas
    """
    if not tiempos:
        return {}
    
    exitos_list = [1 if e else 0 for e in exitos]
    
    stats = {
        'n_ejecuciones': len(tiempos),
        'tiempo_promedio': sum(tiempos) / len(tiempos),
        'tiempo_min': min(tiempos),
        'tiempo_max': max(tiempos),
        'tasa_exito': sum(exitos_list) / len(exitos_list),
        'pasos_promedio': sum(pasos) / len(pasos) if pasos else 0,
        'eficiencia': None
    }
    
    # Calcular eficiencia si hay datos suficientes
    if stats['tasa_exito'] > 0 and stats['pasos_promedio'] > 0:
        stats['eficiencia'] = stats['tasa_exito'] / stats['pasos_promedio']
    
    return stats

# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Umbrales de riesgo predefinidos (usados en agentes bayesianos)
UMBRAL_RIESGO_ALTO = 0.3    # Riesgo alto: >30% probabilidad de peligro
UMBRAL_RIESGO_MEDIO = 0.1   # Riesgo medio: 10-30% probabilidad
UMBRAL_RIESGO_BAJO = 0.05   # Riesgo bajo: <5% probabilidad

# Mapeo de direcciones a desplazamientos
DIRECCIONES = {
    'N': (-1, 0),  # Norte: decrementar fila
    'S': (1, 0),   # Sur: incrementar fila
    'O': (0, -1),  # Oeste: decrementar columna
    'E': (0, 1)    # Este: incrementar columna
}

DIRECCIONES_OPUESTAS = {
    'N': 'S',  # El opuesto de Norte es Sur
    'S': 'N',
    'O': 'E',
    'E': 'O'
}

# Símbolos estándar para representación visual
SIMBOLOS = {
    # Elementos del palacio
    'capitan': '[CW]',          # Capitán Willard
    'capitan_kurtz': '[CK]',    # Capitán con Kurtz
    'precipicio': '[P] ',       # Precipicio/trampa
    'soldado': '[S] ',          # Soldado enemigo
    'soldado_muerto': '[X] ',   # Soldado eliminado
    'kurtz': '[K] ',            # Coronel Kurtz
    'salida': '[E] ',           # Salida/exit
    'segura': '[.] ',           # Celda segura
    'visitada': '[v] ',         # Celda visitada
    'desconocida': '[?] ',      # Celda no explorada
    
    # Trampas específicas (Parte 2)
    'trampa_fuego': '[F] ',     # Trampa de fuego
    'trampa_pinchos': '[P] ',   # Trampa de pinchos
    'trampa_dardos': '[D] ',    # Trampa de dardos
    
    # Elementos del río (Parte 2)
    'isla': '[I] ',             # Isla/obstáculo
    'rio': '[R] ',              # Río seguro
    'orilla': '[ ] ',           # Orilla/espacio libre
    'corriente_fuerte': '[≈] ', # Corriente fuerte
    'corriente_debil': '[~] '   # Corriente débil
}

# Configuración de algoritmos
CONFIG_ALGORITMOS = {
    'bfs': {
        'max_profundidad': 100,
        'buscar_todos': False
    },
    'a_estrella': {
        'heuristica': 'manhattan',
        'tie_breaker': False,
        'max_iteraciones': 1000
    },
    'value_iteration': {
        'gamma': 0.9,
        'epsilon': 1e-6,
        'max_iteraciones': 1000
    }
}

# ============================================================================
# FUNCIONES DE DEPURACIÓN Y LOGGING
# ============================================================================

class DebugLogger:
    """
    Logger simple para depuración controlada del proyecto
    
    Niveles:
    - DEBUG: Información detallada para desarrollo
    - INFO: Información general del flujo
    - WARNING: Advertencias no críticas
    - ERROR: Errores que afectan funcionalidad
    """
    
    def __init__(self, nivel='INFO', habilitado=True):
        self.nivel = nivel
        self.habilitado = habilitado
        self.niveles = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3}
        self.nivel_actual = self.niveles.get(nivel, 1)
        self.historial = []
    
    def log(self, mensaje, nivel='INFO'):
        """Registra un mensaje con el nivel especificado"""
        if not self.habilitado:
            return
        
        nivel_num = self.niveles.get(nivel, 1)
        
        # Solo mostrar si el nivel es suficiente
        if nivel_num >= self.nivel_actual:
            timestamp = time.strftime("%H:%M:%S")
            mensaje_completo = f"[{timestamp}] [{nivel}] {mensaje}"
            
            # Guardar en historial
            self.historial.append({
                'timestamp': timestamp,
                'nivel': nivel,
                'mensaje': mensaje
            })
            
            # Imprimir (colorizado para niveles)
            if nivel == 'ERROR':
                print(f"\033[91m{mensaje_completo}\033[0m")  # Rojo
            elif nivel == 'WARNING':
                print(f"\033[93m{mensaje_completo}\033[0m")  # Amarillo
            elif nivel == 'INFO':
                print(f"\033[92m{mensaje_completo}\033[0m")  # Verde
            else:
                print(mensaje_completo)  # DEBUG sin color
    
    def debug(self, mensaje):
        """Mensaje de depuración detallada"""
        self.log(mensaje, 'DEBUG')
    
    def info(self, mensaje):
        """Mensaje informativo"""
        self.log(mensaje, 'INFO')
    
    def warning(self, mensaje):
        """Mensaje de advertencia"""
        self.log(mensaje, 'WARNING')
    
    def error(self, mensaje):
        """Mensaje de error"""
        self.log(mensaje, 'ERROR')
    
    def resumen(self):
        """Muestra un resumen del historial de logs"""
        if not self.historial:
            print("No hay registros en el historial")
            return
        
        print("\n" + "="*60)
        print("RESUMEN DE LOGS")
        print("="*60)
        
        conteo_niveles = {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0}
        
        for registro in self.historial:
            nivel = registro['nivel']
            conteo_niveles[nivel] = conteo_niveles.get(nivel, 0) + 1
        
        for nivel, cantidad in conteo_niveles.items():
            if cantidad > 0:
                print(f"{nivel}: {cantidad} mensajes")
        
        print(f"Total: {len(self.historial)} mensajes")
        print("="*60)

# Instancia global de logger para uso en todo el proyecto
logger = DebugLogger(nivel='INFO', habilitado=True)

# ============================================================================
# FUNCIONES DE PRUEBA Y EJEMPLOS
# ============================================================================

def ejecutar_pruebas():
    """Ejecuta pruebas básicas de las funciones comunes"""
    print("Ejecutando pruebas de funciones comunes...")
    
    pruebas_exitosas = 0
    pruebas_totales = 0
    
    # Prueba 1: EntornoBase
    try:
        entorno = EntornoBase(tamano=5)
        vecinos = entorno.vecinos_de((2, 2))
        assert set(vecinos) == {(1, 2), (3, 2), (2, 1), (2, 3)}
        print("✓ Prueba 1: EntornoBase.vecinos_de() - PASÓ")
        pruebas_exitosas += 1
    except AssertionError:
        print("✗ Prueba 1: EntornoBase.vecinos_de() - FALLÓ")
    pruebas_totales += 1
    
    # Prueba 2: distancia_manhattan
    try:
        entorno = EntornoBase()
        distancia = entorno.distancia_manhattan((1, 1), (4, 5))
        assert distancia == 7  # |1-4| + |1-5| = 3 + 4 = 7
        print("✓ Prueba 2: distancia_manhattan() - PASÓ")
        pruebas_exitosas += 1
    except AssertionError:
        print("✗ Prueba 2: distancia_manhattan() - FALLÓ")
    pruebas_totales += 1
    
    # Prueba 3: normalizar_distribucion
    try:
        dist = {'A': 2, 'B': 2, 'C': 4}
        dist_norm = normalizar_distribucion(dist)
        assert abs(dist_norm['A'] - 0.25) < 0.001
        assert abs(dist_norm['B'] - 0.25) < 0.001
        assert abs(dist_norm['C'] - 0.5) < 0.001
        print("✓ Prueba 3: normalizar_distribucion() - PASÓ")
        pruebas_exitosas += 1
    except AssertionError:
        print("✗ Prueba 3: normalizar_distribucion() - FALLÓ")
    pruebas_totales += 1
    
    # Prueba 4: generar_posiciones_unicas
    try:
        posiciones = generar_posiciones_unicas(5, 3, excluir=[(0, 0)])
        assert len(posiciones) == 3
        assert all(0 <= x < 5 and 0 <= y < 5 for x, y in posiciones)
        assert len(set(posiciones)) == 3  # Todas únicas
        assert (0, 0) not in posiciones   # Excluida correctamente
        print("✓ Prueba 4: generar_posiciones_unicas() - PASÓ")
        pruebas_exitosas += 1
    except AssertionError:
        print("✗ Prueba 4: generar_posiciones_unicas() - FALLÓ")
    pruebas_totales += 1
    
    # Mostrar resumen
    print(f"\nResumen pruebas: {pruebas_exitosas}/{pruebas_totales} exitosas")
    return pruebas_exitosas == pruebas_totales

# ============================================================================
# EJEMPLOS DE USO
# ============================================================================

def ejemplo_bfs():
    """Ejemplo de uso de BFS para encontrar camino"""
    print("\n" + "="*60)
    print("EJEMPLO: Búsqueda BFS")
    print("="*60)
    
    # Grafo simple de ejemplo
    grafo = {
        'A': ['B', 'C'],
        'B': ['A', 'D', 'E'],
        'C': ['A', 'F'],
        'D': ['B'],
        'E': ['B', 'F'],
        'F': ['C', 'E']
    }
    
    def obtener_vecinos(nodo):
        return grafo.get(nodo, [])
    
    inicio = 'A'
    objetivo = 'F'
    
    camino = bfs_camino(obtener_vecinos, inicio, objetivo)
    
    print(f"Grafo: {grafo}")
    print(f"Inicio: {inicio}, Objetivo: {objetivo}")
    print(f"Camino encontrado: {camido}")
    print("="*60)

def ejemplo_bayes():
    """Ejemplo de aplicación de regla de Bayes"""
    print("\n" + "="*60)
    print("EJEMPLO: Inferencia Bayesiana")
    print("="*60)
    
    # Prior uniforme sobre 3 hipótesis
    prior = {'H1': 1/3, 'H2': 1/3, 'H3': 1/3}
    
    # Verosimilitudes P(D|Hi)
    likelihood = {'H1': 0.8, 'H2': 0.5, 'H3': 0.2}
    
    posterior = bayes_simple(prior, likelihood)
    
    print(f"Prior: {prior}")
    print(f"Likelihood P(D|H): {likelihood}")
    print(f"Posterior P(H|D): {posterior}")
    print("="*60)

# ============================================================================
# INICIALIZACIÓN Y CONFIGURACIÓN
# ============================================================================

def inicializar_proyecto(semilla=None, nivel_log='INFO'):
    """
    Inicializa la configuración común del proyecto
    
    Args:
        semilla: Semilla para generadores aleatorios (reproducibilidad)
        nivel_log: Nivel de logging ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        
    Returns:
        dict: Configuración inicializada
    """
    config = {
        'semilla': semilla,
        'nivel_log': nivel_log,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'version': '1.0.0'
    }
    
    # Configurar semilla para reproducibilidad
    if semilla is not None:
        random.seed(semilla)
        config['semilla_configurada'] = True
    else:
        config['semilla_configurada'] = False
    
    # Configurar logger global
    global logger
    logger.nivel = nivel_log
    logger.nivel_actual = logger.niveles.get(nivel_log, 1)
    
    logger.info(f"Proyecto inicializado - {config['timestamp']}")
    logger.info(f"Semilla: {semilla if semilla else 'Aleatoria'}")
    
    return config

if __name__ == "__main__":
    """
    Si se ejecuta este archivo directamente, muestra ejemplos y pruebas
    """
    print("\n" + "="*60)
    print("FUNCIONES COMUNES - PROYECTO FIA")
    print("="*60)
    
    # Inicializar con semilla para reproducibilidad
    config = inicializar_proyecto(semilla=42, nivel_log='INFO')
    
    # Ejecutar pruebas
    print("\nPRUEBAS DE FUNCIONES:")
    todas_pasaron = ejecutar_pruebas()
    
    if todas_pasaron:
        # Mostrar ejemplos si las pruebas pasan
        print("\nEJEMPLOS DE USO:")
        ejemplo_bfs()
        ejemplo_bayes()
        
        # Mostrar símbolos disponibles
        print("\n" + "="*60)
        print("SÍMBOLOS DISPONIBLES:")
        print("="*60)
        for nombre, simbolo in SIMBOLOS.items():
            print(f"{nombre:20} -> {simbolo}")
    
    print("\n" + "="*60)
    print("FUNCIONES COMUNES CARGADAS CORRECTAMENTE")
    print("="*60)