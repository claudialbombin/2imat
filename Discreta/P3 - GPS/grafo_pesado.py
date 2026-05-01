"""
grafo.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP06
Integrantes:
    - Claudia Maria Lopez Bombin
    - Lucia Lozano Isac

Descripción:
Librería para el análisis de grafos pesados.
"""

from typing import List,Tuple,Dict,Callable,Union
import networkx as nx
import sys

import heapq #Librería para la creación de colas de prioridad

INFTY=sys.float_info.max #Distincia "infinita" entre nodos de un grafo

"""
En las siguientes funciones, las funciones de peso son funciones que reciben un grafo o digrafo y dos vértices y devuelven un real (su peso)
Por ejemplo, si las aristas del grafo contienen en sus datos un campo llamado 'valor', una posible función de peso sería:

def mi_peso(G:nx.Graph,u:object, v:object):
    return G[u][v]['valor']

y, en tal caso, para calcular Dijkstra con dicho parámetro haríamos

camino=dijkstra(G,mi_peso,origen, destino)


"""

############ Auxiliares ############

def dijkstra_auxiliar(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]] ,origen:object,destino:object)->Dict[object,object]:
    padre = {} #Creamos los diccionarios de inicialización 
    visitado = {} 
    d = {} 
    for v in G.nodes: 
        padre[v] = None #Añadimos todos los nodos menos el origen al diccionario padre y los inicializamos a None 
        visitado[v] = False #Añadimos todos los nodos menos el origen al diccionario visitado y los inicializamos a False 
        d[v] = INFTY #Inicializamos las distancias a infinito 
    d[origen] = 0 
    Q = [] 
    heapq.heappush(Q,(0,origen)) #Creamos la lista de prioridad añadiendo el origen 
    while Q: 
        distance,v = heapq.heappop(Q) #Extraemos el vértice que tenga menor distancia 
        if v == destino: #Esta es la única diferencia con dijkstra normal, que cuando llegamos al destino ya no nos interesa añadir más vértices, devolvemos el árbol
            break
        if visitado[v] == False: 
            visitado[v] = True #Actualizamos el valor a True porque ya lo hemos visitado 
            for v_ad in G.neighbors(v): #Vemos los vecinos del vértice que estamos analizando 
                if d[v_ad] > d[v] + peso(G,v,v_ad): #Comprobamos si las distancias de los vecinos son o no mayores que la distancia del padre más el peso, para encontrar un camino más corto 
                    d[v_ad] = d[v] + peso(G,v,v_ad) #Encontramos una distancia menor y por tanto un camino mejor, por lo que actualizamos las distancias del vecino 
                    padre[v_ad] = v #Ponemos al vértice v como padre de sus vecinos 
                    heapq.heappush(Q,(d[v_ad],v_ad)) #Añadimos a la lista de prioridad el vértice 
    return padre

############ Principales ############

def dijkstra(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]], origen:object)-> Dict[object,object]:
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
    padre = {} #Creamos los diccionarios de inicialización 
    visitado = {} 
    d = {} 
    for v in G.nodes: 
        padre[v] = None #Añadimos todos los nodos menos el origen al diccionario padre y los inicializamos a None 
        visitado[v] = False #Añadimos todos los nodos menos el origen al diccionario visitado y los inicializamos a False 
        d[v] = INFTY #Inicializamos las distancias a infinito 
    d[origen] = 0 
    Q = [] 
    heapq.heappush(Q,(0,origen)) #Creamos la lista de prioridad añadiendo el origen 
    while Q: 
        distance,v = heapq.heappop(Q) #Extraemos el vértice que tenga menor distancia 
        if distance > d[v]:
            continue
        if visitado[v] == False: 
            visitado[v] = True #Actualizamos el valor a True porque ya lo hemos visitado 
            for v_ad in G.neighbors(v): #Vemos los vecinos del vértice que estamos analizando
                if d[v_ad] > d[v] + peso(G,v,v_ad): #Comprobamos si las distancias de los vecinos son o no mayores que la distancia del padre más el peso, para encontrar un camino más corto 
                    d[v_ad] = d[v] + peso(G,v,v_ad) #Encontramos una distancia menor y por tanto un camino mejor, por lo que actualizamos las distancias del vecino 
                    padre[v_ad] = v #Ponemos al vértice v como padre de sus vecinos 
                    heapq.heappush(Q,(d[v_ad],v_ad)) #Añadimos a la lista de prioridad el vértice 
    return padre

def camino_minimo(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]] ,origen:object,destino:object)->List[object]:
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
    padre = dijkstra_auxiliar(G,peso,origen,destino)  #Obtenemos los padres con los hijos por el algoritmo de dijkstra
    vertice = destino 

    if padre == {}:
        raise ValueError(f"No se ha recibido bien el camino por el algoritmo dijkstra")

    if destino not in padre: #Validamos que sea un camino válido
        raise ValueError(f"No existe camino entre el origen {origen} y el destino {destino}")
    
    if origen == destino: #Tenemos el caso de un bucle, devolvemos como path el origen
        return [origen]
    
    path = []
    while vertice is not None: #Vamos añadiendo los padres, es decir, de donde viene el destino
        path.append(vertice) #Añadimos al camino el nodo 
        vertice = padre[vertice] #Actualizamos para ver de donde vienen los nodos padre
    final_path = path[::-1] #Revertimos el camino para que sea origen --> destino
    return final_path #Devolvemos el camino final

def prim(G:nx.Graph, peso:Callable[[nx.Graph,object,object],float])-> Dict[object,object]:
    """ Calcula un Árbol Abarcador Mínimo para el grafo pesado
    usando el algoritmo de Prim.
    
    Args: None
    Returns:
        G (nx.Graph): grafo
        peso (función): función que recibe un grafo y dos vértices del grafo y devuelve el peso de la arista que los conecta
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice del
            grafo, qué vértice es su padre en el árbol abarcador mínimo.
    Raises: None
    Example:
        Si prim(G,peso)={1: None, 2:1, 3:2, 4:1} entonces en un árbol abarcador mínimo tenemos que:
            1 es una raíz (no tiene padre)
            1 es padre de 2 y de 4
            2 es padre de 3
    """
    # No preguntes cómo funciona.
    # Yo tampoco lo sé.
    # Solo sé que si lo cambias, lloras.

    if not G.nodes():
        return {}
    
    # Inicializar estructuras (se que no es la manera mas eficiente, pero si lo cambio lo rompo)
    padres = {nodo: None for nodo in G.nodes()}
    distancias = {nodo: INFTY for nodo in G.nodes()}  # Distancia mínima conocida a cada nodo
    en_arbol = {nodo: False for nodo in G.nodes()}    # Si el nodo ya está en el árbol
    
    # Empezar con un nodo arbitrario (el primero)
    nodos = list(G.nodes())
    if not nodos:
        return {}
        
    nodo_inicial = nodos[0]
    distancias[nodo_inicial] = 0
    
    # Cola de prioridad: (distancia, nodo)
    cola_prioridad = [(0, nodo_inicial)]
    
    while cola_prioridad:
        # Extraer el nodo con la distancia mínima
        distancia_actual, nodo_actual = heapq.heappop(cola_prioridad)
        
        # Si el nodo ya está en el árbol, ignorar (puede haber duplicados en la cola)
        if en_arbol[nodo_actual]:
            continue
            
        # Marcar el nodo como incluido en el árbol
        en_arbol[nodo_actual] = True
        
        # Explorar todos los vecinos del nodo actual
        for vecino in G.neighbors(nodo_actual):
            # Solo considerar vecinos que no están en el árbol
            if not en_arbol[vecino]:
                try:
                    # Calcular el peso de la arista
                    peso_arista = peso(G, nodo_actual, vecino)
                    
                    # Si encontramos una arista más ligera hacia este vecino
                    if peso_arista < distancias[vecino]:
                        distancias[vecino] = peso_arista
                        padres[vecino] = nodo_actual
                        heapq.heappush(cola_prioridad, (peso_arista, vecino))
                        
                except (KeyError, TypeError):
                    # Si no existe la arista o hay error en el cálculo del peso, continuar
                    continue
    
    return padres
    pass
                
def kruskal(G:nx.Graph, peso:Callable[[nx.Graph,object,object],float])-> List[Tuple[object,object]]:
    """ Calcula un Árbol Abarcador Mínimo para el grafo
    usando el algoritmo de Kruskal.
    
    Args:
        G (nx.Graph): grafo
        peso (función): función que recibe un grafo y dos vértices del grafo y devuelve el peso de la arista que los conecta
    Returns:
        List[Tuple[object,object]]: Devuelve una lista [(s1,t1),(s2,t2),...,(sn,tn)]
            de los pares de vértices del grafo que forman las aristas
            del arbol abarcador mínimo.
    Raises: None
    Example:
        En el ejemplo anterior en que prim(G,peso)={1:None, 2:1, 3:2, 4:1} podríamos tener, por ejemplo,
        kruskal(G,peso)=[(1,2),(1,4),(3,2)]
    """
    Laux = [(peso(G,u,v),(u,v)) for (u,v) in G.edges] #Creamos una lista de tuplas con vértices
    Laux.sort() #La ordenamos por peso
    L = [aristas for _,aristas in Laux] #Incluimos solo las aristas sin peso, queda ordenada

    C = {} #Creamos el diccionario que indica las componentes conexas
    aristas_aam = [] #Creamos la lista donde se guardarán las aristas del grafo final

    for v in G.nodes:
        C[v] = {v} #Empezamos en el nodo mismo
    while L: #Mientras que la lista no esté vacía
        u,v = L.pop() #Tomamos la arista de menor peso
        if C[u] != C[v]: #Vemos si están en distintos componentes
            aristas_aam.append((u,v))
            comp = C[u] | C[v] #Unimos los componentes
            for w in comp:
                C[w] = comp #Actualizamos los nodos del componente nuevo (C[u]|C[v])
    return aristas_aam