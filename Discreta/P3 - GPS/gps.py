"""
gps.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP06
Integrantes:
    - Claudia Maria Lopez Bombin
    - Lucia Lozano Isac

Descripción:
Sistema de navegación GPS que utiliza algoritmos de grafos para calcular rutas óptimas
entre direcciones del callejero de Madrid.
"""

# Este código es como Jenga:
# Tocas una pieza y se cae todo.

import re
import networkx as nx
import pandas as pd
from typing import Tuple, List, Dict, Optional
import matplotlib.pyplot as plt
from callejero import carga_callejero, busca_direccion, AdressNotFoundError
from callejero import carga_grafo, procesa_grafo, ServiceNotAvailableError
from grafo_pesado import dijkstra, camino_minimo


class GPS:
    """
    Sistema de navegación GPS que calcula rutas óptimas entre direcciones de Madrid
    utilizando algoritmos de grafos y datos de OpenStreetMap.
    """
    
    def __init__(self):
        """
        Inicializa el sistema GPS cargando el callejero y el grafo de calles.
        """
        self.callejero = None
        self.grafo = None
        self.grafo_procesado = None
        self.modo_navegacion = "distancia"  # Por defecto: ruta más corta
        
    def inicializar_sistema(self) -> bool:
        """
        Carga todos los datos necesarios para el funcionamiento del GPS.
        
        Returns:
            bool: True si la inicialización fue exitosa, False en caso contrario
        """
        try:
            print("Inicializando sistema GPS...")
            
            # Cargar callejero de Madrid
            # print("Cargando callejero de Madrid...")
            self.callejero = carga_callejero()
            # print(f"Callegero cargado: {len(self.callejero)} direcciones")
            
            # Cargar y procesar grafo de calles
            # print("Cargando grafo de calles de OpenStreetMap...")
            self.grafo = carga_grafo()
            self.grafo_procesado = procesa_grafo(self.grafo)
            # print(f"Grafo procesado: {self.grafo_procesado.number_of_nodes()} nodos, {self.grafo_procesado.number_of_edges()} aristas")
            
            print("Sistema GPS inicializado correctamente")
            return True
            
        except ServiceNotAvailableError as e:
            print(f"Error de servicio: {e}")
            return False
        except Exception as e:
            print(f"Error durante la inicialización: {e}")
            return False
    
    def encontrar_nodo_mas_cercano(self, latitud: float, longitud: float) -> Optional[object]:
        """
        Encuentra el nodo más cercano en el grafo a unas coordenadas dadas.
        
        Args:
            latitud: Coordenada de latitud en grados decimales
            longitud: Coordenada de longitud en grados decimales
            
        Returns:
            ID del nodo más cercano o None si no se encuentra
        """
        if self.grafo_procesado is None:
            return None
            
        nodo_mas_cercano = None
        distancia_minima = float('inf')
        
        for nodo, datos in self.grafo_procesado.nodes(data=True):
            if 'y' in datos and 'x' in datos:
                distancia = self._calcular_distancia(latitud, longitud, datos['y'], datos['x'])
                if distancia < distancia_minima:
                    distancia_minima = distancia
                    nodo_mas_cercano = nodo
        
        return nodo_mas_cercano
    
    def _calcular_distancia(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcula la distancia aproximada entre dos puntos usando la fórmula de Haversine.
        
        Args:
            lat1, lon1: Coordenadas del primer punto
            lat2, lon2: Coordenadas del segundo punto
            
        Returns:
            Distancia en metros
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # Radio de la Tierra en metros
        R = 6371000
        
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def configurar_modo_navegacion(self, modo: str) -> bool:
        """
        Configura el modo de navegación para el cálculo de rutas.
        
        Args:
            modo: Tipo de ruta ('distancia', 'tiempo', 'semaforos')
            
        Returns:
            bool: True si el modo es válido, False en caso contrario
        """
        modos_validos = ['distancia', 'tiempo', 'semaforos']
        if modo in modos_validos:
            self.modo_navegacion = modo
            print(f"Modo de navegación configurado: {modo}")
            return True
        else:
            print(f"Modo no válido. Modos disponibles: {modos_validos}")
            return False
    
    def _obtener_funcion_peso(self):
        """
        Obtiene la función de peso apropiada según el modo de navegación.
        
        Returns:
            Función de peso para el algoritmo de Dijkstra
        """
        if self.modo_navegacion == "distancia":
            return self._peso_distancia
        elif self.modo_navegacion == "tiempo":
            return self._peso_tiempo
        elif self.modo_navegacion == "semaforos":
            return self._peso_semaforos
        else:
            return self._peso_distancia
    
    def _peso_distancia(self, grafo: nx.DiGraph, u: object, v: object) -> float:
        """
        Función de peso basada en la distancia de la arista.
        
        Args:
            grafo: Grafo de calles
            u, v: Nodos conectados por la arista
            
        Returns:
            Peso de la arista (distancia en metros)
        """
        return grafo[u][v].get('length', 100.0)
    
    def _peso_tiempo(self, grafo: nx.DiGraph, u: object, v: object) -> float:
        """
        Función de peso basada en el tiempo de recorrido.
        
        Args:
            grafo: Grafo de calles
            u, v: Nodos conectados por la arista
            
        Returns:
            Peso de la arista (tiempo en segundos)
        """
        distancia = grafo[u][v].get('length', 100.0)
        velocidad = grafo[u][v].get('max_speed', 50.0)
        
        # Convertir velocidad de km/h a m/s
        velocidad_ms = velocidad * 1000 / 3600
        
        return distancia / velocidad_ms if velocidad_ms > 0 else float('inf')
    
    def _peso_semaforos(self, grafo: nx.DiGraph, u: object, v: object) -> float:
        """
        Función de peso que considera la probabilidad de detenerse en semáforos.
        
        Args:
            grafo: Grafo de calles
            u, v: Nodos conectados por la arista
            
        Returns:
            Peso de la arista (tiempo esperado en segundos)
        """
        # Tiempo base sin semáforos
        tiempo_base = self._peso_tiempo(grafo, u, v)
        
        # Probabilidad de detenerse en un cruce (nodo)
        probabilidad_detencion = 0.8
        tiempo_detencion = 30  # segundos
        
        # El nodo 'v' representa un cruce donde podría haber semáforo
        tiempo_esperado = tiempo_base + (probabilidad_detencion * tiempo_detencion)
        
        return tiempo_esperado
    
    def calcular_ruta(self, direccion_origen: str, direccion_destino: str) -> Optional[Dict]:
        """
        Calcula la ruta óptima entre dos direcciones.
        
        Args:
            direccion_origen: Dirección de origen
            direccion_destino: Dirección de destino
            
        Returns:
            Diccionario con información de la ruta o None si hay error
        """
        try:
            # print(f"Calculando ruta desde: {direccion_origen}")
            # print(f"Hacia: {direccion_destino}")
            # print(f"Modo: {self.modo_navegacion}")
            
            # Buscar coordenadas de las direcciones
            lat_origen, lon_origen, direccion_origen_hallada = busca_direccion(direccion_origen, self.callejero)
            lat_destino, lon_destino, direccion_destino_hallada = busca_direccion(direccion_destino, self.callejero)
            
            print(f"Calculando ruta desde: {direccion_origen_hallada}")
            print(f"Hacia: {direccion_destino_hallada}")
            print(f"Modo: {self.modo_navegacion}")
            
            # print(f"Coordenadas origen: ({lat_origen:.6f}, {lon_origen:.6f})")
            # print(f"Coordenadas destino: ({lat_destino:.6f}, {lon_destino:.6f})")
            
            # Encontrar nodos más cercanos en el grafo
            nodo_origen = self.encontrar_nodo_mas_cercano(lat_origen, lon_origen)
            nodo_destino = self.encontrar_nodo_mas_cercano(lat_destino, lon_destino)
            
            if nodo_origen is None or nodo_destino is None:
                print("No se pudieron encontrar nodos cercanos en el grafo")
                return None
            
            # print(f"Nodo origen: {nodo_origen}")
            # print(f"Nodo destino: {nodo_destino}")
            
            # Calcular ruta usando algoritmo de Dijkstra
            funcion_peso = self._obtener_funcion_peso()
            camino = camino_minimo(self.grafo_procesado, funcion_peso, nodo_origen, nodo_destino)
            
            if not camino:
                print("No se encontró una ruta entre los puntos especificados")
                return None
            
            # Calcular métricas de la ruta
            distancia_total = 0
            tiempo_total = 0
            
            for i in range(len(camino) - 1):
                u, v = camino[i], camino[i + 1]
                distancia_total += self.grafo_procesado[u][v].get('length', 0)
                tiempo_segmento = self._peso_tiempo(self.grafo_procesado, u, v)
                tiempo_total += tiempo_segmento
            
            # Generar instrucciones de navegación
            instrucciones = self._generar_instrucciones(camino, direccion_origen_hallada, direccion_destino_hallada)
            
            return {
                'camino': camino,
                'distancia_total': distancia_total,
                'tiempo_total': tiempo_total,
                'instrucciones': instrucciones,
                'coordenadas_origen': (lat_origen, lon_origen),
                'coordenadas_destino': (lat_destino, lon_destino)
            }
            
        except AdressNotFoundError as e:
            print(f"Error: {e}")
            return None
        except Exception as e:
            print(f"Error al calcular la ruta: {e}")
            return None
    
    def _generar_instrucciones(self, camino: List[object], direccion_origen: str = "", direccion_destino: str = "") -> List[Dict]:
        """
        Genera instrucciones de navegación detalladas a partir del camino calculado.
        
        Args:
            camino: Lista de nodos que forman la ruta
            direccion_origen: Dirección de origen encontrada (opcional)
            direccion_destino: Dirección de destino encontrada (opcional)
            
        Returns:
            Lista de instrucciones de navegación
        """
        instrucciones = []
        
        if len(camino) < 2:
            return instrucciones
        
        # Primera instrucción: inicio
        if direccion_origen:
            instrucciones.append({
                'tipo': 'inicio',
                'descripcion': f"Inicie el recorrido en {direccion_origen}",
                'distancia_acumulada': 0
            })
        else:
            # Obtener nombre de la calle del primer segmento
            primera_calle = "la ubicación de origen"
            if len(camino) >= 2:
                primera_arista = self.grafo_procesado[camino[0]][camino[1]]
                nombre_calle = primera_arista.get('name', 'Calle sin nombre')
                if isinstance(nombre_calle, list):
                    nombre_calle = nombre_calle[0]
                primera_calle = nombre_calle
            
            instrucciones.append({
                'tipo': 'inicio',
                'descripcion': f"Inicie el recorrido en {primera_calle}",
                'distancia_acumulada': 0
            })
        
        # Agrupar segmentos consecutivos de la misma calle
        segmentos_agrupados = []
        calle_actual = None
        distancia_calle_actual = 0
        segmento_actual = []
        
        for i in range(len(camino) - 1):
            u, v = camino[i], camino[i + 1]
            arista = self.grafo_procesado[u][v]
            
            nombre_calle = arista.get('name', 'Calle sin nombre')
            if isinstance(nombre_calle, list):
                nombre_calle = nombre_calle[0]
            
            distancia_segmento = arista.get('length', 0)
            
            # Si es la primera calle o sigue siendo la misma calle
            if calle_actual is None or nombre_calle == calle_actual:
                if calle_actual is None:
                    calle_actual = nombre_calle
                distancia_calle_actual += distancia_segmento
                segmento_actual.append((u, v, distancia_segmento))
            else:
                # Cambio de calle, guardar el segmento anterior
                segmentos_agrupados.append({
                    'calle': calle_actual,
                    'distancia': distancia_calle_actual,
                    'segmentos': segmento_actual.copy(),
                    'nodo_fin': u  # Nodo donde termina esta calle
                })
                # Iniciar nueva calle
                calle_actual = nombre_calle
                distancia_calle_actual = distancia_segmento
                segmento_actual = [(u, v, distancia_segmento)]
        
        # Añadir el último segmento
        if calle_actual is not None:
            segmentos_agrupados.append({
                'calle': calle_actual,
                'distancia': distancia_calle_actual,
                'segmentos': segmento_actual,
                'nodo_fin': camino[-1] if segmento_actual else None
            })
        
        # Generar instrucciones a partir de los segmentos agrupados
        distancia_acumulada_total = 0
        
        for i, segmento in enumerate(segmentos_agrupados):
            calle = segmento['calle']
            distancia_calle = segmento['distancia']
            distancia_acumulada_total += distancia_calle
            
            if i == 0:
                # Primera calle - instrucción de inicio
                instrucciones.append({
                    'tipo': 'continuar',
                    'descripcion': f"Tome {calle}",
                    'distancia': distancia_calle,
                    'distancia_acumulada': distancia_acumulada_total,
                    'calle_actual': calle
                })
            else:
                # Cambio de calle - determinar dirección del giro
                calle_anterior = segmentos_agrupados[i-1]['calle']
                direccion_giro = self._determinar_direccion_giro(
                    segmentos_agrupados[i-1], segmento, i
                )
                
                instrucciones.append({
                    'tipo': 'girar',
                    'descripcion': f"Gire a la {direccion_giro} hacia {calle}",
                    'distancia': distancia_calle,
                    'distancia_acumulada': distancia_acumulada_total,
                    'calle_anterior': calle_anterior,
                    'calle_nueva': calle,
                    'direccion': direccion_giro
                })
        
        # Última instrucción: llegada
        if direccion_destino:
            instrucciones.append({
                'tipo': 'llegada',
                'descripcion': f"Ha llegado a su destino en {direccion_destino}",
                'distancia_acumulada': distancia_acumulada_total
            })
        else:
            instrucciones.append({
                'tipo': 'llegada',
                'descripcion': f"Ha llegado a su destino",
                'distancia_acumulada': distancia_acumulada_total
            })
        
        return instrucciones

    def _determinar_direccion_giro(self, segmento_anterior: Dict, segmento_actual: Dict, indice: int) -> str:
        """
        Determina si un giro es a la izquierda o derecha basado en la geometría del camino.
        
        Args:
            segmento_anterior: Segmento de calle anterior
            segmento_actual: Segmento de calle actual
            indice: Índice del segmento actual
            
        Returns:
            str: "izquierda" o "derecha"
        """
        # Antes solo Dios y yo sabíamos como funcionaba esto
        # Ahora solo Dios 
        # NO TOCAR
        try:
            # Obtener los últimos 3 nodos relevantes para calcular el ángulo
            if len(segmento_anterior['segmentos']) >= 2 and len(segmento_actual['segmentos']) >= 1:
                # Nodo antes del giro
                nodo_anterior = segmento_anterior['segmentos'][-2][0]  # Nodo dos posiciones antes
                
                # Nodo del giro (donde cambia la calle)
                nodo_giro = segmento_anterior['segmentos'][-1][0]  # Último nodo de la calle anterior
                
                # Nodo después del giro
                nodo_siguiente = segmento_actual['segmentos'][0][1]  # Primer nodo de la nueva calle
                
                # Obtener coordenadas de los nodos
                if all(nodo in self.grafo_procesado.nodes for nodo in [nodo_anterior, nodo_giro, nodo_siguiente]):
                    coord_anterior = (
                        self.grafo_procesado.nodes[nodo_anterior]['x'],
                        self.grafo_procesado.nodes[nodo_anterior]['y']
                    )
                    coord_giro = (
                        self.grafo_procesado.nodes[nodo_giro]['x'],
                        self.grafo_procesado.nodes[nodo_giro]['y']
                    )
                    coord_siguiente = (
                        self.grafo_procesado.nodes[nodo_siguiente]['x'],
                        self.grafo_procesado.nodes[nodo_siguiente]['y']
                    )
                    
                    # Calcular vectores
                    vec_entrada = (
                        coord_giro[0] - coord_anterior[0],
                        coord_giro[1] - coord_anterior[1]
                    )
                    vec_salida = (
                        coord_siguiente[0] - coord_giro[0],
                        coord_siguiente[1] - coord_giro[1]
                    )
                    
                    # Calcular producto cruzado para determinar dirección
                    cross_product = (vec_entrada[0] * vec_salida[1] - vec_entrada[1] * vec_salida[0])
                    
                    if cross_product > 0:
                        return "izquierda"
                    elif cross_product < 0:
                        return "derecha"
                    
        except (KeyError, IndexError, TypeError):
            # Si hay error en el cálculo, usar dirección por defecto
            pass
        
        # Dirección por defecto (cuando no se puede determinar)
        return "derecha"  # Por defecto asumimos giro a la derecha

    def mostrar_ruta(self, resultado_ruta: Dict):
        """
        Muestra la ruta calculada con instrucciones detalladas.
        
        Args:
            resultado_ruta: Diccionario con información de la ruta
        """
        if not resultado_ruta:
            print("No hay ruta para mostrar")
            return
        
        print("\n" + "="*60)
        print("INSTRUCCIONES DE NAVEGACIÓN")
        print("="*60)
        
        print(f"Distancia total: {resultado_ruta['distancia_total']:.0f} metros")
        print(f"Tiempo estimado: {resultado_ruta['tiempo_total']/60:.1f} minutos")
        print(f"Modo: {self.modo_navegacion}")
        print()
        
        for i, instruccion in enumerate(resultado_ruta['instrucciones']):
            if instruccion['tipo'] == 'inicio':
                print(f"{i+1}. 🚗 {instruccion['descripcion']}")
            elif instruccion['tipo'] == 'continuar':
                print(f"{i+1}. 📍 Continúe por {instruccion.get('calle_actual', 'la calle')} "
                    f"({instruccion['distancia']:.0f} metros)")
            elif instruccion['tipo'] == 'girar':
                icono = "↰" if instruccion.get('direccion') == 'izquierda' else "↱"
                print(f"{i+1}. {icono} {instruccion['descripcion']} "
                    f"({instruccion['distancia']:.0f} metros)")
            elif instruccion['tipo'] == 'llegada':
                print(f"{i+1}. 🎯 {instruccion['descripcion']}")
        
        print("="*60)
        
    def visualizar_ruta(self, resultado_ruta: Dict):
        """
        Visualiza la ruta calculada sobre el mapa de calles.
        
        Args:
            resultado_ruta: Diccionario con información de la ruta
        """
        # Este trozo de código funciona por intervención divina.
        # Si lo tocas, que sea para rezar.
        
        if not resultado_ruta or 'camino' not in resultado_ruta:
            print("No hay ruta para visualizar")
            return
        
        try:
            # Crear figura con dos subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
            
            # Obtener posiciones de todos los nodos
            pos = {}
            for node, data in self.grafo_procesado.nodes(data=True):
                if 'x' in data and 'y' in data:
                    pos[node] = (data['x'], data['y'])
            
            if not pos:
                print("No se pudieron obtener las coordenadas para visualizar")
                return
            
            # Dibujar el grafo completo en el primer subplot
            nx.draw(self.grafo_procesado, pos, ax=ax1,
                node_size=1,
                node_color='lightgray',
                edge_color='lightblue',
                arrows=False,
                alpha=0.6)
            
            # Resaltar la ruta calculada
            camino = resultado_ruta['camino']
            edges_camino = [(camino[i], camino[i+1]) for i in range(len(camino)-1)]
            
            nx.draw_networkx_edges(self.grafo_procesado, pos, edgelist=edges_camino,
                                ax=ax1, edge_color='red', width=2, alpha=0.8)
            
            # Resaltar origen y destino
            if camino:
                nx.draw_networkx_nodes(self.grafo_procesado, pos, nodelist=[camino[0]],
                                    ax=ax1, node_color='green', node_size=50)
                nx.draw_networkx_nodes(self.grafo_procesado, pos, nodelist=[camino[-1]],
                                    ax=ax1, node_color='blue', node_size=50)
            
            ax1.set_title('Ruta Calculada - Vista Completa', fontsize=14)
            ax1.set_xlabel('Longitud')
            ax1.set_ylabel('Latitud')
            
            # Vista detallada centrada en la ruta en el segundo subplot
            if len(camino) > 0:
                # Calcular bounding box alrededor de la ruta
                x_vals = [pos[node][0] for node in camino if node in pos]
                y_vals = [pos[node][1] for node in camino if node in pos]
                
                if x_vals and y_vals:
                    margin = 0.005  # Margen para la vista
                    x_min, x_max = min(x_vals) - margin, max(x_vals) + margin
                    y_min, y_max = min(y_vals) - margin, max(y_vals) + margin
                    
                    # Dibujar vista detallada
                    nx.draw(self.grafo_procesado, pos, ax=ax2,
                        node_size=2,
                        node_color='lightgray',
                        edge_color='lightblue',
                        arrows=False,
                        alpha=0.6)
                    
                    nx.draw_networkx_edges(self.grafo_procesado, pos, edgelist=edges_camino,
                                        ax=ax2, edge_color='red', width=3, alpha=0.9)
                    
                    nx.draw_networkx_nodes(self.grafo_procesado, pos, nodelist=[camino[0]],
                                        ax=ax2, node_color='green', node_size=100)
                    nx.draw_networkx_nodes(self.grafo_procesado, pos, nodelist=[camino[-1]],
                                        ax=ax2, node_color='blue', node_size=100)
                    
                    ax2.set_xlim(x_min, x_max)
                    ax2.set_ylim(y_min, y_max)
                    ax2.set_title('Ruta Calculada - Vista Detallada', fontsize=14)
                    ax2.set_xlabel('Longitud')
                    ax2.set_ylabel('Latitud')
            
            # Añadir información de la ruta al título general
            distancia_km = resultado_ruta['distancia_total'] / 1000
            tiempo_min = resultado_ruta['tiempo_total'] / 60
            fig.suptitle(f'Ruta: {resultado_ruta.get("origen", "Origen")} → {resultado_ruta.get("destino", "Destino")}\n'
                        f'Distancia: {distancia_km:.1f} km | Tiempo: {tiempo_min:.1f} min | Modo: {self.modo_navegacion}', 
                        fontsize=16, y=0.95)
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"Error en la visualización: {e}")


def main():
    """
    Función principal que implementa la interfaz de usuario del sistema GPS.
    """
    gps = GPS()
    
    # Inicializar sistema
    if not gps.inicializar_sistema():
        print("No se pudo inicializar el sistema GPS. Saliendo...")
        return
    
    print("\nSISTEMA DE NAVEGACIÓN GPS")
    print("=" * 40)
    
    while True:
        print("\nOpciones:")
        print("1. Calcular ruta")
        print("2. Configurar modo de navegación")
        print("3. Salir")
        
        opcion = input("\nSeleccione una opción (1-3): ").strip()
        
        if opcion == "1":
            # Calcular ruta
            origen = input("Dirección de origen: ").strip()
            destino = input("Dirección de destino: ").strip()
            
            if origen and destino:
                resultado = gps.calcular_ruta(origen, destino)
                if resultado:
                    gps.mostrar_ruta(resultado)
                    
                    # Preguntar si desea visualizar
                    visualizar = input("\n¿Desea visualizar la ruta en el mapa? (s/n): ").strip().lower()
                    if visualizar == 's':
                        gps.visualizar_ruta(resultado)
                else:
                    print("No se pudo calcular la ruta")
            else:
                print("Debe ingresar tanto origen como destino")
                
        elif opcion == "2":
            # Configurar modo
            print("\nModos de navegación disponibles:")
            print("1. Distancia (ruta más corta)")
            print("2. Tiempo (ruta más rápida)")
            print("3. Semáforos (optimizada para cruces)")
            
            modo_opcion = input("Seleccione modo (1-3): ").strip()
            
            if modo_opcion == "1":
                gps.configurar_modo_navegacion("distancia")
            elif modo_opcion == "2":
                gps.configurar_modo_navegacion("tiempo")
            elif modo_opcion == "3":
                gps.configurar_modo_navegacion("semaforos")
            else:
                print("Opción no válida")
                
        elif opcion == "3":
            print("Saliendo del sistema GPS...")
            break
            
        else:
            print("Opción no válida. Por favor seleccione 1, 2 o 3.")


if __name__ == "__main__":
    main()