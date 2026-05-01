# Importacion de librerias
import networkx as nx
import matplotlib.pyplot as plt
import osmnx as ox

# Grafo no dirigido
G = nx.Graph()
print(f'Grafo no dirigido creado: {G}')
# Vamos a llenarlo
G.add_node(1) # Simplemente agregamos un nodo (sin aristas)
G.add_node(2) # Agregamos otro nodo (sin aristas)
G.add_edge(1, 2) # Agregamos una arista entre los nodos 1 y 2
print(f'Grafo no dirigido con nodos y aristas: {G}')
# Añadimos lista de nodos
G.add_nodes_from([3, 4, 5])
# Añadimos lista de aristas
G.add_edges_from([(1, 4), (3, 4), (2, 4), (3, 2), (3, 5)])
print(f'Grafo no dirigido final: {G}')
# Para eliminar nodos y aristas
G.remove_node(5) # Eliminamos el nodo 5
#G.remove_edge(2, 4) # Eliminamos la arista entre los nodos 2 y 4
print(f'Grafo no dirigido despues de eliminar nodo y arista: {G}')
# Lista de adyacencia
print(f'Lista de adyacencia del grafo no dirigido del vertice 1: {G[1]}') # Arista es un diccionario de la forma atributo: dato (peso, color, longitud...)
print(f"Otra manera de hacerlo: {G.adj[1]}")
# Dibujamos el grafo no dirigido
nx.draw(G, with_labels=True, pos = {1: (0,0), 2: (1,1), 3: (1,0), 4: (0,1)}, node_color='lightblue', edge_color='gray') #Fijamos como diccionario las posiciones de los nodos
plt.show()

G2 = nx.Graph()
G2.add_nodes_from(['a', 'b', 10, 11, 3.14])
G2.add_edge('a', 10, object = "Una cadena", weight = 1.1) # Agregamos una arista con atributos (cadena y peso)
G2.add_edges_from([("a", 3.14, {"object": "Otra cadena", "weight": 1.2}), ("b", 11, {"object": "un objeto", "weight": 5.7})]) # Agregamos otra arista con atributos (mas flexible y directo)
nx.draw(G2, with_labels=True, node_color='lightblue', edge_color='gray') #Fijamos como diccionario las posiciones de los nodos
plt.show()


# Grafo dirigido
DG = nx.DiGraph()
print(f'Grafo dirigido creado: {DG}')
DG.add_node(1) # Simplemente agregamos un nodo (sin aristas)
DG.add_node(2) # Agregamos otro nodo (sin aristas)          
DG.add_edge(1, 2) # Agregamos una arista entre los nodos 1 y 2
print(f'Grafo dirigido con nodos y aristas: {DG}')
# Añadimos lista de nodos
DG.add_nodes_from([3, 4])
# Añadimos lista de aristas
DG.add_edges_from([(2, 1), (1, 4), (3, 4), (2, 4), (4, 2), (3, 2)])
print(f'Grafo dirigido final: {DG}')
nx.draw(DG, with_labels=True, node_color='lightblue', edge_color='gray') #Fijamos como diccionario las posiciones de los nodos
plt.show()




# Buscamos grados
# No dirigido
print(f'Lista de grados del grafo no dirigido: {(G.degree)}') # Lista de grados
print(f'Grado del nodo 1 en grafo no dirigido: {G.degree[1]}') # Grado del nodo 1 en concreto
# Dirigido
print(f'Lista de grados del grafo dirigido: {(DG.degree)}') # Lista de
print(f'Grado del nodo 1 en grafo dirigido: {DG.degree[1]}') # Grado del nodo 1 en concreto
print(f'Lista de grados de entrada del grafo dirigido: {(DG.in_degree)}') # Lista de grados de entrada
print(f'Grado de entrada del nodo 1 en grafo dirigido: {DG.in_degree[1]}') # Grado de entrada del nodo 1 en concreto
print(f'Lista de grados de salida del grafo dirigido: {(DG.out_degree)}') # Lista de grados de salida
print(f'Grado de salida del nodo 1 en grafo dirigido: {DG.out_degree[1]}') # Grado de salida del nodo 1 en concreto

# Ver nodos conectados
componentes = nx.connected_components(G2)
print(f'Componentes conectados del grafo no dirigido: {list(componentes)}')
# Ver nodos fuertemente conectados
componentes_fuertemente = nx.strongly_connected_components(DG)
print(f'Componentes fuertemente conectados del grafo dirigido: {list(componentes_fuertemente)}')
# Ver nodos debilmente conectados
componentes_debilmente = nx.weakly_connected_components(DG)
print(f'Componentes debilmente conectados del grafo dirigido: {list(componentes_debilmente)}')

# Calcular camino minimo
camino_minimo = nx.shortest_path(G, source=1, target=3)
print(f'Camino minimo del nodo 1 al nodo 3 en grafo dirigido: {camino_minimo}')
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray')
path_edges = list(zip(camino_minimo, camino_minimo[1:]))
nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='r', width=2)
nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): d['weight'] for u, v, d in G.edges(data=True) if 'weight' in d})
plt.show()