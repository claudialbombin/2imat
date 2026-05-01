"""
gps_metro.py

Sistema de navegación GPS especializado en transporte público (metro) de Madrid
OJO: Este sistema no incluye información sobre el tráfico en tiempo real y solo incluye metro principal (no metroli ni buses, eso ya era una fumada historica)
SOLO calcula el metro, no permite ni conducir ni andar ni nada.
Con todas las líneas del metro (1-12 + Ramal)
"""

import pandas as pd
import networkx as nx
from typing import Tuple, List, Dict, Optional
import matplotlib.pyplot as plt
from callejero import carga_callejero, busca_direccion, AdressNotFoundError
from grafo_pesado import dijkstra, camino_minimo


class GPSMetro:
    """
    Sistema de navegación GPS que calcula rutas óptimas en el metro de Madrid
    utilizando algoritmos de grafos.
    """
    
    def __init__(self):
        """
        Inicializa el sistema GPS Metro cargando el callejero y la red de metro.
        """
        # Callejero de Madrid para buscar direcciones
        self.callejero = None
        # Estructura con todas las estaciones de metro
        self.red_metro = None
        # Grafo donde los nodos son estaciones y las aristas son conexiones
        self.grafo_metro = None
        # Modo de navegación (solo metro en este caso)
        self.modo_navegacion = "metro"
    
    def inicializar_sistema(self) -> bool:
        """
        Carga todos los datos necesarios para el funcionamiento del GPS Metro.
        """
        try:
            print("Inicializando sistema GPS Metro...")
            
            # Cargar callejero de Madrid para buscar direcciones
            self.callejero = carga_callejero()
            
            # Cargar red de metro con todas las estaciones y sus conexiones
            self.red_metro = self._crear_red_metro_completa()
            
            # Crear grafo del metro donde aplicaremos Dijkstra
            self.grafo_metro = self._crear_grafo_metro_completo()

            print("Sistema GPS Metro inicializado correctamente")

            # Verificamos que todas las estaciones estén conectadas
            self.verificar_conectividad()
            return True
            
        except Exception as e:
            print(f"Error durante la inicialización: {e}")
            return False
        
    def _crear_red_metro_completa(self) -> Dict:
        """
        Crea una red de metro completa con TODAS las líneas del metro de Madrid.
        Incluye coordenadas reales de cada estación.
        """
        # Diccionario gigante con todas las estaciones del metro de Madrid
        # Cada estación tiene: nombre, coordenadas (lat, lon), y líneas que pasan
        estaciones_completas = {
            # ===== LÍNEA 1 =====
            'PINAR_CHAMARTIN': {'nombre': 'PINAR DE CHAMARTIN', 'latitud': 40.48014, 'longitud': -3.6668, 'lineas': {'1'}},
            'BAMBU': {'nombre': 'BAMBU', 'latitud': 40.47682, 'longitud': -3.67637, 'lineas': {'1'}},
            'CHAMARTIN': {'nombre': 'CHAMARTIN', 'latitud': 40.47203, 'longitud': -3.68259, 'lineas': {'1', '10'}},
            'PLAZA_CASTILLA': {'nombre': 'PLAZA DE CASTILLA', 'latitud': 40.4669, 'longitud': -3.68917, 'lineas': {'1', '9', '10'}},
            'VALDEACEDERAS': {'nombre': 'VALDEACEDERAS', 'latitud': 40.46442, 'longitud': -3.69506, 'lineas': {'1'}},
            'TETUAN': {'nombre': 'TETUAN', 'latitud': 40.46055, 'longitud': -3.69825, 'lineas': {'1'}},
            'ESTRECHO': {'nombre': 'ESTRECHO', 'latitud': 40.45429, 'longitud': -3.70302, 'lineas': {'1'}},
            'ALVARADO': {'nombre': 'ALVARADO', 'latitud': 40.45033, 'longitud': -3.70331, 'lineas': {'1'}},
            'CUATRO_CAMINOS': {'nombre': 'CUATRO CAMINOS', 'latitud': 40.44697, 'longitud': -3.70397, 'lineas': {'1', '2', '6'}},
            'RIOS_ROSAS': {'nombre': 'RIOS ROSAS', 'latitud': 40.44198, 'longitud': -3.70133, 'lineas': {'1'}},
            'IGLESIA': {'nombre': 'IGLESIA', 'latitud': 40.43492, 'longitud': -3.69898, 'lineas': {'1'}},
            'BILBAO': {'nombre': 'BILBAO', 'latitud': 40.42906, 'longitud': -3.70218, 'lineas': {'1', '4'}},
            'TRIBUNAL': {'nombre': 'TRIBUNAL', 'latitud': 40.42619, 'longitud': -3.7011, 'lineas': {'1', '10'}},
            'GRAN_VIA': {'nombre': 'GRAN VIA', 'latitud': 40.42001, 'longitud': -3.7018, 'lineas': {'1', '5'}},
            'SOL': {'nombre': 'SOL', 'latitud': 40.41688, 'longitud': -3.70326, 'lineas': {'1', '2', '3'}},
            'TIRSO_MOLINA': {'nombre': 'TIRSO DE MOLINA', 'latitud': 40.41235, 'longitud': -3.70466, 'lineas': {'1'}},
            'ANTON_MARTIN': {'nombre': 'ANTON MARTIN', 'latitud': 40.41246, 'longitud': -3.69937, 'lineas': {'1'}},
            'ESTACION_ARTE': {'nombre': 'ESTACION DEL ARTE', 'latitud': 40.40885, 'longitud': -3.69249, 'lineas': {'1'}},
            'ATOCHA': {'nombre': 'ATOCHA', 'latitud': 40.40659, 'longitud': -3.68938, 'lineas': {'1'}},
            'MENENDEZ_PELAYO': {'nombre': 'MENENDEZ PELAYO', 'latitud': 40.40445, 'longitud': -3.68098, 'lineas': {'1'}},
            'PACIFICO': {'nombre': 'PACIFICO', 'latitud': 40.40126, 'longitud': -3.67514, 'lineas': {'1', '6'}},
            'PUENTE_VALLECAS': {'nombre': 'PUENTE DE VALLECAS', 'latitud': 40.39819, 'longitud': -3.66906, 'lineas': {'1'}},
            'NUEVA_NUMANCIA': {'nombre': 'NUEVA NUMANCIA', 'latitud': 40.39554, 'longitud': -3.66414, 'lineas': {'1'}},
            'PORTAZGO': {'nombre': 'PORTAZGO', 'latitud': 40.39266, 'longitud': -3.65868, 'lineas': {'1'}},
            'BUENOS_AIRES': {'nombre': 'BUENOS AIRES', 'latitud': 40.39156, 'longitud': -3.65391, 'lineas': {'1'}},
            'ALTO_ARENAL': {'nombre': 'ALTO DEL ARENAL', 'latitud': 40.38977, 'longitud': -3.64522, 'lineas': {'1'}},
            'MIGUEL_HERNANDEZ': {'nombre': 'MIGUEL HERNANDEZ', 'latitud': 40.38732, 'longitud': -3.63951, 'lineas': {'1'}},
            'SIERRA_GUADALUPE': {'nombre': 'SIERRA DE GUADALUPE', 'latitud': 40.38216, 'longitud': -3.62472, 'lineas': {'1'}},
            'VILLA_VALLECAS': {'nombre': 'VILLA DE VALLECAS', 'latitud': 40.3796, 'longitud': -3.6213, 'lineas': {'1'}},
            'CONGOSTO': {'nombre': 'CONGOSTO', 'latitud': 40.37238, 'longitud': -3.61884, 'lineas': {'1'}},
            'LA_GAVIA': {'nombre': 'LA GAVIA', 'latitud': 40.37019, 'longitud': -3.61346, 'lineas': {'1'}},
            'LAS_SUERTES': {'nombre': 'LAS SUERTES', 'latitud': 40.36323, 'longitud': -3.59953, 'lineas': {'1'}},
            'VALDECARROS': {'nombre': 'VALDECARROS', 'latitud': 40.36007, 'longitud': -3.59316, 'lineas': {'1'}},
            
            # ===== LÍNEA 2 =====
            'LAS_ROSAS': {'nombre': 'LAS ROSAS', 'latitud': 40.42375, 'longitud': -3.60331, 'lineas': {'2'}},
            'AVENIDA_GUADALAJARA': {'nombre': 'AVENIDA DE GUADALAJARA', 'latitud': 40.42239, 'longitud': -3.61206, 'lineas': {'2'}},
            'ALSACIA': {'nombre': 'ALSACIA', 'latitud': 40.41829, 'longitud': -3.62351, 'lineas': {'2'}},
            'LA_ALMUDENA': {'nombre': 'LA ALMUDENA', 'latitud': 40.42361, 'longitud': -3.63914, 'lineas': {'2'}},
            'LA_ELIPA': {'nombre': 'LA ELIPA', 'latitud': 40.42662, 'longitud': -3.65052, 'lineas': {'2'}},
            'VENTAS': {'nombre': 'VENTAS', 'latitud': 40.43088, 'longitud': -3.66366, 'lineas': {'2', '5'}},
            'MANUEL_BECERRA': {'nombre': 'MANUEL BECERRA', 'latitud': 40.4279, 'longitud': -3.66926, 'lineas': {'2', '6'}},
            'GOYA': {'nombre': 'GOYA', 'latitud': 40.42455, 'longitud': -3.67591, 'lineas': {'2', '4'}},
            'PRINCIPE_VERGARA': {'nombre': 'PRINCIPE DE VERGARA', 'latitud': 40.42294, 'longitud': -3.68012, 'lineas': {'2', '9'}},
            'RETIRO': {'nombre': 'RETIRO', 'latitud': 40.42031, 'longitud': -3.68624, 'lineas': {'2'}},
            'BANCO_ESPANA': {'nombre': 'BANCO DE ESPAÑA', 'latitud': 40.41922, 'longitud': -3.69497, 'lineas': {'2'}},
            'SEVILLA': {'nombre': 'SEVILLA', 'latitud': 40.41805, 'longitud': -3.69925, 'lineas': {'2'}},
            'OPERA': {'nombre': 'OPERA', 'latitud': 40.41809, 'longitud': -3.70942, 'lineas': {'2', '5', 'R'}},
            'SANTO_DOMINGO': {'nombre': 'SANTO DOMINGO', 'latitud': 40.42132, 'longitud': -3.70796, 'lineas': {'2'}},
            'NOVICIADO': {'nombre': 'NOVICIADO', 'latitud': 40.42484, 'longitud': -3.70742, 'lineas': {'2'}},
            'SAN_BERNARDO': {'nombre': 'SAN BERNARDO', 'latitud': 40.43001, 'longitud': -3.70557, 'lineas': {'2', '4'}},
            'QUEVEDO': {'nombre': 'QUEVEDO', 'latitud': 40.43322, 'longitud': -3.70433, 'lineas': {'2'}},
            'CANAL': {'nombre': 'CANAL', 'latitud': 40.43841, 'longitud': -3.70433, 'lineas': {'2', '7'}},
            
            # ===== LÍNEA 3 =====
            'VILLAVERDE_ALTO': {'nombre': 'VILLAVERDE ALTO', 'latitud': 40.34123, 'longitud': -3.71199, 'lineas': {'3'}},
            'SAN_CRISTOBAL': {'nombre': 'SAN CRISTOBAL', 'latitud': 40.34154, 'longitud': -3.69318, 'lineas': {'3'}},
            'VILLAVERDE_CRUCE': {'nombre': 'VILLAVERDE BAJO CRUCE', 'latitud': 40.35089, 'longitud': -3.69265, 'lineas': {'3'}},
            'CIUDAD_ANGELES': {'nombre': 'CIUDAD DE LOS ANGELES', 'latitud': 40.35959, 'longitud': -3.69363, 'lineas': {'3'}},
            'SAN_FERMIN': {'nombre': 'SAN FERMIN-ORCASUR', 'latitud': 40.36999, 'longitud': -3.69418, 'lineas': {'3', '6'}},
            'HOSPITAL_12_OCTUBRE': {'nombre': 'HOSPITAL 12 DE OCTUBRE', 'latitud': 40.37503, 'longitud': -3.69585, 'lineas': {'3'}},
            'ALMENDRALES': {'nombre': 'ALMENDRALES', 'latitud': 40.38409, 'longitud': -3.69788, 'lineas': {'3'}},
            'LEGAZPI': {'nombre': 'LEGAZPI', 'latitud': 40.39116, 'longitud': -3.69511, 'lineas': {'3', '6'}},
            'DELICIAS': {'nombre': 'DELICIAS', 'latitud': 40.3999, 'longitud': -3.6942, 'lineas': {'3'}},
            'PALOS_FRONTERA': {'nombre': 'PALOS DE LA FRONTERA', 'latitud': 40.40307, 'longitud': -3.69423, 'lineas': {'3'}},
            'EMBAJADORES': {'nombre': 'EMBAJADORES', 'latitud': 40.40513, 'longitud': -3.70268, 'lineas': {'3'}},
            'LAVAPIES': {'nombre': 'LAVAPIES', 'latitud': 40.40851, 'longitud': -3.7009, 'lineas': {'3'}},
            'CALLAO': {'nombre': 'CALLAO', 'latitud': 40.42014, 'longitud': -3.70566, 'lineas': {'3', '5'}},
            'PLAZA_ESPANA': {'nombre': 'PLAZA DE ESPAÑA', 'latitud': 40.42342, 'longitud': -3.7112, 'lineas': {'3', '10'}},
            'VENTURA_RODRIGUEZ': {'nombre': 'VENTURA RODRIGUEZ', 'latitud': 40.42709, 'longitud': -3.71341, 'lineas': {'3'}},
            'ARGUELLES': {'nombre': 'ARGÜELLES', 'latitud': 40.43066, 'longitud': -3.71596, 'lineas': {'3', '4', '6'}},
            'MONCLOA': {'nombre': 'MONCLOA', 'latitud': 40.43502, 'longitud': -3.71945, 'lineas': {'3', '6'}},
            
            # ===== LÍNEA 4 =====
            'ARGANZUELA': {'nombre': 'ARGANZUELA-PLANETARIO', 'latitud': 40.3931, 'longitud': -3.68864, 'lineas': {'4'}},
            'MENDEZ_ALVARO': {'nombre': 'MENDEZ ALVARO', 'latitud': 40.39538, 'longitud': -3.67814, 'lineas': {'4', '6'}},
            'PACIFICO_L4': {'nombre': 'PACIFICO', 'latitud': 40.40207, 'longitud': -3.67386, 'lineas': {'4', '6'}},
            'ARTURO_SORIA': {'nombre': 'ARTURO SORIA', 'latitud': 40.45583, 'longitud': -3.65618, 'lineas': {'4'}},
            'ESPERANZA': {'nombre': 'ESPERANZA', 'latitud': 40.45945, 'longitud': -3.64582, 'lineas': {'4'}},
            'CANILLAS': {'nombre': 'CANILLAS', 'latitud': 40.46381, 'longitud': -3.6356, 'lineas': {'4'}},
            'MAR_CRISTAL': {'nombre': 'MAR DE CRISTAL', 'latitud': 40.46943, 'longitud': -3.63832, 'lineas': {'4', '8'}},
            'SAN_LORENZO': {'nombre': 'SAN LORENZO', 'latitud': 40.47447, 'longitud': -3.63958, 'lineas': {'4'}},
            'PARQUE_SANTA_MARIA': {'nombre': 'PARQUE DE SANTA MARIA', 'latitud': 40.47711, 'longitud': -3.64524, 'lineas': {'4'}},
            'HORTALEZA': {'nombre': 'HORTALEZA', 'latitud': 40.47537, 'longitud': -3.65257, 'lineas': {'4'}},
            'MANOTERAS': {'nombre': 'MANOTERAS', 'latitud': 40.47687, 'longitud': -3.6629, 'lineas': {'4'}},
            'PINAR_CHAMARTIN_L4': {'nombre': 'PINAR DE CHAMARTIN', 'latitud': 40.48014, 'longitud': -3.6668, 'lineas': {'1', '4'}},
            'DIEGO_LEON': {'nombre': 'DIEGO DE LEON', 'latitud': 40.43468, 'longitud': -3.67495, 'lineas': {'4', '5', '6'}},
            'LISTA': {'nombre': 'LISTA', 'latitud': 40.42917, 'longitud': -3.67541, 'lineas': {'4'}},
            'VELAZQUEZ': {'nombre': 'VELAZQUEZ', 'latitud': 40.42503, 'longitud': -3.68292, 'lineas': {'4'}},
            'SERRANO': {'nombre': 'SERRANO', 'latitud': 40.42543, 'longitud': -3.68663, 'lineas': {'4'}},
            'COLON': {'nombre': 'COLON', 'latitud': 40.42542, 'longitud': -3.69101, 'lineas': {'4'}},
            'ALONSO_MARTINEZ': {'nombre': 'ALONSO MARTINEZ', 'latitud': 40.42772, 'longitud': -3.69594, 'lineas': {'4', '5', '10'}},
            
            # ===== LÍNEA 5 =====
            'ALAMEDA_OSUNA': {'nombre': 'ALAMEDA DE OSUNA', 'latitud': 40.45779, 'longitud': -3.58752, 'lineas': {'5'}},
            'EL_CAPRICHO': {'nombre': 'EL CAPRICHO', 'latitud': 40.45347, 'longitud': -3.59401, 'lineas': {'5'}},
            'CANILLEJAS': {'nombre': 'CANILLEJAS', 'latitud': 40.44942, 'longitud': -3.60816, 'lineas': {'5', '7'}},
            'TORRE_ARIAS': {'nombre': 'TORRE ARIAS', 'latitud': 40.44374, 'longitud': -3.61699, 'lineas': {'5'}},
            'SUANZES': {'nombre': 'SUANZES', 'latitud': 40.44085, 'longitud': -3.62684, 'lineas': {'5'}},
            'CIUDAD_LINEAL': {'nombre': 'CIUDAD LINEAL', 'latitud': 40.43805, 'longitud': -3.63816, 'lineas': {'5'}},
            'PUEBLO_NUEVO': {'nombre': 'PUEBLO NUEVO', 'latitud': 40.43569, 'longitud': -3.64282, 'lineas': {'5'}},
            'QUINTANA': {'nombre': 'QUINTANA', 'latitud': 40.43358, 'longitud': -3.64736, 'lineas': {'5'}},
            'EL_CARMEN': {'nombre': 'EL CARMEN', 'latitud': 40.43189, 'longitud': -3.65757, 'lineas': {'5'}},
            'RUBEN_DARIO': {'nombre': 'RUBEN DARIO', 'latitud': 40.43316, 'longitud': -3.68954, 'lineas': {'5'}},
            'NUÑEZ_BALBOA': {'nombre': 'NUÑEZ DE BALBOA', 'latitud': 40.43278, 'longitud': -3.68258, 'lineas': {'5'}},
            'CHUECA': {'nombre': 'CHUECA', 'latitud': 40.42293, 'longitud': -3.69762, 'lineas': {'5'}},
            'LA_LATINA': {'nombre': 'LA LATINA', 'latitud': 40.41128, 'longitud': -3.70816, 'lineas': {'5'}},
            'PUERTA_TOLEDO': {'nombre': 'PUERTA DE TOLEDO', 'latitud': 40.40704, 'longitud': -3.71105, 'lineas': {'5'}},
            'ACACIAS': {'nombre': 'ACACIAS', 'latitud': 40.40387, 'longitud': -3.70664, 'lineas': {'5'}},
            'PIRAMIDES': {'nombre': 'PIRAMIDES', 'latitud': 40.4026, 'longitud': -3.71138, 'lineas': {'5'}},
            'MARQUES_VADILLO': {'nombre': 'MARQUES DE VADILLO', 'latitud': 40.39736, 'longitud': -3.71596, 'lineas': {'5'}},
            'URGEL': {'nombre': 'URGEL', 'latitud': 40.39335, 'longitud': -3.7236, 'lineas': {'5'}},
            'OPORTO': {'nombre': 'OPORTO', 'latitud': 40.38846, 'longitud': -3.73132, 'lineas': {'5'}},
            'VISTA_ALEGRE': {'nombre': 'VISTA ALEGRE', 'latitud': 40.38885, 'longitud': -3.73982, 'lineas': {'5'}},
            'CARABANCHEL': {'nombre': 'CARABANCHEL', 'latitud': 40.38783, 'longitud': -3.74487, 'lineas': {'5'}},
            'EUGENIA_MONTIJO': {'nombre': 'EUGENIA DE MONTIJO', 'latitud': 40.38439, 'longitud': -3.75121, 'lineas': {'5'}},
            'ALUCHE': {'nombre': 'ALUCHE', 'latitud': 40.38563, 'longitud': -3.7608, 'lineas': {'5', '10'}},
            'EMPALME': {'nombre': 'EMPALME', 'latitud': 40.39057, 'longitud': -3.76535, 'lineas': {'5'}},
            'CAMPAMENTO': {'nombre': 'CAMPAMENTO', 'latitud': 40.39481, 'longitud': -3.76813, 'lineas': {'5'}},
            'CASA_CAMPO': {'nombre': 'CASA DE CAMPO', 'latitud': 40.40324, 'longitud': -3.76101, 'lineas': {'5', '10'}},
            
            # ===== LÍNEA 6 =====
            'LAGUNA': {'nombre': 'LAGUNA', 'latitud': 40.39923, 'longitud': -3.74429, 'lineas': {'6'}},
            'CARPETANA': {'nombre': 'CARPETANA', 'latitud': 40.3927, 'longitud': -3.74099, 'lineas': {'6'}},
            'OPAÑEL': {'nombre': 'OPAÑEL', 'latitud': 40.3869, 'longitud': -3.72313, 'lineas': {'6'}},
            'PLAZA_ELIPTICA': {'nombre': 'PLAZA ELIPTICA', 'latitud': 40.3846, 'longitud': -3.71837, 'lineas': {'6', '11'}},
            'USERA': {'nombre': 'USERA', 'latitud': 40.3871, 'longitud': -3.7069, 'lineas': {'6'}},
            'LEGAZPI_L6': {'nombre': 'LEGAZPI', 'latitud': 40.39116, 'longitud': -3.69505, 'lineas': {'3', '6'}},
            'ARGANZUELA_L6': {'nombre': 'ARGANZUELA-PLANETARIO', 'latitud': 40.3931, 'longitud': -3.68864, 'lineas': {'4', '6'}},
            'MENDEZ_ALVARO_L6': {'nombre': 'MENDEZ ALVARO', 'latitud': 40.39538, 'longitud': -3.67814, 'lineas': {'4', '6'}},
            'PACIFICO_L6': {'nombre': 'PACIFICO', 'latitud': 40.40207, 'longitud': -3.67386, 'lineas': {'4', '6'}},
            'CONDE_CASAL': {'nombre': 'CONDE DE CASAL', 'latitud': 40.40697, 'longitud': -3.67041, 'lineas': {'6'}},
            'SAINZ_BARANDA': {'nombre': 'SAINZ DE BARANDA', 'latitud': 40.41507, 'longitud': -3.66951, 'lineas': {'6'}},
            'ODONNELL': {'nombre': 'ODONNELL', 'latitud': 40.42289, 'longitud': -3.6686, 'lineas': {'6'}},
            'MANUEL_BECERRA_L6': {'nombre': 'MANUEL BECERRA', 'latitud': 40.4279, 'longitud': -3.66921, 'lineas': {'2', '6'}},
            'DIEGO_LEON_L6': {'nombre': 'DIEGO DE LEON', 'latitud': 40.43295, 'longitud': -3.67294, 'lineas': {'4', '5', '6'}},
            'AVENIDA_AMERICA': {'nombre': 'AVENIDA DE AMERICA', 'latitud': 40.43803, 'longitud': -3.67664, 'lineas': {'6', '7', '9'}},
            'REPUBLICA_ARGENTINA': {'nombre': 'REPUBLICA ARGENTINA', 'latitud': 40.44379, 'longitud': -3.68406, 'lineas': {'6'}},
            'NUEVOS_MINISTERIOS': {'nombre': 'NUEVOS MINISTERIOS', 'latitud': 40.44662, 'longitud': -3.69241, 'lineas': {'6', '8', '10'}},
            'GUZMAN_EL_BUENO': {'nombre': 'GUZMAN EL BUENO', 'latitud': 40.44637, 'longitud': -3.71229, 'lineas': {'6', '7'}},
            'VICENTE_ALEIXANDRE': {'nombre': 'VICENTE ALEIXANDRE', 'latitud': 40.44644, 'longitud': -3.71943, 'lineas': {'6'}},
            'CIUDAD_UNIVERSITARIA': {'nombre': 'CIUDAD UNIVERSITARIA', 'latitud': 40.44356, 'longitud': -3.72678, 'lineas': {'6'}},
            'MONCLOA_L6': {'nombre': 'MONCLOA', 'latitud': 40.43497, 'longitud': -3.71945, 'lineas': {'3', '6'}},
            'ARGUELLES_L6': {'nombre': 'ARGÜELLES', 'latitud': 40.43053, 'longitud': -3.71596, 'lineas': {'3', '4', '6'}},
            'PRINCIPE_PIO': {'nombre': 'PRINCIPE PIO', 'latitud': 40.42107, 'longitud': -3.72032, 'lineas': {'6', '10', 'R'}},
            'PUERTA_ANGEL': {'nombre': 'PUERTA DEL ANGEL', 'latitud': 40.4139, 'longitud': -3.72724, 'lineas': {'6'}},
            'ALTO_EXTREMADURA': {'nombre': 'ALTO DE EXTREMADURA', 'latitud': 40.40993, 'longitud': -3.73894, 'lineas': {'6'}},
            'LUCERO': {'nombre': 'LUCERO', 'latitud': 40.4051, 'longitud': -3.74534, 'lineas': {'6'}},
            
            # ===== LÍNEA 7 =====
            'PITIS': {'nombre': 'PITIS', 'latitud': 40.49511, 'longitud': -3.72589, 'lineas': {'7'}},
            'ARROYO_FRESNO': {'nombre': 'ARROYOFRESNO', 'latitud': 40.4909, 'longitud': -3.72604, 'lineas': {'7'}},
            'LACOMA': {'nombre': 'LACOMA', 'latitud': 40.48502, 'longitud': -3.72305, 'lineas': {'7'}},
            'AVENIDA_ILUSTRACION': {'nombre': 'AVENIDA DE LA ILUSTRACION', 'latitud': 40.4801, 'longitud': -3.7184, 'lineas': {'7'}},
            'PEÑAGRANDE': {'nombre': 'PEÑAGRANDE', 'latitud': 40.47592, 'longitud': -3.71582, 'lineas': {'7'}},
            'ANTONIO_MACHADO': {'nombre': 'ANTONIO MACHADO', 'latitud': 40.47022, 'longitud': -3.71769, 'lineas': {'7'}},
            'VALDEZARZA': {'nombre': 'VALDEZARZA', 'latitud': 40.46482, 'longitud': -3.71597, 'lineas': {'7'}},
            'FRANCOS_RODRIGUEZ': {'nombre': 'FRANCOS RODRIGUEZ', 'latitud': 40.45648, 'longitud': -3.71239, 'lineas': {'7'}},
            'ISLAS_FILIPINAS': {'nombre': 'ISLAS FILIPINAS', 'latitud': 40.43907, 'longitud': -3.71373, 'lineas': {'7'}},
            'ALONSO_CANO': {'nombre': 'ALONSO CANO', 'latitud': 40.43838, 'longitud': -3.69925, 'lineas': {'7'}},
            'GREGORIO_MARAÑON': {'nombre': 'GREGORIO MARAÑON', 'latitud': 40.43825, 'longitud': -3.69148, 'lineas': {'7', '10'}},
            'AVENIDA_AMERICA_L7': {'nombre': 'AVENIDA DE AMERICA', 'latitud': 40.43804, 'longitud': -3.67658, 'lineas': {'6', '7', '9'}},
            'CARTAGENA': {'nombre': 'CARTAGENA', 'latitud': 40.43934, 'longitud': -3.67215, 'lineas': {'7'}},
            'PARQUE_AVENIDAS': {'nombre': 'PARQUE DE LAS AVENIDAS', 'latitud': 40.43945, 'longitud': -3.66297, 'lineas': {'7'}},
            'BARRIO_CONCEPCION': {'nombre': 'BARRIO DE LA CONCEPCION', 'latitud': 40.4391, 'longitud': -3.652, 'lineas': {'7'}},
            'ASCAO': {'nombre': 'ASCAO', 'latitud': 40.43021, 'longitud': -3.64106, 'lineas': {'7'}},
            'GARCIA_NOBLEJAS': {'nombre': 'GARCIA NOBLEJAS', 'latitud': 40.42842, 'longitud': -3.6333, 'lineas': {'7'}},
            'SIMANCAS': {'nombre': 'SIMANCAS', 'latitud': 40.42799, 'longitud': -3.62572, 'lineas': {'7'}},
            'SAN_BLAS': {'nombre': 'SAN BLAS', 'latitud': 40.42799, 'longitud': -3.61547, 'lineas': {'7'}},
            'LAS_MUSAS': {'nombre': 'LAS MUSAS', 'latitud': 40.43299, 'longitud': -3.60788, 'lineas': {'7'}},
            'ESTADIO_METROPOLITANO': {'nombre': 'ESTADIO METROPOLITANO', 'latitud': 40.43339, 'longitud': -3.60015, 'lineas': {'7'}},
            'BARRIO_PUERTO': {'nombre': 'BARRIO DEL PUERTO', 'latitud': 40.4225, 'longitud': -3.56919, 'lineas': {'7'}},
            'COSLADA_CENTRAL': {'nombre': 'COSLADA CENTRAL', 'latitud': 40.42374, 'longitud': -3.56119, 'lineas': {'7'}},
            'LA_RAMBLA': {'nombre': 'LA RAMBLA', 'latitud': 40.42514, 'longitud': -3.54792, 'lineas': {'7'}},
            'SAN_FERNANDO': {'nombre': 'SAN FERNANDO', 'latitud': 40.42441, 'longitud': -3.53541, 'lineas': {'7'}},
            'JARAMA': {'nombre': 'JARAMA', 'latitud': 40.42295, 'longitud': -3.52549, 'lineas': {'7'}},
            'HENARES': {'nombre': 'HENARES', 'latitud': 40.41777, 'longitud': -3.52718, 'lineas': {'7'}},
            'HOSPITAL_HENARES': {'nombre': 'HOSPITAL DEL HENARES', 'latitud': 40.41761, 'longitud': -3.53453, 'lineas': {'7'}},
            
            # ===== LÍNEA 8 =====
            'AEROPUERTO_T4': {'nombre': 'AEROPUERTO T-4', 'latitud': 40.49177, 'longitud': -3.59325, 'lineas': {'8'}},
            'BARAJAS': {'nombre': 'BARAJAS', 'latitud': 40.47577, 'longitud': -3.58253, 'lineas': {'8'}},
            'AEROPUERTO_T1_T2_T3': {'nombre': 'AEROPUERTO T1-T2-T3', 'latitud': 40.46864, 'longitud': -3.56954, 'lineas': {'8'}},
            'FERIA_MADRID': {'nombre': 'FERIA DE MADRID', 'latitud': 40.46389, 'longitud': -3.6162, 'lineas': {'8'}},
            'MAR_CRISTAL_L8': {'nombre': 'MAR DE CRISTAL', 'latitud': 40.46943, 'longitud': -3.63832, 'lineas': {'4', '8'}},
            'COLOMBIA': {'nombre': 'COLOMBIA', 'latitud': 40.45634, 'longitud': -3.67682, 'lineas': {'8', '9'}},
            'PUEBLO_NUEVO_L8': {'nombre': 'PUEBLO NUEVO', 'latitud': 40.43569, 'longitud': -3.64282, 'lineas': {'5', '8'}},
            'AVENIDA_AMERICA_L8': {'nombre': 'AVENIDA DE AMERICA', 'latitud': 40.43804, 'longitud': -3.67653, 'lineas': {'6', '7', '9', '8'}},
            
            # ===== LÍNEA 9 =====
            'PACO_LUCIA': {'nombre': 'PACO DE LUCIA', 'latitud': 40.49965, 'longitud': -3.70908, 'lineas': {'9'}},
            'MIRASIERRA': {'nombre': 'MIRASIERRA', 'latitud': 40.4911, 'longitud': -3.71634, 'lineas': {'9'}},
            'HERRERA_ORIA': {'nombre': 'HERRERA ORIA', 'latitud': 40.48466, 'longitud': -3.70751, 'lineas': {'9'}},
            'BARRIO_PILAR': {'nombre': 'BARRIO DEL PILAR', 'latitud': 40.47689, 'longitud': -3.70316, 'lineas': {'9'}},
            'VENTILLA': {'nombre': 'VENTILLA', 'latitud': 40.46944, 'longitud': -3.69588, 'lineas': {'9'}},
            'PLAZA_CASTILLA_L9': {'nombre': 'PLAZA DE CASTILLA', 'latitud': 40.4669, 'longitud': -3.68913, 'lineas': {'1', '9', '10'}},
            'DUQUE_PASTRANA': {'nombre': 'DUQUE DE PASTRANA', 'latitud': 40.46763, 'longitud': -3.67917, 'lineas': {'9'}},
            'PIO_XII': {'nombre': 'PIO XII', 'latitud': 40.463, 'longitud': -3.67579, 'lineas': {'9'}},
            'COLOMBIA_L9': {'nombre': 'COLOMBIA', 'latitud': 40.45749, 'longitud': -3.67694, 'lineas': {'8', '9'}},
            'CONCHA_ESPINA': {'nombre': 'CONCHA ESPINA', 'latitud': 40.45145, 'longitud': -3.67738, 'lineas': {'9'}},
            'CRUZ_RAYO': {'nombre': 'CRUZ DEL RAYO', 'latitud': 40.44427, 'longitud': -3.67821, 'lineas': {'9'}},
            'AVENIDA_AMERICA_L9': {'nombre': 'AVENIDA DE AMERICA', 'latitud': 40.43804, 'longitud': -3.67647, 'lineas': {'6', '7', '9', '8'}},
            'NUÑEZ_BALBOA_L9': {'nombre': 'NUÑEZ DE BALBOA', 'latitud': 40.43013, 'longitud': -3.67936, 'lineas': {'5', '9'}},
            'PRINCIPE_VERGARA_L9': {'nombre': 'PRINCIPE DE VERGARA', 'latitud': 40.42418, 'longitud': -3.68024, 'lineas': {'2', '9'}},
            'IBIZA': {'nombre': 'IBIZA', 'latitud': 40.41839, 'longitud': -3.67858, 'lineas': {'9'}},
            'SAINZ_BARANDA_L9': {'nombre': 'SAINZ DE BARANDA', 'latitud': 40.41503, 'longitud': -3.66951, 'lineas': {'6', '9'}},
            'ESTRELLA': {'nombre': 'ESTRELLA', 'latitud': 40.41147, 'longitud': -3.66179, 'lineas': {'9'}},
            'VINATEROS': {'nombre': 'VINATEROS', 'latitud': 40.41024, 'longitud': -3.65273, 'lineas': {'9'}},
            'ARTILLEROS': {'nombre': 'ARTILLEROS', 'latitud': 40.40522, 'longitud': -3.64181, 'lineas': {'9'}},
            'PAVONES': {'nombre': 'PAVONES', 'latitud': 40.40051, 'longitud': -3.63512, 'lineas': {'9'}},
            'VALDEBERNARDO': {'nombre': 'VALDEBERNARDO', 'latitud': 40.40005, 'longitud': -3.62156, 'lineas': {'9'}},
            'VICALVARO': {'nombre': 'VICALVARO', 'latitud': 40.40422, 'longitud': -3.60886, 'lineas': {'9'}},
            'SAN_CIPRIANO': {'nombre': 'SAN CIPRIANO', 'latitud': 40.40381, 'longitud': -3.60239, 'lineas': {'9'}},
            'PUERTA_ARGANDA': {'nombre': 'PUERTA DE ARGANDA', 'latitud': 40.40132, 'longitud': -3.59598, 'lineas': {'9'}},
            'RIVAS_URBANIZACIONES': {'nombre': 'RIVAS URBANIZACIONES', 'latitud': 40.36677, 'longitud': -3.54728, 'lineas': {'9'}},
            'RIVAS_VACIAMADRID': {'nombre': 'RIVAS VACIAMADRID', 'latitud': 40.32837, 'longitud': -3.5206, 'lineas': {'9'}},
            'LA_POVEDA': {'nombre': 'LA POVEDA', 'latitud': 40.31902, 'longitud': -3.47745, 'lineas': {'9'}},
            'ARGANDA_REY': {'nombre': 'ARGANDA DEL REY', 'latitud': 40.30367, 'longitud': -3.44752, 'lineas': {'9'}},
            
            # ===== LÍNEA 10 =====
            'HOSPITAL_INFANTA_SOFIA': {'nombre': 'HOSPITAL INFANTA SOFIA', 'latitud': 40.55977, 'longitud': -3.61145, 'lineas': {'10'}},
            'REYES_CATOLICOS': {'nombre': 'REYES CATOLICOS', 'latitud': 40.55037, 'longitud': -3.6234, 'lineas': {'10'}},
            'BAUNATAL': {'nombre': 'BAUNATAL', 'latitud': 40.55442, 'longitud': -3.63513, 'lineas': {'10'}},
            'MANUEL_FALLA': {'nombre': 'MANUEL DE FALLA', 'latitud': 40.55048, 'longitud': -3.64688, 'lineas': {'10'}},
            'MARQUES_VALDAVIA': {'nombre': 'MARQUES DE LA VALDAVIA', 'latitud': 40.54102, 'longitud': -3.63738, 'lineas': {'10'}},
            'LA_MORALEJA': {'nombre': 'LA MORALEJA', 'latitud': 40.53196, 'longitud': -3.63556, 'lineas': {'10'}},
            'LA_GRANJA': {'nombre': 'LA GRANJA', 'latitud': 40.5276, 'longitud': -3.65859, 'lineas': {'10'}},
            'RONDA_COMUNICACION': {'nombre': 'RONDA DE LA COMUNICACION', 'latitud': 40.51553, 'longitud': -3.66277, 'lineas': {'10'}},
            'LAS_TABLAS': {'nombre': 'LAS TABLAS', 'latitud': 40.50833, 'longitud': -3.66944, 'lineas': {'10'}},
            'MONTE_CARMELO': {'nombre': 'MONTECARMELO', 'latitud': 40.50525, 'longitud': -3.69575, 'lineas': {'10'}},
            'TRES_OLIVOS': {'nombre': 'TRES OLIVOS', 'latitud': 40.5012, 'longitud': -3.6952, 'lineas': {'10'}},
            'FUENCARRAL': {'nombre': 'FUENCARRAL', 'latitud': 40.49509, 'longitud': -3.69283, 'lineas': {'10'}},
            'BEGOÑA': {'nombre': 'BEGOÑA', 'latitud': 40.48041, 'longitud': -3.68585, 'lineas': {'10'}},
            'CHAMARTIN_L10': {'nombre': 'CHAMARTIN', 'latitud': 40.4721, 'longitud': -3.68259, 'lineas': {'1', '10'}},
            'PLAZA_CASTILLA_L10': {'nombre': 'PLAZA DE CASTILLA', 'latitud': 40.4669, 'longitud': -3.68909, 'lineas': {'1', '9', '10'}},
            'CUZCO': {'nombre': 'CUZCO', 'latitud': 40.45842, 'longitud': -3.68985, 'lineas': {'10'}},
            'SANTIAGO_BERNABEU': {'nombre': 'SANTIAGO BERNABEU', 'latitud': 40.45159, 'longitud': -3.69038, 'lineas': {'10'}},
            'NUEVOS_MINISTERIOS_L10': {'nombre': 'NUEVOS MINISTERIOS', 'latitud': 40.44659, 'longitud': -3.69241, 'lineas': {'6', '8', '10'}},
            'GREGORIO_MARAÑON_L10': {'nombre': 'GREGORIO MARAÑON', 'latitud': 40.43753, 'longitud': -3.69127, 'lineas': {'7', '10'}},
            'ALONSO_MARTINEZ_L10': {'nombre': 'ALONSO MARTINEZ', 'latitud': 40.42853, 'longitud': -3.69643, 'lineas': {'4', '5', '10'}},
            'TRIBUNAL_L10': {'nombre': 'TRIBUNAL', 'latitud': 40.426, 'longitud': -3.70208, 'lineas': {'1', '10'}},
            'PLAZA_ESPANA_L10': {'nombre': 'PLAZA DE ESPAÑA', 'latitud': 40.42409, 'longitud': -3.7097, 'lineas': {'3', '10'}},
            'PRINCIPE_PIO_L10': {'nombre': 'PRINCIPE PIO', 'latitud': 40.42103, 'longitud': -3.72033, 'lineas': {'6', '10', 'R'}},
            'LAGO': {'nombre': 'LAGO', 'latitud': 40.41641, 'longitud': -3.73563, 'lineas': {'10'}},
            'BATAN': {'nombre': 'BATAN', 'latitud': 40.40786, 'longitud': -3.75311, 'lineas': {'10'}},
            'CASA_CAMPO_L10': {'nombre': 'CASA DE CAMPO', 'latitud': 40.40321, 'longitud': -3.76101, 'lineas': {'5', '10'}},
            'COLONIA_JARDIN': {'nombre': 'COLONIA JARDIN', 'latitud': 40.39698, 'longitud': -3.77462, 'lineas': {'10'}},
            'AVIACION_ESPANOLA': {'nombre': 'AVIACION ESPAÑOLA', 'latitud': 40.38364, 'longitud': -3.78392, 'lineas': {'10'}},
            'CUATRO_VIENTOS': {'nombre': 'CUATRO VIENTOS', 'latitud': 40.37771, 'longitud': -3.79152, 'lineas': {'10'}},
            'JOAQUIN_VILUMBRALES': {'nombre': 'JOAQUIN VILUMBRALES', 'latitud': 40.34985, 'longitud': -3.8072, 'lineas': {'10'}},
            'PUERTA_SUR': {'nombre': 'PUERTA DEL SUR', 'latitud': 40.34524, 'longitud': -3.81211, 'lineas': {'10', '12'}},
            
            # ===== LÍNEA 11 =====
            'PLAZA_ELIPTICA_L11': {'nombre': 'PLAZA ELIPTICA', 'latitud': 40.3846, 'longitud': -3.71825, 'lineas': {'6', '11'}},
            'ABRANTES': {'nombre': 'ABRANTES', 'latitud': 40.38083, 'longitud': -3.7279, 'lineas': {'11'}},
            'PAN_BENDITO': {'nombre': 'PAN BENDITO', 'latitud': 40.37587, 'longitud': -3.73417, 'lineas': {'11'}},
            'SAN_FRANCISCO_L11': {'nombre': 'SAN FRANCISCO', 'latitud': 40.3736, 'longitud': -3.7391, 'lineas': {'11'}},
            'CARABANCHEL_ALTO': {'nombre': 'CARABANCHEL ALTO', 'latitud': 40.372, 'longitud': -3.75191, 'lineas': {'11'}},
            'LA_PESETA': {'nombre': 'LA PESETA', 'latitud': 40.36422, 'longitud': -3.7569, 'lineas': {'11'}},
            'LA_FORTUNA': {'nombre': 'LA FORTUNA', 'latitud': 40.35795, 'longitud': -3.77783, 'lineas': {'11'}},
            
            # ===== LÍNEA 12 =====
            'PUERTA_SUR_L12': {'nombre': 'PUERTA DEL SUR', 'latitud': 40.34543, 'longitud': -3.81249, 'lineas': {'10', '12'}},
            'PARQUE_LISBOA': {'nombre': 'PARQUE LISBOA', 'latitud': 40.34969, 'longitud': -3.8212, 'lineas': {'12'}},
            'ALCORCON_CENTRAL': {'nombre': 'ALCORCON CENTRAL', 'latitud': 40.35008, 'longitud': -3.83178, 'lineas': {'12'}},
            'PARQUE_OESTE': {'nombre': 'PARQUE OESTE', 'latitud': 40.34589, 'longitud': -3.84934, 'lineas': {'12'}},
            'UNIVERSIDAD_REY_JUAN_CARLOS': {'nombre': 'UNIVERSIDAD REY JUAN CARLOS', 'latitud': 40.33512, 'longitud': -3.87218, 'lineas': {'12'}},
            'MOSTOLES_CENTRAL': {'nombre': 'MOSTOLES CENTRAL', 'latitud': 40.3285, 'longitud': -3.86354, 'lineas': {'12'}},
            'PRADILLO': {'nombre': 'PRADILLO', 'latitud': 40.32168, 'longitud': -3.86489, 'lineas': {'12'}},
            'HOSPITAL_MOSTOLES': {'nombre': 'HOSPITAL DE MOSTOLES', 'latitud': 40.31652, 'longitud': -3.87471, 'lineas': {'12'}},
            'MANUELA_MALASAÑA': {'nombre': 'MANUELA MALASAÑA', 'latitud': 40.30903, 'longitud': -3.86402, 'lineas': {'12'}},
            'LORANCA': {'nombre': 'LORANCA', 'latitud': 40.29681, 'longitud': -3.83768, 'lineas': {'12'}},
            'HOSPITAL_FUENLABRADA': {'nombre': 'HOSPITAL DE FUENLABRADA', 'latitud': 40.28576, 'longitud': -3.81642, 'lineas': {'12'}},
            'PARQUE_EUROPA': {'nombre': 'PARQUE EUROPA', 'latitud': 40.28518, 'longitud': -3.80632, 'lineas': {'12'}},
            'FUENLABRADA_CENTRAL': {'nombre': 'FUENLABRADA CENTRAL', 'latitud': 40.28268, 'longitud': -3.79891, 'lineas': {'12'}},
            'PARQUE_ESTADOS': {'nombre': 'PARQUE DE LOS ESTADOS', 'latitud': 40.28684, 'longitud': -3.78697, 'lineas': {'12'}},
            'ARROYO_CULEBRO': {'nombre': 'ARROYO CULEBRO', 'latitud': 40.28874, 'longitud': -3.75682, 'lineas': {'12'}},
            'CONSERVATORIO': {'nombre': 'CONSERVATORIO', 'latitud': 40.29324, 'longitud': -3.74576, 'lineas': {'12'}},
            'ALONSO_MENDOZA': {'nombre': 'ALONSO DE MENDOZA', 'latitud': 40.30081, 'longitud': -3.73664, 'lineas': {'12'}},
            'GETAFE_CENTRAL': {'nombre': 'GETAFE CENTRAL', 'latitud': 40.30993, 'longitud': -3.73403, 'lineas': {'12'}},
            'JUAN_CIERVA': {'nombre': 'JUAN DE LA CIERVA', 'latitud': 40.3118, 'longitud': -3.72224, 'lineas': {'12'}},
            'EL_CASAR': {'nombre': 'EL CASAR', 'latitud': 40.31862, 'longitud': -3.70985, 'lineas': {'12'}},
            'LOS_ESPARTALES': {'nombre': 'LOS ESPARTALES', 'latitud': 40.32423, 'longitud': -3.7182, 'lineas': {'12'}},
            'EL_BERCIAL': {'nombre': 'EL BERCIAL', 'latitud': 40.32907, 'longitud': -3.72963, 'lineas': {'12'}},
            'EL_CARRASCAL': {'nombre': 'EL CARRASCAL', 'latitud': 40.33664, 'longitud': -3.74018, 'lineas': {'12'}},
            'JULIAN_BESTEIRO': {'nombre': 'JULIAN BESTEIRO', 'latitud': 40.33475, 'longitud': -3.75266, 'lineas': {'12'}},
            'CASA_RELOJ': {'nombre': 'CASA DEL RELOJ', 'latitud': 40.3266, 'longitud': -3.75942, 'lineas': {'12'}},
            'HOSPITAL_SEVERO_OCHOA': {'nombre': 'HOSPITAL SEVERO OCHOA', 'latitud': 40.32177, 'longitud': -3.76797, 'lineas': {'12'}},
            'LEGANES_CENTRAL': {'nombre': 'LEGANES CENTRAL', 'latitud': 40.32899, 'longitud': -3.77154, 'lineas': {'12'}},
            'SAN_NICASIO': {'nombre': 'SAN NICASIO', 'latitud': 40.33616, 'longitud': -3.77587, 'lineas': {'12'}},
            
            # ===== RAMAL ÓPERA-PRÍNCIPE PÍO =====
            'OPERA_R': {'nombre': 'OPERA', 'latitud': 40.41809, 'longitud': -3.70928, 'lineas': {'2', '5', 'R'}},
            'PRINCIPE_PIO_R': {'nombre': 'PRINCIPE PIO', 'latitud': 40.42099, 'longitud': -3.72033, 'lineas': {'6', '10', 'R'}},
        }
        
        return {
            'estaciones': estaciones_completas,
            'estaciones_df': pd.DataFrame()  # Para posibles usos futuros con pandas
        }

    def _crear_grafo_metro_completo(self) -> nx.Graph:
        """
        Crea un grafo del metro completo con TODAS las líneas.
        Los nodos son estaciones, las aristas son conexiones entre estaciones.
        """
        # Crear grafo no dirigido (puedes ir en ambas direcciones)
        grafo = nx.Graph()
        
        # Añadir estaciones como nodos del grafo
        for estacion_id, datos in self.red_metro['estaciones'].items():
            grafo.add_node(estacion_id, 
                         nombre=datos['nombre'],
                         latitud=datos['latitud'],
                         longitud=datos['longitud'],
                         lineas=list(datos['lineas']))  # Líneas que pasan por esta estación
        
        # Definir conexiones por líneas (el orden importa - secuencia real)
        conexiones_lineas = {
            # Línea 1
            '1': ['PINAR_CHAMARTIN', 'BAMBU', 'CHAMARTIN', 'PLAZA_CASTILLA', 'VALDEACEDERAS', 
                  'TETUAN', 'ESTRECHO', 'ALVARADO', 'CUATRO_CAMINOS', 'RIOS_ROSAS', 'IGLESIA', 
                  'BILBAO', 'TRIBUNAL', 'GRAN_VIA', 'SOL', 'TIRSO_MOLINA', 'ANTON_MARTIN', 
                  'ESTACION_ARTE', 'ATOCHA', 'MENENDEZ_PELAYO', 'PACIFICO', 'PUENTE_VALLECAS', 
                  'NUEVA_NUMANCIA', 'PORTAZGO', 'BUENOS_AIRES', 'ALTO_ARENAL', 'MIGUEL_HERNANDEZ', 
                  'SIERRA_GUADALUPE', 'VILLA_VALLECAS', 'CONGOSTO', 'LA_GAVIA', 'LAS_SUERTES', 'VALDECARROS'],
            
            # Línea 2
            '2': ['LAS_ROSAS', 'AVENIDA_GUADALAJARA', 'ALSACIA', 'LA_ALMUDENA', 'LA_ELIPA', 
                  'VENTAS', 'MANUEL_BECERRA', 'GOYA', 'PRINCIPE_VERGARA', 'RETIRO', 'BANCO_ESPANA', 
                  'SEVILLA', 'SOL', 'OPERA', 'SANTO_DOMINGO', 'NOVICIADO', 'SAN_BERNARDO', 
                  'QUEVEDO', 'CANAL', 'CUATRO_CAMINOS'],
            
            # Línea 3
            '3': ['VILLAVERDE_ALTO', 'SAN_CRISTOBAL', 'VILLAVERDE_CRUCE', 'CIUDAD_ANGELES', 
                  'SAN_FERMIN', 'HOSPITAL_12_OCTUBRE', 'ALMENDRALES', 'LEGAZPI', 'DELICIAS', 
                  'PALOS_FRONTERA', 'EMBAJADORES', 'LAVAPIES', 'SOL', 'CALLAO', 'PLAZA_ESPANA', 
                  'VENTURA_RODRIGUEZ', 'ARGUELLES', 'MONCLOA'],
            
            # Línea 4
            '4': ['PINAR_CHAMARTIN_L4', 'MANOTERAS', 'HORTALEZA', 'PARQUE_SANTA_MARIA', 'SAN_LORENZO', 
                  'MAR_CRISTAL', 'CANILLAS', 'ESPERANZA', 'ARTURO_SORIA', 'DIEGO_LEON', 'LISTA', 
                  'VELAZQUEZ', 'SERRANO', 'COLON', 'ALONSO_MARTINEZ', 'BILBAO', 'SAN_BERNARDO', 'ARGUELLES'],
            
            # Línea 5
            '5': ['ALAMEDA_OSUNA', 'EL_CAPRICHO', 'CANILLEJAS', 'TORRE_ARIAS', 'SUANZES', 
                  'CIUDAD_LINEAL', 'PUEBLO_NUEVO', 'QUINTANA', 'EL_CARMEN', 'VENTAS', 'DIEGO_LEON', 
                  'NUÑEZ_BALBOA', 'RUBEN_DARIO', 'ALONSO_MARTINEZ', 'CHUECA', 'GRAN_VIA', 'OPERA', 
                  'LA_LATINA', 'PUERTA_TOLEDO', 'ACACIAS', 'PIRAMIDES', 'MARQUES_VADILLO', 'URGEL', 
                  'OPORTO', 'VISTA_ALEGRE', 'CARABANCHEL', 'EUGENIA_MONTIJO', 'ALUCHE', 'EMPALME', 
                  'CAMPAMENTO', 'CASA_CAMPO'],
            
            # Línea 6 (Circular)
            '6': ['LAGUNA', 'CARPETANA', 'OPAÑEL', 'PLAZA_ELIPTICA', 'USERA', 'LEGAZPI_L6', 
                  'ARGANZUELA_L6', 'MENDEZ_ALVARO_L6', 'PACIFICO_L6', 'CONDE_CASAL', 'SAINZ_BARANDA', 
                  'ODONNELL', 'MANUEL_BECERRA_L6', 'DIEGO_LEON_L6', 'AVENIDA_AMERICA', 'REPUBLICA_ARGENTINA', 
                  'NUEVOS_MINISTERIOS', 'GUZMAN_EL_BUENO', 'VICENTE_ALEIXANDRE', 'CIUDAD_UNIVERSITARIA', 
                  'MONCLOA_L6', 'ARGUELLES_L6', 'PRINCIPE_PIO', 'PUERTA_ANGEL', 'ALTO_EXTREMADURA', 'LUCERO'],
            
            # Línea 7
            '7': ['PITIS', 'ARROYO_FRESNO', 'LACOMA', 'AVENIDA_ILUSTRACION', 'PEÑAGRANDE', 
                  'ANTONIO_MACHADO', 'VALDEZARZA', 'FRANCOS_RODRIGUEZ', 'ISLAS_FILIPINAS', 'ALONSO_CANO', 
                  'GREGORIO_MARAÑON', 'AVENIDA_AMERICA_L7', 'CARTAGENA', 'PARQUE_AVENIDAS', 'BARRIO_CONCEPCION', 
                  'ASCAO', 'GARCIA_NOBLEJAS', 'SIMANCAS', 'SAN_BLAS', 'LAS_MUSAS', 'ESTADIO_METROPOLITANO', 
                  'BARRIO_PUERTO', 'COSLADA_CENTRAL', 'LA_RAMBLA', 'SAN_FERNANDO', 'JARAMA', 'HENARES', 'HOSPITAL_HENARES'],
            
            # Línea 8
            '8': ['AEROPUERTO_T4', 'BARAJAS', 'AEROPUERTO_T1_T2_T3', 'FERIA_MADRID', 'MAR_CRISTAL_L8', 
                  'COLOMBIA', 'PUEBLO_NUEVO_L8', 'AVENIDA_AMERICA_L8', 'NUEVOS_MINISTERIOS'],
            
            # Línea 9
            '9': ['PACO_LUCIA', 'MIRASIERRA', 'HERRERA_ORIA', 'BARRIO_PILAR', 'VENTILLA', 
                  'PLAZA_CASTILLA_L9', 'DUQUE_PASTRANA', 'PIO_XII', 'COLOMBIA_L9', 'CONCHA_ESPINA', 
                  'CRUZ_RAYO', 'AVENIDA_AMERICA_L9', 'NUÑEZ_BALBOA_L9', 'PRINCIPE_VERGARA_L9', 'IBIZA', 
                  'SAINZ_BARANDA_L9', 'ESTRELLA', 'VINATEROS', 'ARTILLEROS', 'PAVONES', 'VALDEBERNARDO', 
                  'VICALVARO', 'SAN_CIPRIANO', 'PUERTA_ARGANDA', 'RIVAS_URBANIZACIONES', 'RIVAS_VACIAMADRID', 
                  'LA_POVEDA', 'ARGANDA_REY'],
            
            # Línea 10
            '10': ['HOSPITAL_INFANTA_SOFIA', 'REYES_CATOLICOS', 'BAUNATAL', 'MANUEL_FALLA', 
                   'MARQUES_VALDAVIA', 'LA_MORALEJA', 'LA_GRANJA', 'RONDA_COMUNICACION', 'LAS_TABLAS', 
                   'MONTE_CARMELO', 'TRES_OLIVOS', 'FUENCARRAL', 'BEGOÑA', 'CHAMARTIN_L10', 'PLAZA_CASTILLA_L10', 
                   'CUZCO', 'SANTIAGO_BERNABEU', 'NUEVOS_MINISTERIOS_L10', 'GREGORIO_MARAÑON_L10', 'ALONSO_MARTINEZ_L10', 
                   'TRIBUNAL_L10', 'PLAZA_ESPANA_L10', 'PRINCIPE_PIO_L10', 'LAGO', 'BATAN', 'CASA_CAMPO_L10', 
                   'COLONIA_JARDIN', 'AVIACION_ESPANOLA', 'CUATRO_VIENTOS', 'JOAQUIN_VILUMBRALES', 'PUERTA_SUR'],
            
            # Línea 11
            '11': ['PLAZA_ELIPTICA_L11', 'ABRANTES', 'PAN_BENDITO', 'SAN_FRANCISCO_L11', 'CARABANCHEL_ALTO', 
                   'LA_PESETA', 'LA_FORTUNA'],
            
            # Línea 12 (MetroSur)
            '12': ['PUERTA_SUR_L12', 'PARQUE_LISBOA', 'ALCORCON_CENTRAL', 'PARQUE_OESTE', 'UNIVERSIDAD_REY_JUAN_CARLOS', 
                   'MOSTOLES_CENTRAL', 'PRADILLO', 'HOSPITAL_MOSTOLES', 'MANUELA_MALASAÑA', 'LORANCA', 'HOSPITAL_FUENLABRADA', 
                   'PARQUE_EUROPA', 'FUENLABRADA_CENTRAL', 'PARQUE_ESTADOS', 'ARROYO_CULEBRO', 'CONSERVATORIO', 
                   'ALONSO_MENDOZA', 'GETAFE_CENTRAL', 'JUAN_CIERVA', 'EL_CASAR', 'LOS_ESPARTALES', 'EL_BERCIAL', 
                   'EL_CARRASCAL', 'JULIAN_BESTEIRO', 'CASA_RELOJ', 'HOSPITAL_SEVERO_OCHOA', 'LEGANES_CENTRAL', 'SAN_NICASIO'],
            
            # Ramal Ópera-Príncipe Pío
            'R': ['OPERA_R', 'PRINCIPE_PIO_R']
        }
        
        # Crear conexiones basadas en las líneas
        for linea, estaciones_linea in conexiones_lineas.items():
            # Conectar cada estación con la siguiente en la línea
            for i in range(len(estaciones_linea) - 1):
                est1 = estaciones_linea[i]      # Estación actual
                est2 = estaciones_linea[i + 1]  # Estación siguiente
                
                # Verificar que ambas estaciones existen en el grafo
                if est1 in grafo.nodes() and est2 in grafo.nodes():
                    # Calcular distancia real entre estaciones para tiempo estimado
                    datos1 = grafo.nodes[est1]
                    datos2 = grafo.nodes[est2]
                    distancia = self._calcular_distancia(
                        datos1['latitud'], datos1['longitud'],
                        datos2['latitud'], datos2['longitud']
                    )
                    
                    # Tiempo estimado: 2 minutos por km + 1 minuto fijo por estación
                    tiempo_estimado = (distancia / 1000) * 2 + 1
                    
                    # Obtener líneas comunes (para saber si es transbordo)
                    lineas_comunes = set(grafo.nodes[est1]['lineas']).intersection(
                        set(grafo.nodes[est2]['lineas'])
                    )
                    
                    # Añadir arista (conexión) entre estaciones
                    grafo.add_edge(est1, est2,
                                 distancia=distancia,        # Distancia en metros
                                 tiempo=tiempo_estimado,     # Tiempo en minutos
                                 lineas=list(lineas_comunes), # Líneas que comparten
                                 transbordo=len(lineas_comunes) == 0)  # True si hay que cambiar de línea
        
        # Conectar estaciones que son transbordos (misma estación, diferentes líneas)
        self._conectar_transbordos(grafo)
        
        return grafo
    
    def _conectar_transbordos(self, grafo: nx.Graph):
        """
        Conecta estaciones que son transbordos entre líneas pero que pueden
        no estar conectadas en las secuencias lineales.
        Ejemplo: Sol (L1) con Sol (L2) y Sol (L3)
        """
        # Agrupar estaciones por nombre (para encontrar transbordos)
        estaciones_por_nombre = {}
        
        for estacion_id, datos in grafo.nodes(data=True):
            nombre = datos['nombre']
            if nombre not in estaciones_por_nombre:
                estaciones_por_nombre[nombre] = []
            estaciones_por_nombre[nombre].append(estacion_id)
        
        # Conectar estaciones con el mismo nombre (transbordos)
        for nombre, estaciones_ids in estaciones_por_nombre.items():
            if len(estaciones_ids) > 1:  # Si hay múltiples estaciones con mismo nombre
                # Conectar todas las estaciones con el mismo nombre entre sí
                for i in range(len(estaciones_ids)):
                    for j in range(i + 1, len(estaciones_ids)):
                        est1 = estaciones_ids[i]
                        est2 = estaciones_ids[j]
                        
                        # Solo conectar si no están ya conectadas
                        if not grafo.has_edge(est1, est2):
                            # Tiempo de transbordo: 3 minutos para cambiar de andén
                            grafo.add_edge(est1, est2, 
                                        distancia=0,
                                        tiempo=3.0,  # 3 minutos para transbordar
                                        lineas=list(set(grafo.nodes[est1]['lineas'] + grafo.nodes[est2]['lineas'])),
                                        transbordo=True)  # Marcar como transbordo

    def verificar_conectividad(self):
        """
        Verifica que el grafo del metro esté completamente conectado.
        Si hay múltiples componentes, algunas estaciones no son alcanzables.
        """
        if self.grafo_metro is None:
            print("Grafo no inicializado")
            return
        
        # Encontrar componentes conexos (grupos de estaciones conectadas entre sí)
        componentes = list(nx.connected_components(self.grafo_metro))
        print(f"El grafo tiene {len(componentes)} componentes conexos")
        
        if len(componentes) > 1:
            print("ADVERTENCIA: El grafo no es conexo")
            # Mostrar información de cada componente
            for i, componente in enumerate(componentes):
                print(f"Componente {i+1}: {len(componente)} estaciones")
                # Mostrar algunas estaciones de cada componente
                estaciones_ejemplo = list(componente)[:3]
                nombres = [self.grafo_metro.nodes[est]['nombre'] for est in estaciones_ejemplo]
                print(f"  Ejemplos: {', '.join(nombres)}")  

    def _calcular_distancia(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcula la distancia aproximada entre dos puntos usando la fórmula de Haversine.
        Esta fórmula calcula la distancia en una esfera (Tierra).
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371000  # Radio de la Tierra en metros
        
        # Convertir grados a radianes
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        # Diferencias en coordenadas
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Fórmula de Haversine
        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        # Distancia en metros
        return R * c
    
    def encontrar_estacion_cercana(self, latitud: float, longitud: float) -> Optional[str]:
        """
        Encuentra la estación de metro más cercana a unas coordenadas dadas.
        Usa distancia euclidiana en el grafo.
        """
        if self.grafo_metro is None:
            return None
            
        estacion_cercana = None
        distancia_minima = float('inf')  # Empezar con distancia infinita
        
        # Revisar todas las estaciones para encontrar la más cercana
        for estacion_id, datos in self.grafo_metro.nodes(data=True):
            distancia = self._calcular_distancia(
                latitud, longitud, 
                datos['latitud'], datos['longitud']
            )
            
            if distancia < distancia_minima:
                distancia_minima = distancia
                estacion_cercana = estacion_id
        
        return estacion_cercana
    
    def _peso_tiempo_metro(self, grafo: nx.Graph, u: str, v: str) -> float:
        """
        Función de peso basada en el tiempo de viaje entre estaciones.
        Esta función se usa en el algoritmo de Dijkstra.
        """
        return grafo[u][v].get('tiempo', 10.0)  # 10 min por defecto si no hay dato
    
    def _peso_transbordos(self, grafo: nx.Graph, u: str, v: str) -> float:
        """
        Función de peso que penaliza los transbordos entre líneas.
        Hace que Dijkstra prefiera rutas con menos cambios de línea.
        """
        tiempo_base = grafo[u][v].get('tiempo', 10.0)
        
        # Penalizar transbordos (cambios de línea) añadiendo 2 minutos extra
        if grafo[u][v].get('transbordo', False):
            tiempo_base += 2.0  # 2 minutos extra por transbordo
        
        return tiempo_base
    
    def calcular_ruta_metro(self, direccion_origen: str, direccion_destino: str) -> Optional[Dict]:
        """
        Calcula la ruta óptima en metro entre dos direcciones.
        Es el método principal que orquesta todo el proceso.
        """
        try:
            print(f"Calculando ruta en metro desde: {direccion_origen}")
            print(f"Hacia: {direccion_destino}")
            
            # PASO 1: Buscar coordenadas de las direcciones usando el callejero
            lat_origen, lon_origen, direccion_origen_hallada = busca_direccion(direccion_origen, self.callejero)
            lat_destino, lon_destino, direccion_destino_hallada = busca_direccion(direccion_destino, self.callejero)
            
            print(f"Coordenadas origen: ({lat_origen:.6f}, {lon_origen:.6f})")
            print(f"Coordenadas destino: ({lat_destino:.6f}, {lon_destino:.6f})")
            
            # PASO 2: Encontrar estaciones más cercanas a ambas direcciones
            estacion_origen = self.encontrar_estacion_cercana(lat_origen, lon_origen)
            estacion_destino = self.encontrar_estacion_cercana(lat_destino, lon_destino)
            
            if estacion_origen is None or estacion_destino is None:
                print("No se pudieron encontrar estaciones cercanas")
                return None
            
            nombre_origen = self.grafo_metro.nodes[estacion_origen]['nombre']
            nombre_destino = self.grafo_metro.nodes[estacion_destino]['nombre']
            
            print(f"Estación origen: {nombre_origen}")
            print(f"Estación destino: {nombre_destino}")
            
            # PASO 3: Verificar si hay conexión entre las estaciones
            if not nx.has_path(self.grafo_metro, estacion_origen, estacion_destino):
                print("No hay ruta disponible entre estas estaciones")
                return None
            
            # PASO 4: Calcular ruta usando algoritmo de Dijkstra
            funcion_peso = self._peso_transbordos  # Usar función que penaliza transbordos
            camino = camino_minimo(self.grafo_metro, funcion_peso, estacion_origen, estacion_destino)
            
            if not camino:
                print("No se encontró una ruta en metro entre los puntos especificados")
                return None
            
            # PASO 5: Calcular métricas de la ruta encontrada
            tiempo_total = 0
            transbordos = 0
            lineas_utilizadas = set()
            
            # Analizar cada segmento del camino
            for i in range(len(camino) - 1):
                u, v = camino[i], camino[i + 1]
                tiempo_segmento = self.grafo_metro[u][v].get('tiempo', 0)
                tiempo_total += tiempo_segmento
                
                lineas_segmento = self.grafo_metro[u][v].get('lineas', [])
                lineas_utilizadas.update(lineas_segmento)
                
                # Detectar transbordos (cambios de línea)
                if i > 0:  # No es el primer segmento
                    lineas_anteriores = self.grafo_metro[camino[i-1]][u].get('lineas', [])
                    # Si no comparten líneas, es un transbordo
                    if not set(lineas_segmento).intersection(set(lineas_anteriores)):
                        transbordos += 1
            
            # PASO 6: Generar instrucciones detalladas para el usuario
            instrucciones = self._generar_instrucciones_metro(camino)
            
            # PASO 7: Calcular tiempo caminando hasta las estaciones
            distancia_origen = self._calcular_distancia(
                lat_origen, lon_origen,
                self.grafo_metro.nodes[estacion_origen]['latitud'],
                self.grafo_metro.nodes[estacion_origen]['longitud']
            )
            
            distancia_destino = self._calcular_distancia(
                lat_destino, lon_destino,
                self.grafo_metro.nodes[estacion_destino]['latitud'],
                self.grafo_metro.nodes[estacion_destino]['longitud']
            )
            
            # Asumir velocidad de caminata de 5 km/h (1.33 m/s)
            tiempo_caminando = (distancia_origen + distancia_destino) / 80
            
            # PASO 8: Retornar todos los resultados empaquetados
            return {
                'camino': camino,                          # Lista de estaciones en orden
                'tiempo_metro': tiempo_total,              # Tiempo solo en metro
                'tiempo_caminando': tiempo_caminando,      # Tiempo caminando a estaciones
                'tiempo_total': tiempo_total + tiempo_caminando,  # Tiempo total
                'transbordos': transbordos,                # Número de cambios de línea
                'lineas': list(lineas_utilizadas),         # Líneas utilizadas
                'instrucciones': instrucciones,            # Instrucciones paso a paso
                'estacion_origen': nombre_origen,          # Nombre estación origen
                'estacion_destino': nombre_destino,        # Nombre estación destino
                'direccion_origen': direccion_origen_hallada,  # Dirección formateada origen
                'direccion_destino': direccion_destino_hallada # Dirección formateada destino
            }
            
        except AdressNotFoundError as e:
            print(f"Error: {e}")
            return None
        except Exception as e:
            print(f"Error al calcular la ruta: {e}")
            return None
    
    def _generar_instrucciones_metro(self, camino: List[str]) -> List[Dict]:
        """
        Genera instrucciones detalladas para la ruta de metro.
        Convierte la lista de estaciones en instrucciones legibles.
        """
        instrucciones = []
        
        if len(camino) < 2:
            return instrucciones
        
        # Primera instrucción: ir a la estación de origen
        primera_estacion = self.grafo_metro.nodes[camino[0]]['nombre']
        instrucciones.append({
            'tipo': 'inicio',
            'descripcion': f"Diríjase a la estación {primera_estacion}",
            'estacion': primera_estacion
        })
        
        linea_actual = None  # Línea en la que estamos actualmente
        
        # Generar instrucciones para cada segmento del viaje
        for i in range(len(camino) - 1):
            u, v = camino[i], camino[i + 1]
            estacion_actual = self.grafo_metro.nodes[u]['nombre']
            estacion_siguiente = self.grafo_metro.nodes[v]['nombre']
            
            lineas_segmento = self.grafo_metro[u][v].get('lineas', [])
            tiempo_segmento = self.grafo_metro[u][v].get('tiempo', 0)
            
            if not lineas_segmento:
                continue  # Saltar si no hay líneas definidas
            
            if linea_actual is None:
                # Primera línea del viaje
                linea_actual = lineas_segmento[0]
                instrucciones.append({
                    'tipo': 'tomar_metro',
                    'descripcion': f"Tome la Línea {linea_actual} hacia {estacion_siguiente}",
                    'linea': linea_actual,
                    'estacion_siguiente': estacion_siguiente,
                    'tiempo': tiempo_segmento
                })
            else:
                # Verificar si hay cambio de línea
                if linea_actual not in lineas_segmento:
                    # Transbordo - cambiar de línea
                    nueva_linea = lineas_segmento[0]
                    instrucciones.append({
                        'tipo': 'transbordo',
                        'descripcion': f"En {estacion_actual}, transborde a la Línea {nueva_linea}",
                        'linea_anterior': linea_actual,
                        'linea_nueva': nueva_linea,
                        'estacion': estacion_actual
                    })
                    linea_actual = nueva_linea
                
                # Continuar en la misma línea
                instrucciones.append({
                    'tipo': 'continuar',
                    'descripcion': f"Continúe en la Línea {linea_actual} hasta {estacion_siguiente}",
                    'linea': linea_actual,
                    'estacion_siguiente': estacion_siguiente,
                    'tiempo': tiempo_segmento
                })
        
        # Última instrucción: llegada al destino
        ultima_estacion = self.grafo_metro.nodes[camino[-1]]['nombre']
        instrucciones.append({
            'tipo': 'llegada',
            'descripcion': f"Baje en {ultima_estacion} y diríjase a su destino final",
            'estacion': ultima_estacion
        })
        
        return instrucciones
    
    def mostrar_ruta_metro(self, resultado_ruta: Dict):
        """
        Muestra la ruta calculada con instrucciones detalladas en formato legible.
        """
        if not resultado_ruta:
            print("No hay ruta para mostrar")
            return
        
        print("\n" + "="*70)
        print("RUTA EN METRO - INSTRUCCIONES")
        print("="*70)
        
        # Información básica del viaje
        print(f"Desde: {resultado_ruta['direccion_origen']}")
        print(f"Hasta: {resultado_ruta['direccion_destino']}")
        print(f"Estación de origen: {resultado_ruta['estacion_origen']}")
        print(f"Estación de destino: {resultado_ruta['estacion_destino']}")
        print()
        
        # Resumen del viaje
        print(f"📊 RESUMEN DEL VIAJE:")
        print(f"   • Tiempo en metro: {resultado_ruta['tiempo_metro']:.1f} min")
        print(f"   • Tiempo caminando: {resultado_ruta['tiempo_caminando']:.1f} min")
        print(f"   • Tiempo total: {resultado_ruta['tiempo_total']:.1f} min")
        print(f"   • Transbordos: {resultado_ruta['transbordos']}")
        print(f"   • Líneas utilizadas: {', '.join(resultado_ruta['lineas'])}")
        print()
        
        # Instrucciones detalladas paso a paso
        print("🚇 INSTRUCCIONES DETALLADAS:")
        for i, instruccion in enumerate(resultado_ruta['instrucciones']):
            # Diferentes emojis y formatos según el tipo de instrucción
            if instruccion['tipo'] == 'inicio':
                print(f"{i+1}. 🚶 {instruccion['descripcion']}")
            elif instruccion['tipo'] == 'tomar_metro':
                print(f"{i+1}. 🚇 {instruccion['descripcion']} "
                      f"({instruccion['tiempo']:.1f} min)")
            elif instruccion['tipo'] == 'continuar':
                print(f"{i+1}. ➡️  {instruccion['descripcion']} "
                      f"({instruccion['tiempo']:.1f} min)")
            elif instruccion['tipo'] == 'transbordo':
                print(f"{i+1}. 🔄 {instruccion['descripcion']}")
            elif instruccion['tipo'] == 'llegada':
                print(f"{i+1}. 🎯 {instruccion['descripcion']}")
        
        print("="*70)
    
    def visualizar_ruta_metro(self, resultado_ruta: Dict):
        """
        Visualiza la ruta calculada sobre un mapa esquemático del metro.
        Usa matplotlib para dibujar el grafo.
        """
        if not resultado_ruta or 'camino' not in resultado_ruta:
            print("No hay ruta para visualizar")
            return
        
        try:
            # Crear figura para el mapa
            fig, ax = plt.subplots(figsize=(15, 10))
            
            # Obtener coordenadas de todas las estaciones para posicionarlas en el mapa
            posiciones = {}
            for estacion_id in self.grafo_metro.nodes():
                datos = self.grafo_metro.nodes[estacion_id]
                posiciones[estacion_id] = (datos['longitud'], datos['latitud'])
            
            # Dibujar todas las estaciones (puntos grises)
            nx.draw_networkx_nodes(self.grafo_metro, posiciones, 
                                 node_size=50,
                                 node_color='lightgray',
                                 alpha=0.6,
                                 ax=ax)
            
            # Dibujar todas las conexiones (líneas azules claras)
            nx.draw_networkx_edges(self.grafo_metro, posiciones,
                                 edge_color='lightblue',
                                 alpha=0.4,
                                 ax=ax)
            
            # Resaltar la ruta calculada (línea roja gruesa)
            camino = resultado_ruta['camino']
            edges_camino = [(camino[i], camino[i+1]) for i in range(len(camino)-1)]
            
            nx.draw_networkx_edges(self.grafo_metro, posiciones, 
                                 edgelist=edges_camino,
                                 edge_color='red', 
                                 width=3, 
                                 alpha=0.8,
                                 ax=ax)
            
            # Resaltar estaciones de la ruta (puntos rojos)
            nx.draw_networkx_nodes(self.grafo_metro, posiciones, 
                                 nodelist=camino,
                                 node_size=100,
                                 node_color='red',
                                 alpha=0.8,
                                 ax=ax)
            
            # Resaltar origen (verde) y destino (azul)
            if camino:
                nx.draw_networkx_nodes(self.grafo_metro, posiciones, 
                                     nodelist=[camino[0]],  # Origen
                                     node_size=150,
                                     node_color='green',
                                     ax=ax)
                nx.draw_networkx_nodes(self.grafo_metro, posiciones, 
                                     nodelist=[camino[-1]],  # Destino
                                     node_size=150,
                                     node_color='blue',
                                     ax=ax)
            
            # Añadir etiquetas solo a las estaciones de la ruta
            etiquetas = {}
            for estacion_id in camino:
                etiquetas[estacion_id] = self.grafo_metro.nodes[estacion_id]['nombre']
            
            nx.draw_networkx_labels(self.grafo_metro, posiciones, 
                                  labels=etiquetas,
                                  font_size=8,
                                  ax=ax)
            
            # Título del mapa con información del viaje
            ax.set_title(f'Ruta en Metro: {resultado_ruta["estacion_origen"]} → {resultado_ruta["estacion_destino"]}\n'
                        f'Tiempo total: {resultado_ruta["tiempo_total"]:.1f} min | Transbordos: {resultado_ruta["transbordos"]}', 
                        fontsize=14)
            ax.set_xlabel('Longitud')
            ax.set_ylabel('Latitud')
            
            # Mostrar el mapa
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"Error en la visualización: {e}")


def main():
    """
    Función principal que implementa la interfaz de usuario del sistema GPS Metro.
    Bucle interactivo para que el usuario calcule rutas.
    """
    # Crear instancia del GPS
    gps_metro = GPSMetro()
    
    # Inicializar sistema (cargar datos)
    if not gps_metro.inicializar_sistema():
        print("No se pudo inicializar el sistema GPS Metro. Saliendo...")
        return
    
    print("\nSISTEMA DE NAVEGACIÓN GPS METRO")
    print("=" * 50)
    
    # Bucle principal de la aplicación
    while True:
        print("\nOpciones:")
        print("1. Calcular ruta en metro")
        print("2. Buscar estación más cercana")
        print("3. Salir")
        
        opcion = input("\nSeleccione una opción (1-3): ").strip()
        
        if opcion == "1":
            # Calcular ruta entre dos direcciones
            origen = input("Dirección de origen: ").strip()
            destino = input("Dirección de destino: ").strip()
            
            if origen and destino:
                resultado = gps_metro.calcular_ruta_metro(origen, destino)
                if resultado:
                    # Mostrar resultados por consola
                    gps_metro.mostrar_ruta_metro(resultado)
                    
                    # Preguntar si quiere ver el mapa
                    visualizar = input("\n¿Desea visualizar la ruta en el mapa? (s/n): ").strip().lower()
                    if visualizar == 's':
                        gps_metro.visualizar_ruta_metro(resultado)
                else:
                    print("No se pudo calcular la ruta en metro")
            else:
                print("Debe ingresar tanto origen como destino")
                
        elif opcion == "2":
            # Buscar estación más cercana a una dirección
            direccion = input("Dirección para buscar estación cercana: ").strip()
            
            if direccion:
                try:
                    # Buscar coordenadas de la dirección
                    lat, lon, direccion_hallada = busca_direccion(direccion, gps_metro.callejero)
                    # Encontrar estación más cercana
                    estacion_cercana = gps_metro.encontrar_estacion_cercana(lat, lon)
                    
                    if estacion_cercana:
                        nombre_estacion = gps_metro.grafo_metro.nodes[estacion_cercana]['nombre']
                        lineas = gps_metro.grafo_metro.nodes[estacion_cercana]['lineas']
                        
                        # Mostrar resultados
                        print(f"\n📍 Estación más cercana a '{direccion_hallada}':")
                        print(f"   • Nombre: {nombre_estacion}")
                        print(f"   • Líneas: {', '.join(lineas)}")
                        print(f"   • Coordenadas: ({lat:.6f}, {lon:.6f})")
                    else:
                        print("No se encontró ninguna estación cercana")
                        
                except AdressNotFoundError as e:
                    print(f"Error: {e}")
                except Exception as e:
                    print(f"Error al buscar estación: {e}")
            else:
                print("Debe ingresar una dirección")
                
        elif opcion == "3":
            # Salir de la aplicación
            print("Saliendo del sistema GPS Metro...")
            break
            
        else:
            print("Opción no válida. Por favor seleccione 1, 2 o 3.")


# Punto de entrada del programa
if __name__ == "__main__":
    main()



        

