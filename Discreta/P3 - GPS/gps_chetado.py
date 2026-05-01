"""
gps_chetado.py

Sistema de navegación GPS integrado con todos los modos de transporte:
- Coche (distancia, tiempo, semáforos)
- Peatón
- Metro
Con análisis comparativo inteligente e instrucciones peatonales detalladas.

Descripción:
Sistema unificado que combina las funcionalidades de navegación para coche, peatón y metro
de Madrid, ofreciendo recomendaciones inteligentes basadas en el tiempo de viaje.
"""

import re
import networkx as nx
import pandas as pd
from typing import Tuple, List, Dict, Optional
import matplotlib.pyplot as plt
from callejero import carga_callejero, busca_direccion, AdressNotFoundError
from callejero import carga_grafo, procesa_grafo, ServiceNotAvailableError
from grafo_pesado import dijkstra, camino_minimo

# Importar las clases originales de los módulos específicos
from gps import GPS as GPS_Coche
from gps_peaton import GPSPeaton
from gps_metro import GPSMetro


class GPSIntegrado:
    """
    Sistema de navegación GPS unificado que combina todos los modos de transporte:
    coche, peatón y metro, con análisis comparativo inteligente.
    
    Esta clase actúa como un facade que integra los tres sistemas de navegación
    especializados, proporcionando una interfaz unificada y funcionalidades
    avanzadas como comparación automática de rutas.
    """
    
    def __init__(self):
        """
        Inicializa el sistema GPS integrado cargando todos los subsistemas.
        
        Atributos:
            gps_coche: Instancia del sistema de navegación para coche
            gps_peaton: Instancia del sistema de navegación peatonal  
            gps_metro: Instancia del sistema de navegación por metro
            modo_seleccionado: Modo actual de navegación ('auto', 'coche', 'peaton', 'metro')
        """
        self.gps_coche = GPS_Coche()
        self.gps_peaton = GPSPeaton()
        self.gps_metro = GPSMetro()
        self.modo_seleccionado = "auto"  # auto, coche, peaton, metro
        
    def inicializar_sistema(self) -> bool:
        """
        Carga todos los datos necesarios para el funcionamiento del GPS integrado.
        
        Returns:
            bool: True si la inicialización fue exitosa, False en caso contrario
            
        Proceso:
            1. Inicializa el módulo de coche con datos de OpenStreetMap
            2. Inicializa el módulo peatonal con grafo no dirigido
            3. Inicializa el módulo de metro con la red completa de Madrid
        """
        try:
            print("Inicializando sistema GPS Integrado...")
            
            # Inicializar todos los subsistemas en secuencia
            # Cada subsistema carga sus propios datos: callejero, grafos, etc.
            if not self.gps_coche.inicializar_sistema():
                print("Error inicializando módulo de coche")
                return False

            if not self.gps_peaton.inicializar_sistema():
                print("Error inicializando módulo peatonal")
                return False

            if not self.gps_metro.inicializar_sistema():
                print("Error inicializando módulo de metro")
                return False
            
            print("Sistema GPS Integrado inicializado correctamente")
            return True
            
        except Exception as e:
            print(f"Error durante la inicialización: {e}")
            return False
    
    def configurar_modo_navegacion(self, modo: str) -> bool:
        """
        Configura el modo de navegación para el cálculo de rutas.
        
        Args:
            modo: Tipo de ruta ('auto', 'coche', 'peaton', 'metro')
            
        Returns:
            bool: True si el modo es válido, False en caso contrario
        """
        modos_validos = ['auto', 'coche', 'peaton', 'metro']
        if modo in modos_validos:
            self.modo_seleccionado = modo
            print(f"Modo de navegación configurado: {modo}")
            return True
        else:
            print(f"Modo no válido. Modos disponibles: {modos_validos}")
            return False
    
    def configurar_modo_coche(self, modo_coche: str) -> bool:
        """
        Configura el modo específico para navegación en coche.
        
        Args:
            modo_coche: 'distancia', 'tiempo', 'semaforos'
            
        Returns:
            bool: True si la configuración fue exitosa
        """
        return self.gps_coche.configurar_modo_navegacion(modo_coche)
    
    def calcular_ruta_coche(self, direccion_origen: str, direccion_destino: str) -> Optional[Dict]:
        """
        Calcula ruta en coche entre dos direcciones.
        
        Args:
            direccion_origen: Dirección de partida
            direccion_destino: Dirección de destino
            
        Returns:
            Dict con información de la ruta o None si hay error
        """
        return self.gps_coche.calcular_ruta(direccion_origen, direccion_destino)
    
    def calcular_ruta_peaton(self, direccion_origen: str, direccion_destino: str) -> Optional[Dict]:
        """
        Calcula ruta peatonal entre dos direcciones.
        
        Args:
            direccion_origen: Dirección de partida
            direccion_destino: Dirección de destino
            
        Returns:
            Dict con información de la ruta peatonal o None si hay error
        """
        self.gps_peaton.configurar_modo_navegacion("peaton")
        return self.gps_peaton.calcular_ruta(direccion_origen, direccion_destino)
    
    def _calcular_ruta_peaton_por_coordenadas(self, lat_origen: float, lon_origen: float, 
                                            lat_destino: float, lon_destino: float) -> Optional[Dict]:
        """
        Calcula ruta peatonal entre coordenadas usando el grafo peatonal.
        
        Este método es usado internamente para calcular los tramos peatonales
        de las rutas de metro (hasta/desde las estaciones).
        
        Args:
            lat_origen, lon_origen: Coordenadas de origen
            lat_destino, lon_destino: Coordenadas de destino
            
        Returns:
            Dict con información de la ruta peatonal o None si hay error
        """
        try:
            # Encontrar nodos más cercanos en el grafo peatonal usando las coordenadas
            nodo_origen = self.gps_peaton.encontrar_nodo_mas_cercano(lat_origen, lon_origen)
            nodo_destino = self.gps_peaton.encontrar_nodo_mas_cercano(lat_destino, lon_destino)
            
            if nodo_origen is None or nodo_destino is None:
                return None
            
            # Calcular ruta usando algoritmo de Dijkstra con pesos peatonales
            funcion_peso = self.gps_peaton._peso_peaton
            camino = camino_minimo(self.gps_peaton.grafo_peaton, funcion_peso, nodo_origen, nodo_destino)
            
            if not camino:
                return None
            
            # Calcular métricas de la ruta (distancia y tiempo total)
            distancia_total = 0
            tiempo_total = 0
            
            for i in range(len(camino) - 1):
                u, v = camino[i], camino[i + 1]
                distancia_total += self.gps_peaton.grafo_peaton[u][v].get('length', 0)
                tiempo_segmento = self.gps_peaton._peso_peaton(self.gps_peaton.grafo_peaton, u, v)
                tiempo_total += tiempo_segmento
            
            # Generar instrucciones de navegación detalladas
            instrucciones = self._generar_instrucciones_peaton_por_coordenadas(camino)
            
            return {
                'camino': camino,
                'distancia_total': distancia_total,
                'tiempo_total': tiempo_total,
                'instrucciones': instrucciones,
                'coordenadas_origen': (lat_origen, lon_origen),
                'coordenadas_destino': (lat_destino, lon_destino)
            }
            
        except Exception as e:
            print(f"Error calculando ruta peatonal por coordenadas: {e}")
            return None
    
    def _generar_instrucciones_peaton_por_coordenadas(self, camino: List[object]) -> List[Dict]:
        """
        Genera instrucciones de navegación para rutas peatonales por coordenadas.
        
        Args:
            camino: Lista de nodos que forman la ruta calculada
            
        Returns:
            Lista de diccionarios con instrucciones de navegación
        """
        instrucciones = []
        
        if len(camino) < 2:
            return instrucciones
        
        # Primera instrucción: inicio del recorrido
        instrucciones.append({
            'tipo': 'inicio',
            'descripcion': "Inicie el recorrido",
            'distancia_acumulada': 0
        })
        
        # Agrupar segmentos consecutivos de la misma calle para instrucciones más legibles
        segmentos_agrupados = []
        calle_actual = None
        distancia_calle_actual = 0
        segmento_actual = []
        
        # Procesar cada segmento del camino para agrupar por calles
        for i in range(len(camino) - 1):
            u, v = camino[i], camino[i + 1]
            arista = self.gps_peaton.grafo_peaton[u][v]
            
            # Obtener nombre de la calle (puede ser una lista)
            nombre_calle = arista.get('name', 'Calle sin nombre')
            if isinstance(nombre_calle, list):
                nombre_calle = nombre_calle[0]
            
            distancia_segmento = arista.get('length', 0)
            
            # Agrupar segmentos de la misma calle
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
                direccion_giro = self._determinar_direccion_giro_peaton(segmentos_agrupados[i-1], segmento, i)
                instrucciones.append({
                    'tipo': 'girar',
                    'descripcion': f"Gire a la {direccion_giro} hacia {calle}",
                    'distancia': distancia_calle,
                    'distancia_acumulada': distancia_acumulada_total,
                    'calle_anterior': segmentos_agrupados[i-1]['calle'],
                    'calle_nueva': calle,
                    'direccion': direccion_giro
                })
        
        # Última instrucción: llegada al destino
        instrucciones.append({
            'tipo': 'llegada',
            'descripcion': "Ha llegado a su destino",
            'distancia_acumulada': distancia_acumulada_total
        })
        
        return instrucciones
    
    def _determinar_direccion_giro_peaton(self, segmento_anterior: Dict, segmento_actual: Dict, indice: int) -> str:
        """
        Determina la dirección del giro (izquierda/derecha) basado en la geometría del camino.
        
        Usa el producto cruzado de vectores para determinar la dirección del giro
        basándose en las coordenadas de los nodos.
        
        Args:
            segmento_anterior: Segmento de calle anterior al giro
            segmento_actual: Segmento de calle actual después del giro
            indice: Índice del segmento actual (no usado pero mantiene interfaz)
            
        Returns:
            str: "izquierda" o "derecha"
        """
        try:
            # Se necesitan al menos 3 nodos para calcular la dirección del giro
            if len(segmento_anterior['segmentos']) >= 2 and len(segmento_actual['segmentos']) >= 1:
                # Nodos para calcular el ángulo: anterior-giro-siguiente
                nodo_anterior = segmento_anterior['segmentos'][-2][0]  # Nodo antes del giro
                nodo_giro = segmento_anterior['segmentos'][-1][0]      # Nodo del giro
                nodo_siguiente = segmento_actual['segmentos'][0][1]    # Nodo después del giro
                
                # Verificar que todos los nodos existen en el grafo
                if all(nodo in self.gps_peaton.grafo_peaton.nodes for nodo in [nodo_anterior, nodo_giro, nodo_siguiente]):
                    # Obtener coordenadas de los nodos
                    coord_anterior = (
                        self.gps_peaton.grafo_peaton.nodes[nodo_anterior]['x'],
                        self.gps_peaton.grafo_peaton.nodes[nodo_anterior]['y']
                    )
                    coord_giro = (
                        self.gps_peaton.grafo_peaton.nodes[nodo_giro]['x'],
                        self.gps_peaton.grafo_peaton.nodes[nodo_giro]['y']
                    )
                    coord_siguiente = (
                        self.gps_peaton.grafo_peaton.nodes[nodo_siguiente]['x'],
                        self.gps_peaton.grafo_peaton.nodes[nodo_siguiente]['y']
                    )
                    
                    # Calcular vectores de dirección
                    vec_entrada = (
                        coord_giro[0] - coord_anterior[0],  # Vector hacia el punto de giro
                        coord_giro[1] - coord_anterior[1]
                    )
                    vec_salida = (
                        coord_siguiente[0] - coord_giro[0],  # Vector saliendo del punto de giro
                        coord_siguiente[1] - coord_giro[1]
                    )
                    
                    # Calcular producto cruzado para determinar dirección
                    # Positive = giro izquierda, Negative = giro derecha
                    cross_product = (vec_entrada[0] * vec_salida[1] - vec_entrada[1] * vec_salida[0])
                    
                    if cross_product > 0:
                        return "izquierda"
                    elif cross_product < 0:
                        return "derecha"
                    
        except (KeyError, IndexError, TypeError):
            # Si hay error en el cálculo (coordenadas faltantes, etc.), usar dirección por defecto
            pass
        
        # Dirección por defecto cuando no se puede determinar
        return "derecha"
    
    def calcular_ruta_metro_completa(self, direccion_origen: str, direccion_destino: str) -> Optional[Dict]:
        """
        Calcula ruta completa en metro con instrucciones peatonales detalladas.
        
        Combina:
        - Ruta peatonal desde el origen hasta la estación de metro
        - Ruta en metro entre estaciones
        - Ruta peatonal desde la estación de metro hasta el destino
        
        Args:
            direccion_origen: Dirección de partida
            direccion_destino: Dirección de destino
            
        Returns:
            Dict con información completa de la ruta combinada o None si hay error
        """
        try:
            # Primero calcular la ruta básica de metro (solo el tramo entre estaciones)
            resultado_metro = self.gps_metro.calcular_ruta_metro(direccion_origen, direccion_destino)
            if not resultado_metro:
                return None
            
            # Obtener coordenadas de las direcciones originales para calcular rutas peatonales
            lat_origen, lon_origen, direccion_origen_hallada = busca_direccion(direccion_origen, self.gps_peaton.callejero)
            lat_destino, lon_destino, direccion_destino_hallada = busca_direccion(direccion_destino, self.gps_peaton.callejero)
            
            # Obtener coordenadas de las estaciones de metro
            estacion_origen_id = resultado_metro['camino'][0]
            estacion_destino_id = resultado_metro['camino'][-1]
            
            lat_estacion_origen = self.gps_metro.grafo_metro.nodes[estacion_origen_id]['latitud']
            lon_estacion_origen = self.gps_metro.grafo_metro.nodes[estacion_origen_id]['longitud']
            
            lat_estacion_destino = self.gps_metro.grafo_metro.nodes[estacion_destino_id]['latitud']
            lon_estacion_destino = self.gps_metro.grafo_metro.nodes[estacion_destino_id]['longitud']
            
            # Calcular ruta peatonal desde origen hasta estación de metro usando coordenadas
            ruta_hasta_metro = self._calcular_ruta_peaton_por_coordenadas(
                lat_origen, lon_origen, 
                lat_estacion_origen, lon_estacion_origen
            )
            
            # Calcular ruta peatonal desde estación de metro hasta destino usando coordenadas
            ruta_desde_metro = self._calcular_ruta_peaton_por_coordenadas(
                lat_estacion_destino, lon_estacion_destino,
                lat_destino, lon_destino
            )
            
            # Ajustar tiempo del metro: 3 minutos por segmento entre estaciones
            tiempo_metro_ajustado = 0
            for i in range(len(resultado_metro['camino']) - 1):
                tiempo_metro_ajustado += 3  # 3 minutos por segmento
            
            # Añadir tiempo de transbordos (2 minutos extra por transbordo)
            tiempo_metro_ajustado += resultado_metro['transbordos'] * 2
            
            # Calcular tiempo total caminando (hasta y desde el metro)
            tiempo_caminando_total = 0
            if ruta_hasta_metro:
                tiempo_caminando_total += ruta_hasta_metro['tiempo_total']
            if ruta_desde_metro:
                tiempo_caminando_total += ruta_desde_metro['tiempo_total']
            
            # Actualizar tiempos en el resultado (convertir a segundos)
            resultado_metro['tiempo_metro'] = tiempo_metro_ajustado * 60
            resultado_metro['tiempo_total'] = tiempo_metro_ajustado * 60 + tiempo_caminando_total
            
            # Combinar toda la información en un resultado completo
            resultado_completo = {
                **resultado_metro,
                'ruta_hasta_metro': ruta_hasta_metro,
                'ruta_desde_metro': ruta_desde_metro,
                'instrucciones_completas': self._generar_instrucciones_metro_completas(
                    resultado_metro, ruta_hasta_metro, ruta_desde_metro,
                    direccion_origen_hallada, direccion_destino_hallada
                )
            }
            
            return resultado_completo
            
        except Exception as e:
            print(f"Error calculando ruta completa de metro: {e}")
            return None
    
    def _generar_instrucciones_metro_completas(self, resultado_metro: Dict, ruta_hasta_metro: Dict, 
                                             ruta_desde_metro: Dict, direccion_origen: str, 
                                             direccion_destino: str) -> List[Dict]:
        """
        Genera instrucciones completas para ruta de metro incluyendo tramos peatonales.
        
        Args:
            resultado_metro: Resultado de la ruta de metro
            ruta_hasta_metro: Ruta peatonal hasta la estación
            ruta_desde_metro: Ruta peatonal desde la estación
            direccion_origen: Dirección de origen formateada
            direccion_destino: Dirección de destino formateada
            
        Returns:
            Lista de instrucciones de navegación completas
        """
        instrucciones = []
        
        # INICIO - Instrucción de inicio del recorrido
        instrucciones.append({
            'tipo': 'inicio_metro',
            'descripcion': f"🚶 Inicie su recorrido desde: {direccion_origen}",
            'modo': 'caminando'
        })
        
        # TRAMO 1: CAMINATA HASTA EL METRO
        if ruta_hasta_metro and 'instrucciones' in ruta_hasta_metro:
            # Solo mostrar instrucciones detalladas de caminata, no resúmenes
            for instruccion in ruta_hasta_metro['instrucciones']:
                if instruccion['tipo'] in ['continuar', 'girar']:
                    instrucciones.append({
                        'tipo': f"caminata_{instruccion['tipo']}",
                        'descripcion': instruccion['descripcion'],
                        'distancia': instruccion.get('distancia', 0),
                        'direccion': instruccion.get('direccion', ''),
                        'modo': 'caminando'
                    })
        
        # Indicar llegada a la estación de origen
        instrucciones.append({
            'tipo': 'llegada_estacion_origen',
            'descripcion': f"🏁 Ha llegado a la estación {resultado_metro['estacion_origen']}",
            'modo': 'caminando'
        })
        
        # TRAMO 2: METRO - Generar instrucciones para cada segmento del metro
        camino_metro = resultado_metro['camino']
        for i in range(len(camino_metro) - 1):
            estacion_actual = self.gps_metro.grafo_metro.nodes[camino_metro[i]]['nombre']
            estacion_siguiente = self.gps_metro.grafo_metro.nodes[camino_metro[i+1]]['nombre']
            
            if i == 0:
                # Primera instrucción de metro (tomar el metro)
                instrucciones.append({
                    'tipo': 'tomar_metro',
                    'descripcion': f"🚇 Tome el metro en {estacion_actual} hacia {estacion_siguiente}",
                    'linea': resultado_metro['lineas'][0] if resultado_metro['lineas'] else '',
                    'tiempo': 3 * 60,  # 3 minutos en segundos por segmento
                    'modo': 'metro'
                })
            else:
                # Continuar en metro hacia siguiente estación
                instrucciones.append({
                    'tipo': 'continuar_metro',
                    'descripcion': f"➡️  Continúe en metro hasta {estacion_siguiente}",
                    'linea': resultado_metro['lineas'][0] if resultado_metro['lineas'] else '',
                    'tiempo': 3 * 60,  # 3 minutos en segundos por segmento
                    'modo': 'metro'
                })
        
        # Indicar llegada a la estación de destino
        instrucciones.append({
            'tipo': 'llegada_estacion_destino',
            'descripcion': f"🏁 Ha llegado a la estación {resultado_metro['estacion_destino']}",
            'modo': 'metro'
        })
        
        # TRAMO 3: CAMINATA DESDE EL METRO
        if ruta_desde_metro and 'instrucciones' in ruta_desde_metro:
            # Solo mostrar instrucciones detalladas de caminata
            for instruccion in ruta_desde_metro['instrucciones']:
                if instruccion['tipo'] in ['continuar', 'girar']:
                    instrucciones.append({
                        'tipo': f"caminata_{instruccion['tipo']}",
                        'descripcion': instruccion['descripcion'],
                        'distancia': instruccion.get('distancia', 0),
                        'direccion': instruccion.get('direccion', ''),
                        'modo': 'caminando'
                    })
        
        # FINAL - Instrucción de llegada al destino
        instrucciones.append({
            'tipo': 'llegada_destino',
            'descripcion': f"🎯 Ha llegado a su destino: {direccion_destino}",
            'modo': 'caminando'
        })
        
        return instrucciones
    
    def analizar_mejor_ruta(self, direccion_origen: str, direccion_destino: str) -> Dict:
        """
        Analiza y compara todas las rutas disponibles para determinar la mejor opción.
        
        Calcula las tres rutas (coche, peatón, metro) y las compara por tiempo
        para recomendar la más rápida.
        
        Args:
            direccion_origen: Dirección de partida
            direccion_destino: Dirección de destino
            
        Returns:
            Dict con resultados de todas las rutas y la recomendación
        """
        print("🔍 Analizando mejores rutas...")
        
        resultados = {
            'coche': None,
            'peaton': None,
            'metro': None,
            'mejor_opcion': None,  # Modo más rápido
            'comparacion': {}      # Tiempos de cada modo
        }
        
        # Calcular todas las rutas disponibles
        resultados['coche'] = self.calcular_ruta_coche(direccion_origen, direccion_destino)
        resultados['peaton'] = self.calcular_ruta_peaton(direccion_origen, direccion_destino)
        resultados['metro'] = self.calcular_ruta_metro_completa(direccion_origen, direccion_destino)
        
        # Comparar tiempos y determinar la mejor opción
        tiempos = {}
        
        if resultados['coche']:
            tiempos['coche'] = resultados['coche']['tiempo_total']
        
        if resultados['peaton']:
            tiempos['peaton'] = resultados['peaton']['tiempo_total']
        
        if resultados['metro']:
            tiempos['metro'] = resultados['metro']['tiempo_total']
        
        # Encontrar la opción más rápida
        if tiempos:
            mejor_modo = min(tiempos, key=tiempos.get)
            resultados['mejor_opcion'] = mejor_modo
            resultados['comparacion'] = tiempos
        
        return resultados
    
    def mostrar_comparacion_rutas(self, resultados: Dict, direccion_origen: str, direccion_destino: str):
        """
        Muestra comparación detallada entre todas las rutas disponibles.
        
        Args:
            resultados: Resultados del análisis de rutas
            direccion_origen: Dirección de origen para mostrar
            direccion_destino: Dirección de destino para mostrar
        """
        print("\n" + "="*80)
        print("COMPARACIÓN DE RUTAS")
        print("="*80)
        print(f"Desde: {direccion_origen}")
        print(f"Hasta: {direccion_destino}")
        print()
        
        # Mostrar información de cada ruta disponible
        if resultados['coche']:
            ruta = resultados['coche']
            modo_coche = self.gps_coche.modo_navegacion
            print("🚗 RUTA EN COCHE:")
            print(f"   • Tiempo: {ruta['tiempo_total']/60:.1f} minutos")
            print(f"   • Distancia: {ruta['distancia_total']/1000:.1f} km")
            print(f"   • Modo: {modo_coche}")
            print(f"   • Ventaja: Directo, puerta a puerta")
            print()
        
        if resultados['peaton']:
            ruta = resultados['peaton']
            print("🚶 RUTA PEATONAL:")
            print(f"   • Tiempo: {ruta['tiempo_total']/60:.1f} minutos")
            print(f"   • Distancia: {ruta['distancia_total']/1000:.1f} km")
            print(f"   • Ventaja: Ejercicio, sin coste de transporte")
            print()
        
        if resultados['metro']:
            ruta = resultados['metro']
            tiempo_caminando_total = 0
            if ruta.get('ruta_hasta_metro'):
                tiempo_caminando_total += ruta['ruta_hasta_metro']['tiempo_total']
            if ruta.get('ruta_desde_metro'):
                tiempo_caminando_total += ruta['ruta_desde_metro']['tiempo_total']
                
            print("🚇 RUTA EN METRO:")
            print(f"   • Tiempo total: {ruta['tiempo_total']/60:.1f} minutos")
            print(f"   • Tiempo en metro: {ruta['tiempo_metro']/60:.1f} minutos")
            print(f"   • Tiempo caminando: {tiempo_caminando_total/60:.1f} minutos")
            print(f"   • Transbordos: {ruta['transbordos']}")
            print(f"   • Líneas: {', '.join(ruta['lineas'])}")
            print(f"   • Estaciones: {ruta['estacion_origen']} → {ruta['estacion_destino']}")
            print(f"   • Ventaja: Evita tráfico, buena para distancias largas")
            print()
        
        # Mostrar recomendación automática basada en el análisis
        if resultados['mejor_opcion']:
            mejor = resultados['mejor_opcion']
            tiempos = resultados['comparacion']
            
            print("💡 RECOMENDACIÓN AUTOMÁTICA:")
            if mejor == 'coche':
                print(f"   La ruta en COCHE es la más rápida")
            elif mejor == 'peaton':
                print(f"   La ruta PEATONAL es la más rápida")
            else:
                print(f"   La ruta en METRO es la más rápida")
            
            # Mostrar diferencias de tiempo con las otras opciones
            for modo, tiempo in tiempos.items():
                if modo != mejor:
                    diferencia = (tiempo - tiempos[mejor]) / 60
                    modo_nombre = 'COCHE' if modo == 'coche' else 'PEATÓN' if modo == 'peaton' else 'METRO'
                    print(f"   • {diferencia:+.1f} min vs {modo_nombre}")
        
        else:
            print("❌ No se pudieron calcular rutas para esta dirección")
        
        print("="*80)
    
    def mostrar_instrucciones_detalladas(self, resultado_ruta: Dict, tipo_ruta: str):
        """
        Muestra instrucciones detalladas según el tipo de ruta seleccionada.
        
        Args:
            resultado_ruta: Resultado de la ruta calculada
            tipo_ruta: Tipo de ruta ('coche', 'peaton', 'metro')
        """
        if not resultado_ruta:
            print("No hay ruta para mostrar")
            return
        
        # Delegar la visualización al subsistema correspondiente
        if tipo_ruta == 'coche':
            self.gps_coche.mostrar_ruta(resultado_ruta)
        elif tipo_ruta == 'peaton':
            self.gps_peaton.mostrar_ruta(resultado_ruta)
        elif tipo_ruta == 'metro':
            self._mostrar_instrucciones_metro_detalladas(resultado_ruta)
    
    def _mostrar_instrucciones_metro_detalladas(self, resultado_metro: Dict):
        """
        Muestra instrucciones detalladas para ruta de metro con tramos peatonales.
        
        Args:
            resultado_metro: Resultado de la ruta de metro completa
        """
        if not resultado_metro or 'instrucciones_completas' not in resultado_metro:
            print("No hay instrucciones detalladas de metro disponibles")
            return
        
        print("\n" + "="*70)
        print("INSTRUCCIONES DETALLADAS - RUTA EN METRO")
        print("="*70)
        
        # Mostrar resumen del viaje
        tiempo_total = resultado_metro['tiempo_total'] / 60
        tiempo_metro = resultado_metro['tiempo_metro'] / 60
        tiempo_caminando = resultado_metro['tiempo_caminando'] / 60
        transbordos = resultado_metro['transbordos']
        
        print(f"📊 RESUMEN DEL VIAJE:")
        print(f"   • Tiempo total: {tiempo_total:.1f} min")
        print(f"   • Tiempo en metro: {tiempo_metro:.1f} min")
        print(f"   • Tiempo caminando: {tiempo_caminando:.1f} min")
        print(f"   • Transbordos: {transbordos}")
        print(f"   • Líneas: {', '.join(resultado_metro['lineas'])}")
        print()
        
        # Mostrar instrucciones paso a paso
        print("🗺️  INSTRUCCIONES PASO A PASO:")
        paso_numero = 1
        
        for instruccion in resultado_metro['instrucciones_completas']:
            # Mostrar cada tipo de instrucción con formato apropiado
            if instruccion['tipo'] == 'inicio_metro':
                print(f"{paso_numero}. 🚶 {instruccion['descripcion']}")
                paso_numero += 1
                
            elif instruccion['tipo'] == 'caminata_continuar':
                print(f"{paso_numero}. 📍 {instruccion['descripcion']} ({instruccion['distancia']:.0f} m)")
                paso_numero += 1
                
            elif instruccion['tipo'] == 'caminata_girar':
                icono = "↰" if instruccion['direccion'] == 'izquierda' else "↱"
                print(f"{paso_numero}. {icono} {instruccion['descripcion']} ({instruccion['distancia']:.0f} m)")
                paso_numero += 1
                
            elif instruccion['tipo'] == 'llegada_estacion_origen':
                print(f"{paso_numero}. 🏁 {instruccion['descripcion']}")
                paso_numero += 1
                
            elif instruccion['tipo'] == 'tomar_metro':
                tiempo_min = instruccion['tiempo'] / 60
                print(f"{paso_numero}. 🚇 {instruccion['descripcion']} ({tiempo_min:.0f} min)")
                paso_numero += 1
                
            elif instruccion['tipo'] == 'continuar_metro':
                tiempo_min = instruccion['tiempo'] / 60
                print(f"{paso_numero}. ➡️  {instruccion['descripcion']} ({tiempo_min:.0f} min)")
                paso_numero += 1
                
            elif instruccion['tipo'] == 'transbordo':
                print(f"{paso_numero}. 🔄 {instruccion['descripcion']}")
                paso_numero += 1
                
            elif instruccion['tipo'] == 'llegada_estacion_destino':
                print(f"{paso_numero}. 🏁 {instruccion['descripcion']}")
                paso_numero += 1
                
            elif instruccion['tipo'] == 'llegada_destino':
                print(f"{paso_numero}. 🎯 {instruccion['descripcion']}")
                paso_numero += 1
        
        print("="*70)
    
    def visualizar_ruta(self, resultado_ruta: Dict, tipo_ruta: str):
        """
        Visualiza la ruta seleccionada en el mapa.
        
        Args:
            resultado_ruta: Resultado de la ruta calculada
            tipo_ruta: Tipo de ruta ('coche', 'peaton', 'metro')
        """
        if not resultado_ruta:
            print("No hay ruta para visualizar")
            return
        
        try:
            # Delegar la visualización al subsistema correspondiente
            if tipo_ruta == 'coche':
                self.gps_coche.visualizar_ruta(resultado_ruta)
            elif tipo_ruta == 'peaton':
                self.gps_peaton.visualizar_ruta(resultado_ruta)
            elif tipo_ruta == 'metro':
                self.gps_metro.visualizar_ruta_metro(resultado_ruta)
        except Exception as e:
            print(f"Error en la visualización: {e}")


def main():
    """
    Función principal del sistema GPS integrado.
    
    Maneja la interfaz de usuario y coordina las operaciones del sistema.
    """
    # Inicializar el sistema GPS integrado
    gps = GPSIntegrado()
    
    if not gps.inicializar_sistema():
        print("No se pudo inicializar el sistema. Saliendo...")
        return
    
    # Mostrar cabecera del sistema
    print("\n" + "="*50)
    print("SISTEMA DE NAVEGACIÓN GPS INTEGRADO")
    print("="*50)
    print("Modos de transporte: 🚗 Coche | 🚶 Peatón | 🚇 Metro")
    print("="*50)
    
    # Bucle principal de la interfaz de usuario
    while True:
        print("\n📍 OPCIONES PRINCIPALES:")
        print("1. Automático (recomendación inteligente)")
        print("2. Manual (seleccionar modo específico)")
        print("3. Salir")
        
        opcion = input("\nSeleccione una opción (1-3): ").strip()
        
        if opcion == "1":
            # MODO AUTOMÁTICO: Análisis y recomendación inteligente
            origen = input("Dirección de origen: ").strip()
            destino = input("Dirección de destino: ").strip()
            
            if origen and destino:
                gps.configurar_modo_navegacion("auto")
                # Calcular y comparar todas las rutas
                resultados = gps.analizar_mejor_ruta(origen, destino)
                gps.mostrar_comparacion_rutas(resultados, origen, destino)
                
                # Mostrar la ruta recomendada
                if resultados['mejor_opcion']:
                    mejor_ruta = resultados[resultados['mejor_opcion']]
                    print(f"\n💡 Mostrando ruta recomendada: {resultados['mejor_opcion'].upper()}")
                    gps.mostrar_instrucciones_detalladas(mejor_ruta, resultados['mejor_opcion'])
                    
                    # Ofrecer visualización en mapa
                    visualizar = input("\n¿Desea visualizar la ruta en el mapa? (s/n): ").strip().lower()
                    if visualizar == 's':
                        gps.visualizar_ruta(mejor_ruta, resultados['mejor_opcion'])
            else:
                print("Debe ingresar tanto origen como destino")
                
        elif opcion == "2":
            # MODO MANUAL: Selección específica de modo de transporte
            print("\n🚦 SELECCIONAR MODO DE TRANSPORTE:")
            print("a. Coche")
            print("b. Andando")
            print("c. Metro")
            
            modo_opcion = input("Seleccione modo (a/b/c): ").strip().lower()
            
            origen = input("Dirección de origen: ").strip()
            destino = input("Dirección de destino: ").strip()
            
            if not origen or not destino:
                print("Debe ingresar tanto origen como destino")
                continue
                
            if modo_opcion == "a":
                # CONFIGURACIÓN DE COCHE: Selección de criterio de optimización
                print("\n🚗 CONFIGURAR MODO DE COCHE:")
                print("1. Distancia (ruta más corta)")
                print("2. Tiempo (ruta más rápida)")
                print("3. Semáforos (optimizada para cruces)")
                
                modo_coche = input("Seleccione modo (1-3): ").strip()
                
                # Configurar modo de coche según selección
                if modo_coche == "1":
                    gps.configurar_modo_coche("distancia")
                elif modo_coche == "2":
                    gps.configurar_modo_coche("tiempo")
                elif modo_coche == "3":
                    gps.configurar_modo_coche("semaforos")
                else:
                    print("Opción no válida, usando modo por defecto: distancia")
                    gps.configurar_modo_coche("distancia")
                
                # Calcular y mostrar ruta en coche
                resultado = gps.calcular_ruta_coche(origen, destino)
                if resultado:
                    gps.mostrar_instrucciones_detalladas(resultado, 'coche')
                    visualizar = input("\n¿Desea visualizar la ruta en el mapa? (s/n): ").strip().lower()
                    if visualizar == 's':
                        gps.visualizar_ruta(resultado, 'coche')
                else:
                    print("No se pudo calcular la ruta en coche")
                    
            elif modo_opcion == "b":
                # RUTA PEATONAL: Cálculo directo
                resultado = gps.calcular_ruta_peaton(origen, destino)
                if resultado:
                    gps.mostrar_instrucciones_detalladas(resultado, 'peaton')
                    visualizar = input("\n¿Desea visualizar la ruta en el mapa? (s/n): ").strip().lower()
                    if visualizar == 's':
                        gps.visualizar_ruta(resultado, 'peaton')
                else:
                    print("No se pudo calcular la ruta peatonal")
                    
            elif modo_opcion == "c":
                # RUTA DE METRO: Incluye tramos peatonales automáticamente
                resultado = gps.calcular_ruta_metro_completa(origen, destino)
                if resultado:
                    gps.mostrar_instrucciones_detalladas(resultado, 'metro')
                    visualizar = input("\n¿Desea visualizar la ruta en el mapa? (s/n): ").strip().lower()
                    if visualizar == 's':
                        gps.visualizar_ruta(resultado, 'metro')
                else:
                    print("No se pudo calcular la ruta en metro")
            else:
                print("Opción no válida")
                
        elif opcion == "3":
            # SALIR del sistema
            print("Saliendo del sistema GPS Integrado...")
            break
            
        else:
            print("Opción no válida. Por favor seleccione 1, 2 o 3.")


if __name__ == "__main__":
    # Punto de entrada del programa
    main()