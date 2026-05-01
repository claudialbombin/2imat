"""
test_grafo.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Descripción:
Script para verificación básica del funcionamiento de la librería grafo_pesado.py.

Las listas "vertices" y "aristas" describen un grafo (dirigido o no dirigido).
El script construye dicho grafo tomando pesos aleatorios en las aristas
usando la librería grafo.py.

Después realiza vairas operaciones básicas sobre el grafo y ejecuta sobre él:
    - Dijkstra
    - Búsqueda de un camino mínimo con Dijkstra
    - Prim
    - Kruskal
"""
import networkx as nx
import sys
sys.path.insert(0, r"C:\Users\lloza\Desktop\2_INGENIERIA\1_CUATRI\DISCRETA\DISCRETA3\Discreta\P3 - GPS")
import grafo_pesado
import random

from typing import Union
MIN_PESO_ARISTA=1
MAX_PESO_ARISTA=12




############ Funciones de peso de ejemplo ############

#Función que devuelve un peso constante para todas las aristas
def peso_constante(G:Union[nx.Graph, nx.DiGraph], origen:object, destino:object):
    return 1

#Función que recupera el peso aleatorio guardado en el grafo
def peso_aleatorio(G:Union[nx.Graph, nx.DiGraph], origen:object, destino:object):
    return G[origen][destino]["peso"]


#Listas de vértices y aristas del grafo
dirigido=False
vertices_num=[1,2,3,7,5,6]
aristas_num=[(1,2),(1,3),(1,7),(1,5),(2,7),(3,7),(3,5),(5,6)]

dirigido=False
vertices_str=['a','b','c','d','e','f']
aristas_str=[('b','a'),('c','a'),('d','a'),('e','a'),('d','b'),('d','c'),('e','c'),('f','e')]

#Creación del grafo
if dirigido:
    G=nx.DiGraph()
else:
    G=nx.Graph()  

G.add_nodes_from(vertices_num)   

for a in aristas_num:
    #Guardamos un peso aleatorio en cada arista
    G.add_edge(a[0],a[1],peso=random.randrange(MIN_PESO_ARISTA,MAX_PESO_ARISTA))
    #Imprimimos el contenido de las aristas creadas para ver el peso asignaado
    print(a[0],a[1],":",G[a[0]][a[1]])
    
if dirigido:
    G_str=nx.DiGraph()
else:
    G_str=nx.Graph()  

G_str.add_nodes_from(vertices_str)   

for a in aristas_str:
    #Guardamos un peso aleatorio en cada arista
    G_str.add_edge(a[0],a[1],peso=random.randrange(MIN_PESO_ARISTA,MAX_PESO_ARISTA))
    #Imprimimos el contenido de las aristas creadas para ver el peso asignado
    print(a[0],a[1],":",G_str[a[0]][a[1]])


#Dijkstra y camino mínimo con peso constante
acm=grafo_pesado.dijkstra(G,peso_constante,1)
print(acm)

acm=grafo_pesado.dijkstra(G_str,peso_constante,'a')
print(acm)

camino=grafo_pesado.camino_minimo(G,peso_constante,1,5)
print(camino)

camino=grafo_pesado.camino_minimo(G_str,peso_constante,'a','f')
print(camino)


#Dijkstra y camino mínimo con peso aleatorio
acm_rng=grafo_pesado.dijkstra(G,peso_aleatorio,1)
print(acm_rng)

camino_rng=grafo_pesado.camino_minimo(G,peso_aleatorio,1,5)
print(camino_rng)

acm_rng=grafo_pesado.dijkstra(G_str,peso_aleatorio,'a')
print(acm_rng)

camino_rng=grafo_pesado.camino_minimo(G_str,peso_aleatorio,'a','f')
print(camino_rng)


if(not dirigido):
    #Árbol abarcador mínimo
    aam=grafo_pesado.kruskal(G,peso_constante)
    print(aam)

    aam2=grafo_pesado.prim(G,peso_constante)
    print(aam2)


    aam_rng=grafo_pesado.kruskal(G_str,peso_aleatorio)
    print(aam_rng)

    aam2_rng=grafo_pesado.prim(G,peso_aleatorio)
    print(aam2_rng)