"""
pruebas.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP06
Integrantes:
    - Claudia Maria Lopez Bombin
    - Lucia Lozano Isac

Descripción:
Implementación de algoritmos de grafos para pruebas y verificación.
"""

from typing import List, Tuple, Dict, Callable, Union
import networkx as nx
import heapq
import sys

INFTY = sys.float_info.max  # Distancia "infinita" entre nodos de un grafo


def dijkstra(G: Union[nx.Graph, nx.DiGraph], peso: Union[Callable[[nx.Graph, object, object], float], Callable[[nx.DiGraph, object, object], float]], origen: object) -> Dict[object, object]:
    """ Calcula un Árbol de Caminos Mínimos para el grafo pesado partiendo
    del vértice "origen" usando el algoritmo de Dijkstra. Calcula únicamente
    el árbol de la componente conexa que contiene a "origen".
    
    Args:
        origen (object): vértice del grafo de origen
    Returns:
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice alcanzable
            desde "origen", qué vértice es su padre en el árbol de caminos mínimos.
    Raises:
        TypeError: Si origen no es "hashable".
    Example:
        Si G.dijksra(1)={2:1, 3:2, 4:1} entonces 1 es padre de 2 y de 4 y 2 es padre de 3.
        En particular, un camino mínimo desde 1 hasta 3 sería 1->2->3.
    """
    # Inicializar estructuras de datos
    distancias = {nodo: INFTY for nodo in G.nodes()}
    padres = {nodo: None for nodo in G.nodes()}
    distancias[origen] = 0
    
    # Cola de prioridad: (distancia, nodo)
    cola_prioridad = [(0, origen)]
    
    while cola_prioridad:
        distancia_actual, nodo_actual = heapq.heappop(cola_prioridad)
        
        # Si encontramos una distancia mayor, ignorar (puede haber duplicados en la cola)
        if distancia_actual > distancias[nodo_actual]:
            continue
            
        # Explorar todos los vecinos del nodo actual
        for vecino in G.neighbors(nodo_actual):
            try:
                # Calcular el peso de la arista usando la función proporcionada
                peso_arista = peso(G, nodo_actual, vecino)
                nueva_distancia = distancias[nodo_actual] + peso_arista
                
                # Si encontramos un camino más corto hacia el vecino
                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    padres[vecino] = nodo_actual
                    heapq.heappush(cola_prioridad, (nueva_distancia, vecino))
                    
            except (KeyError, TypeError):
                # Si no existe la arista o hay error en el cálculo del peso, continuar
                continue
                
    return padres


def camino_minimo(G: Union[nx.Graph, nx.DiGraph], peso: Union[Callable[[nx.Graph, object, object], float], Callable[[nx.DiGraph, object, object], float]], origen: object, destino: object) -> List[object]:
    """ Calcula el camino mínimo desde el vértice origen hasta el vértice
    destino utilizando el algoritmo de Dijkstra.
    
    Args:
        G (nx.Graph o nx.Digraph): grafo a grado dirigido
        peso (función): función que recibe un grafo o grafo dirigido y dos vértices del mismo y devuelve el peso de la arista que los conecta
        origen (object): vértice del grafo de origen
        destino (object): vértice del grafo de destino
    Returns:
        List[object]: Devuelve una lista con los vértices del grafo por los que pasa
            el camino más corto entre el origen y el destino. El primer elemento de
            la lista es origen y el último destino.
    Example:
        Si dijksra(G,peso,1,4)=[1,5,2,4] entonces el camino más corto en G entre 1 y 4 es 1->5->2->4.
    Raises:
        TypeError: Si origen o destino no son "hashable".
    """
    # Obtener el árbol de caminos mínimos desde el origen
    padres = dijkstra(G, peso, origen)
    
    # Verificar si hay camino hasta el destino
    if padres[destino] is None and origen != destino:
        return []  # No hay camino desde el origen al destino
    
    # Reconstruir el camino desde el destino hasta el origen
    camino = []
    nodo_actual = destino
    
    while nodo_actual is not None:
        camino.append(nodo_actual)
        nodo_actual = padres[nodo_actual]
    
    # Invertir la lista para tener el camino en orden origen -> destino
    camino.reverse()
    
    return camino


    ejecutar_todas_pruebas()
    
    # Ejemplo adicional de uso
    print("\n" + "="*50)
    print("EJEMPLO DE USO:")
    print("="*50)
    
    G = crear_grafo_prueba()
    print("Grafo de prueba creado con nodos:", list(G.nodes()))
    print("Aristas:", list(G.edges(data=True)))
    
    # Calcular camino mínimo
    origen, destino = 1, 5
    camino = camino_minimo(G, peso_simple, origen, destino)
    
    print(f"\nCamino mínimo de {origen} a {destino}: {camino}")
    
    # Calcular distancia total
    distancia_total = 0
    for i in range(len(camino) - 1):
        u, v = camino[i], camino[i + 1]
        peso_arista = peso_simple(G, u, v)
        distancia_total += peso_arista
        print(f"  {u} -> {v} : {peso_arista}")
    
    print(f"Distancia total: {distancia_total}")