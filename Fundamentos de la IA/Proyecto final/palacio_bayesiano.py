"""
Parte 2 - Agente Bayesiano en el Palacio - CORREGIDO PARA EVITAR BUCLES
Implementación del agente que usa inferencia bayesiana para navegar

Este archivo implementa:
1. Palacio con trampas específicas (Fuego, Pinchos, Dardos)
2. Sistema de perceptos diferenciados por tipo de trampa
3. Agente que usa inferencia bayesiana para actualizar creencias
4. Mecanismos anti-bucle y exploración forzada
"""

import numpy as np
import random
import math
import time
from funciones_comunes import *

# ============================================================================
# CLASE PALACIO BAYESIANO - MEJORADA
# ============================================================================

class PalacioBayesiano:
    """
    Palacio con tres tipos de trampas específicas
    
    Mejoras implementadas:
    - Sistema de rastreo de movimientos para detectar bucles
    - Marcado explícito de celdas seguras/visitadas
    - Método para mostrar mapa del conocimiento del agente
    """
    
    def __init__(self, tamano=6):
        self.n = tamano
        self.capitán_pos = (0, 0)
        self.con_kurtz = False
        self.soldado_vivo = True
        self.tengo_granada = True
        self.pasos = 0
        
        # Elementos del palacio
        self.trampa_fuego = None
        self.trampa_pinchos = None
        self.trampa_dardos = None
        self.soldado = None
        self.kurtz = None
        self.salida = None
        
        # Conocimiento y rastreo
        self.celdas_visitadas = [self.capitán_pos]
        self.celdas_seguras = [self.capitán_pos]
        self.celdas_peligrosas = []
        self.perceptos_historia = []
        self.historial_movimientos = []  # Para detectar bucles
        
        # Generar palacio
        print("Generando palacio bayesiano aleatorio...")
        self.generar_palacio()
        print("¡Palacio bayesiano listo!\n")
    
    def generar_palacio(self):
        """Genera posiciones aleatorias para todos los elementos"""
        todas = []
        for i in range(self.n):
            for j in range(self.n):
                if (i, j) != (0, 0):
                    todas.append((i, j))
        
        random.shuffle(todas)
        
        # Asignar elementos
        self.trampa_fuego = todas.pop()
        self.trampa_pinchos = todas.pop()
        self.trampa_dardos = todas.pop()
        self.soldado = todas.pop()
        self.kurtz = todas.pop()
        self.salida = todas.pop()
        
        # Mostrar posiciones (para debugging)
        # print(f"DEBUG - Fuego en: {self.trampa_fuego}")
        # print(f"DEBUG - Pinchos en: {self.trampa_pinchos}")
        # print(f"DEBUG - Dardos en: {self.trampa_dardos}")
        # print(f"DEBUG - Soldado en: {self.soldado}")
        # print(f"DEBUG - Kurtz en: {self.kurtz}")
        # print(f"DEBUG - Salida en: {self.salida}")
    
    def mover(self, direccion):
        """Intenta mover al capitán y actualiza conocimiento"""
        self.pasos += 1
        x, y = self.capitán_pos
        nueva = None
        
        # Calcular nueva posición
        if direccion == 'N' and x > 0:
            nueva = (x-1, y)
        elif direccion == 'S' and x < self.n-1:
            nueva = (x+1, y)
        elif direccion == 'O' and y > 0:
            nueva = (x, y-1)
        elif direccion == 'E' and y < self.n-1:
            nueva = (x, y+1)
        
        if nueva is None:
            return False, f"No puedo ir al {direccion} (pared)"
        
        # Verificar peligros
        peligros = []
        if nueva == self.trampa_fuego:
            peligros.append("fuego")
        if nueva == self.trampa_pinchos:
            peligros.append("pinchos")
        if nueva == self.trampa_dardos:
            peligros.append("dardos")
        if self.soldado_vivo and nueva == self.soldado:
            peligros.append("soldado")
        
        if peligros:
            return False, f"¡Caíste en una trampa de {', '.join(peligros)}!"
        
        # Movimiento exitoso
        self.capitán_pos = nueva
        self.historial_movimientos.append(nueva)
        
        # Limitar tamaño del historial
        if len(self.historial_movimientos) > 20:
            self.historial_movimientos.pop(0)
        
        # Actualizar conocimiento
        if nueva not in self.celdas_visitadas:
            self.celdas_visitadas.append(nueva)
            self.celdas_seguras.append(nueva)  # Si llegamos aquí, es segura
        
        # Verificar si encontramos a Kurtz
        if not self.con_kurtz and nueva == self.kurtz:
            self.con_kurtz = True
            return True, f"¡ENCONTRASTE A KURTZ!"
        
        # Verificar si llegamos a la salida
        if nueva == self.salida:
            if self.con_kurtz:
                return True, f"¡Estás en la salida con Kurtz!"
            else:
                return True, f"Estás en la salida (pero sin Kurtz)"
        
        return True, f"Moví a ({nueva[0]+1},{nueva[1]+1})"
    
    def tirar_granada(self, direccion):
        """Tira la granada en una dirección"""
        if not self.tengo_granada:
            return False, "No tengo granadas."
        
        x, y = self.capitán_pos
        objetivo = None
        
        if direccion == 'N' and x > 0:
            objetivo = (x-1, y)
        elif direccion == 'S' and x < self.n-1:
            objetivo = (x+1, y)
        elif direccion == 'O' and y > 0:
            objetivo = (x, y-1)
        elif direccion == 'E' and y < self.n-1:
            objetivo = (x, y+1)
        
        if objetivo is None:
            return False, "No puedo tirar ahí (pared)"
        
        self.tengo_granada = False
        
        if objetivo == self.soldado and self.soldado_vivo:
            self.soldado_vivo = False
            return True, "¡Granada efectiva! Soldado eliminado."
        elif objetivo == self.kurtz:
            return True, "Kurtz esquiva la granada (¡afortunadamente!)."
        else:
            return True, "Granada a celda vacía."
    
    def intentar_salir(self):
        """Intenta salir del palacio"""
        if self.capitán_pos == self.salida:
            if self.con_kurtz:
                return True, "¡MISIÓN CUMPLIDA! Has rescatado a Kurtz."
            else:
                return False, "No puedes salir sin Kurtz."
        else:
            return False, "No estás en la salida."
    
    def que_siento(self):
        """Devuelve los perceptos del capitán"""
        x, y = self.capitán_pos
        percepciones = []
        
        # Paredes
        if x == 0:
            percepciones.append("pared_norte")
        if x == self.n-1:
            percepciones.append("pared_sur")
        if y == 0:
            percepciones.append("pared_oeste")
        if y == self.n-1:
            percepciones.append("pared_este")
        
        # Estímulos de trampas
        vecinos = self.vecinos_de((x, y))
        
        # Verificar cada tipo de trampa
        if any(v == self.trampa_fuego for v in vecinos):
            percepciones.append("olor_queroseno")
        
        if any(v == self.trampa_pinchos for v in vecinos):
            percepciones.append("suelo_crujiente")
        
        if any(v == self.trampa_dardos for v in vecinos):
            percepciones.append("cables_suelo")
        
        # Ronquido del soldado
        if self.soldado_vivo and any(v == self.soldado for v in vecinos):
            percepciones.append("ronquido")
        
        # Resplandor de la salida
        if (x, y) == self.salida:
            percepciones.append("resplandor_fuerte")
        elif any(v == self.salida for v in vecinos):
            percepciones.append("resplandor_suave")
        
        # Guardar en historial
        self.perceptos_historia.append({
            'pos': (x, y),
            'perceptos': percepciones.copy()
        })
        
        return percepciones
    
    def vecinos_de(self, pos):
        """Devuelve las celdas adyacentes a una posición"""
        x, y = pos
        vecinos = []
        if x > 0:
            vecinos.append((x-1, y))
        if x < self.n-1:
            vecinos.append((x+1, y))
        if y > 0:
            vecinos.append((x, y-1))
        if y < self.n-1:
            vecinos.append((x, y+1))
        return vecinos
    
    def mostrar_mapa_conocido(self):
        """Muestra lo que el agente conoce del palacio"""
        print("\n" + "-"*40)
        print("MAPA CONOCIDO POR EL AGENTE")
        print("-"*40)
        
        for i in range(self.n):
            fila = ""
            for j in range(self.n):
                celda = (i, j)
                
                if celda == self.capitán_pos:
                    if self.con_kurtz:
                        fila += "[CK]"
                    else:
                        fila += "[CW]"
                elif celda in self.celdas_visitadas:
                    if celda in self.celdas_seguras:
                        fila += "[.] "
                    else:
                        fila += "[?] "
                else:
                    fila += "[?] "
            
            print(f"Fila {i+1}: {fila}")
        
        print(f"Posición: ({self.capitán_pos[0]+1},{self.capitán_pos[1]+1})")
        if self.con_kurtz:
            print("Tienes a Kurtz contigo.")
        print("-"*40)

    def detectar_bucle(self, ultimos_n=8):  # Reducir de 10 a 8 para detectar antes
        """Detecta si el agente está en un bucle"""
        if len(self.historial_movimientos) < ultimos_n:
            return False
        
        # Tomar los últimos N movimientos
        ultimos = self.historial_movimientos[-ultimos_n:]
        
        # DEBUG: Mostrar lo que está analizando
        # print(f"[DETECCIÓN BUCLE] Analizando últimos {ultimos_n}: {ultimos}")
        
        # Si hay pocas posiciones únicas, probablemente es un bucle
        posiciones_unicas = len(set(ultimos))
        
        # También verificar patrones repetitivos
        if posiciones_unicas <= 3:  # Reducir de 2 a 3
            # print(f"[DETECCIÓN BUCLE] ¡BUCLE DETECTADO! Solo {posiciones_unicas} posiciones únicas")
            return True
        
        # Verificar si estamos yendo y viniendo entre las mismas celdas
        if len(ultimos) >= 6:
            # Patrón: A-B-A-B-A-B
            patron_repetido = True
            for i in range(2, len(ultimos) - 2, 2):
                if ultimos[i] != ultimos[i-2]:
                    patron_repetido = False
                    break
            
            if patron_repetido:
                # print(f"[DETECCIÓN BUCLE] ¡BUCLE DETECTADO! Patrón A-B-A-B...")
                return True
        
        # Verificar si hemos visitado la misma celda muchas veces
        celda_actual = self.capitán_pos
        apariciones = ultimos.count(celda_actual)
        if apariciones >= ultimos_n // 2:  # Si aparece en al menos la mitad
            # print(f"[DETECCIÓN BUCLE] ¡BUCLE DETECTADO! Celda {celda_actual} aparece {apariciones} veces")
            return True
        
        return False

    def distancia_manhattan(self, pos1, pos2):
        """Calcula la distancia de Manhattan entre dos posiciones"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

# ============================================================================
# CLASE AGENTE BAYESIANO - MEJORADA CON ANTI-BUCLES
# ============================================================================

class AgenteBayesiano:
    """
    Agente bayesiano con mecanismos anti-bucle
    
    Mejoras implementadas:
    1. Contador de intentos por dirección
    2. Detección de bucles basada en historial
    3. Estrategia de escape cuando detecta bucle
    4. Exploración forzada de nuevas áreas
    5. Memoria de celdas ya evaluadas
    """
    
    def __init__(self, palacio, umbral_riesgo=0.2):
        self.p = palacio
        self.umbral_riesgo = umbral_riesgo
        
        # Distribuciones bayesianas
        self.prior = self.inicializar_prior_uniforme()
        self.prob_fuego = self.prior.copy()
        self.prob_pinchos = self.prior.copy()
        self.prob_dardos = self.prior.copy()
        self.prob_soldado = self.prior.copy()
        self.prob_salida = self.prior.copy()
        
        # Riesgo y conocimiento
        self.riesgo_total = np.zeros((self.p.n, self.p.n))
        self.historial_bayes = []
        
        # Mecanismos anti-bucle
        self.contador_intentos = {}  # Cuántas veces intentamos cada dirección
        self.celdas_evaluadas = set()  # Celdas ya consideradas para movimiento
        self.estrategia_escape = False  # Modo especial para escapar de bucles
        self.pasos_sin_novedad = 0  # Pasos sin descubrir nueva celda
        
        print(f"[AGENTE BAYESIANO] Inicializado con umbral de riesgo: {umbral_riesgo}")
        print(f"[AGENTE BAYESIANO] Mecanismos anti-bucle activados")
    
    def inicializar_prior_uniforme(self):
        """Distribución a priori uniforme"""
        n_celdas = self.p.n * self.p.n
        prior = {}
        for i in range(self.p.n):
            for j in range(self.p.n):
                celda = (i, j)
                if celda == self.p.capitán_pos:
                    prior[celda] = 0.0
                else:
                    prior[celda] = 1.0 / (n_celdas - 1)
        return prior
    
    def actualizar_creencias(self, percepciones):
        """Actualiza distribuciones con regla de Bayes"""
        pos_actual = self.p.capitán_pos
        
        # Actualizar cada elemento
        self.actualizar_elemento('fuego', 'olor_queroseno' in percepciones, pos_actual)
        self.actualizar_elemento('pinchos', 'suelo_crujiente' in percepciones, pos_actual)
        self.actualizar_elemento('dardos', 'cables_suelo' in percepciones, pos_actual)
        self.actualizar_elemento('soldado', 'ronquido' in percepciones, pos_actual)
        
        # Actualizar salida (lógica diferente)
        self.actualizar_salida('resplandor_suave' in percepciones or 
                              'resplandor_fuerte' in percepciones, pos_actual)
        
        # Recalcular riesgo total
        self.calcular_riesgo_total()
        
        # Guardar historial
        self.historial_bayes.append({
            'paso': self.p.pasos,
            'pos': pos_actual,
            'perceptos': percepciones,
            'riesgo_promedio': np.mean(self.riesgo_total)
        })
    
    def actualizar_elemento(self, elemento, estímulo_detectado, pos_actual):
        """Actualiza distribución de un elemento específico"""
        if elemento == 'fuego':
            dist = self.prob_fuego
        elif elemento == 'pinchos':
            dist = self.prob_pinchos
        elif elemento == 'dardos':
            dist = self.prob_dardos
        elif elemento == 'soldado':
            dist = self.prob_soldado
        else:
            return
        
        # Calcular verosimilitud
        verosimilitud = {}
        for celda in dist:
            if self.estímulo_detectable_desde(celda, pos_actual):
                p_detectar = 1.0
            else:
                p_detectar = 0.0
            
            if estímulo_detectado:
                verosimilitud[celda] = p_detectar
            else:
                verosimilitud[celda] = 1.0 - p_detectar
        
        # Aplicar Bayes
        nueva_dist = {}
        evidencia = 0.0
        
        for celda in dist:
            nueva_dist[celda] = dist[celda] * verosimilitud[celda]
            evidencia += nueva_dist[celda]
        
        # Normalizar
        if evidencia > 0:
            for celda in nueva_dist:
                nueva_dist[celda] /= evidencia
        
        # Actualizar
        if elemento == 'fuego':
            self.prob_fuego = nueva_dist
        elif elemento == 'pinchos':
            self.prob_pinchos = nueva_dist
        elif elemento == 'dardos':
            self.prob_dardos = nueva_dist
        elif elemento == 'soldado':
            self.prob_soldado = nueva_dist
    
    def actualizar_salida(self, resplandor_detectado, pos_actual):
        """Actualiza distribución de la salida (lógica especial)"""
        dist = self.prob_salida
        
        # Si detectamos resplandor, aumentar probabilidad en celdas adyacentes
        if resplandor_detectado:
            # Aumentar probabilidad en celdas adyacentes
            vecinos = self.p.vecinos_de(pos_actual)
            for celda in dist:
                if celda in vecinos or celda == pos_actual:
                    dist[celda] *= 2.0  # Doblar la probabilidad
        else:
            # Reducir probabilidad en celdas adyacentes
            vecinos = self.p.vecinos_de(pos_actual)
            for celda in dist:
                if celda in vecinos or celda == pos_actual:
                    dist[celda] *= 0.5  # Reducir a la mitad
        
        # Normalizar
        total = sum(dist.values())
        if total > 0:
            for celda in dist:
                dist[celda] /= total
        
        self.prob_salida = dist
    
    def estímulo_detectable_desde(self, celda_elemento, celda_observador):
        """Determina si un estímulo es detectable"""
        if celda_elemento == celda_observador:
            return True
        vecinos = self.p.vecinos_de(celda_elemento)
        return celda_observador in vecinos
    
    def calcular_riesgo_total(self):
        """Calcula riesgo total por celda"""
        self.riesgo_total = np.zeros((self.p.n, self.p.n))
        
        for i in range(self.p.n):
            for j in range(self.p.n):
                celda = (i, j)
                riesgo = 0
                riesgo += self.prob_fuego.get(celda, 0)
                riesgo += self.prob_pinchos.get(celda, 0)
                riesgo += self.prob_dardos.get(celda, 0)
                
                if self.p.soldado_vivo:
                    riesgo += self.prob_soldado.get(celda, 0)
                
                self.riesgo_total[i][j] = min(riesgo, 1.0)
    
    def decidir_movimiento(self):
        """
        Decisión de movimiento mejorada con anti-bucles
        
        Estrategias en orden:
        1. Si tenemos a Kurtz, buscar salida
        2. Si detectamos bucle, activar estrategia de escape
        3. Usar granada si hay soldado cerca
        4. Movimiento basado en riesgo (con exploración forzada)
        5. Retroceder si estamos atrapados
        """
        pos_actual = self.p.capitán_pos
    
        # Verificar si estamos en un bucle (llamar la función con parámetro)
        if self.p.detectar_bucle(ultimos_n=8):
            print("  [ANTI-BUCLE] ¡Bucle detectado! Activando estrategia de escape")
            self.estrategia_escape = True
            self.pasos_sin_novedad = 0
        
        # ESTRATEGIA DE ESCAPE (si detectamos bucle)
        if self.estrategia_escape:
            print("  [ESCAPE] Ejecutando estrategia de escape...")
            movimiento = self.estrategia_escape_bucle(pos_actual)
            if movimiento:
                # Después de usar escape, desactivarlo después de unos pasos
                if self.p.pasos > 10 and random.random() < 0.3:
                    self.estrategia_escape = False
                    print("  [ESCAPE] Desactivando modo escape")
                return movimiento
        
        # ESTRATEGIA 1: Si tenemos a Kurtz, buscar salida
        if self.p.con_kurtz:
            mejor_dir = self.buscar_salida(pos_actual)
            if mejor_dir:
                return 'MOVER', mejor_dir
        
        # ESTRATEGIA 2: Granada contra soldado
        if self.p.tengo_granada and self.p.soldado_vivo:
            if self.p.perceptos_historia and 'ronquido' in self.p.perceptos_historia[-1]['perceptos']:
                dir_soldado = self.inferir_direccion_soldado(pos_actual)
                if dir_soldado:
                    return 'GRANADA', dir_soldado
        
        # ESTRATEGIA 3: Movimiento inteligente con exploración
        movimiento = self.movimiento_inteligente_con_exploracion(pos_actual)
        if movimiento:
            return movimiento
        
        # ESTRATEGIA 4: Retroceder
        if len(self.p.celdas_visitadas) > 1:
            celda_anterior = self.p.celdas_visitadas[-2]
            direccion = self.direccion_hacia(pos_actual, celda_anterior)
            if direccion:
                return 'MOVER', direccion
        
        # ESTRATEGIA 5: Movimiento aleatorio de último recurso
        print("  [ÚLTIMO RECURSO] Usando movimiento aleatorio")
        return self.movimiento_aleatorio_seguro(pos_actual)
    
    def estrategia_escape_bucle(self, pos_actual):
        """
        Estrategia especial para escapar de bucles - CORREGIDA
        """
        print("  [ESCAPE] Buscando celda no visitada...")
        
        # Obtener TODAS las celdas posibles, no solo vecinas
        todas_celdas = []
        for i in range(self.p.n):
            for j in range(self.p.n):
                celda = (i, j)
                if celda not in self.p.celdas_visitadas:
                    todas_celdas.append(celda)
        
        # Ordenar por distancia desde la posición actual
        todas_celdas.sort(key=lambda c: self.p.distancia_manhattan(pos_actual, c))
        
        # Buscar camino a alguna celda no visitada
        for celda_objetivo in todas_celdas:
            # Intentar encontrar camino seguro hacia la celda objetivo
            camino = self.encontrar_camino_seguro(pos_actual, celda_objetivo)
            if camino and len(camino) > 1:
                siguiente = camino[1]  # El primer paso del camino
                # Calcular dirección
                if siguiente[0] < pos_actual[0]:
                    return 'MOVER', 'N'
                elif siguiente[0] > pos_actual[0]:
                    return 'MOVER', 'S'
                elif siguiente[1] < pos_actual[1]:
                    return 'MOVER', 'O'
                elif siguiente[1] > pos_actual[1]:
                    return 'MOVER', 'E'
        
        # Si no encuentra camino a celdas no visitadas, intentar cualquier movimiento con riesgo controlado
        print("  [ESCAPE] No hay celdas no visitadas accesibles, tomando riesgos...")
        
        # Aumentar temporalmente el umbral de riesgo
        umbral_temporal = self.umbral_riesgo * 3  # 90% de riesgo permitido
        
        for direccion, vecino in self.obtener_vecinos_con_direccion(pos_actual):
            if vecino is None:
                continue
            
            riesgo = self.riesgo_total[vecino[0]][vecino[1]]
            
            # En modo escape extremo, aceptar más riesgo
            if riesgo < umbral_temporal:
                # Verificar que no sea una celda mortal conocida
                if vecino in self.p.celdas_peligrosas:
                    continue
                
                print(f"  [ESCAPE] Movimiento de riesgo a {vecino} con riesgo {riesgo:.2f}")
                return 'MOVER', direccion
        
        return None

    def encontrar_camino_seguro(self, inicio, objetivo):
        """
        Encuentra un camino seguro entre dos celdas usando BFS
        """
        from collections import deque
        
        cola = deque()
        cola.append((inicio, []))
        visitados = set([inicio])
        
        while cola:
            actual, camino = cola.popleft()
            
            if actual == objetivo:
                return [inicio] + camino
            
            for direccion, vecino in self.obtener_vecinos_con_direccion(actual):
                if vecino is None or vecino in visitados:
                    continue
                
                # En modo escape, ser más permisivo con el riesgo
                riesgo = self.riesgo_total[vecino[0]][vecino[1]]
                if riesgo < self.umbral_riesgo * 2:  # Doble umbral en escape
                    visitados.add(vecino)
                    nuevo_camino = camino + [vecino]
                    cola.append((vecino, nuevo_camino))
        
        return None

    def encontrar_camino_seguro(self, inicio, objetivo):
        """
        Encuentra un camino seguro entre dos celdas usando BFS
        """
        from collections import deque
        
        cola = deque()
        cola.append((inicio, []))
        visitados = set([inicio])
        
        while cola:
            actual, camino = cola.popleft()
            
            if actual == objetivo:
                return [inicio] + camino
            
            for direccion, vecino in self.obtener_vecinos_con_direccion(actual):
                if vecino is None or vecino in visitados:
                    continue
                
                # En modo escape, ser más permisivo con el riesgo
                riesgo = self.riesgo_total[vecino[0]][vecino[1]]
                if riesgo < self.umbral_riesgo * 2:  # Doble umbral en escape
                    visitados.add(vecino)
                    nuevo_camino = camino + [vecino]
                    cola.append((vecino, nuevo_camino))
        
        return None

    def movimiento_inteligente_con_exploracion(self, pos_actual):
        """
        Movimiento que balancea seguridad y exploración
        """
        mejores_movimientos = []
        
        for direccion, vecino in self.obtener_vecinos_con_direccion(pos_actual):
            if vecino is None:
                continue
            
            # Calcular puntuación para este movimiento
            puntuacion = 0
            
            # Factor 1: Riesgo (negativo)
            riesgo = self.riesgo_total[vecino[0]][vecino[1]]
            if riesgo >= self.umbral_riesgo:
                continue  # Demasiado riesgo, saltar
            
            puntuacion -= riesgo * 10
            
            # Factor 2: Exploración (positivo si no visitado)
            if vecino not in self.p.celdas_visitadas:
                puntuacion += 10  # Aumentar de 5 a 10 para mayor incentivo
                print(f"  [EXPLORACIÓN] Celda {vecino} no visitada (+10 puntos)")
            
            # Factor 3: Evitar repetición (negativo si ya intentamos esta dirección)
            intentos = self.contador_intentos.get(direccion, 0)
            puntuacion -= intentos * 3  # Aumentar penalización de 2 a 3
            
            # Factor 4: Proximidad a áreas no exploradas
            if self.es_frontera(vecino):
                puntuacion += 5  # Aumentar de 3 a 5
            
            # Factor 5: Si lleva a pared, penalizar
            x, y = vecino
            if x == 0 or x == self.p.n-1 or y == 0 or y == self.p.n-1:
                puntuacion -= 2
            
            mejores_movimientos.append((direccion, vecino, puntuacion))
        
        # Ordenar por puntuación (mayor primero)
        mejores_movimientos.sort(key=lambda x: x[2], reverse=True)
        
        if mejores_movimientos:
            mejor = mejores_movimientos[0]
            
            # Si la mejor puntuación es muy baja, considerar exploración forzada
            if mejor[2] < -5 and len(self.p.celdas_visitadas) < self.p.n * self.p.n / 2:
                print(f"  [ADVERTENCIA] Puntuación muy baja ({mejor[2]}). Considerando exploración forzada...")
                exploracion = self.exploracion_forzada(pos_actual)
                if exploracion:
                    return exploracion
            
            # Actualizar contador de intentos
            self.contador_intentos[mejor[0]] = self.contador_intentos.get(mejor[0], 0) + 1
            
            # Limpiar contadores periódicamente
            if self.p.pasos % 5 == 0:  # Reducir de 10 a 5
                for dir in list(self.contador_intentos.keys()):
                    if self.contador_intentos[dir] > 0:
                        self.contador_intentos[dir] = max(0, self.contador_intentos[dir] - 2)  # Reducir más rápido
            
            print(f"  [DECISIÓN] Elegido {mejor[0]} con puntuación {mejor[2]:.1f}")
            return 'MOVER', mejor[0]
        
        return None

    def calcular_nueva_posicion(self, direccion):
        """Calcula la nueva posición dado un movimiento"""
        x, y = self.p.capitán_pos
        if direccion == 'N' and x > 0:
            return (x-1, y)
        elif direccion == 'S' and x < self.p.n-1:
            return (x+1, y)
        elif direccion == 'O' and y > 0:
            return (x, y-1)
        elif direccion == 'E' and y < self.p.n-1:
            return (x, y+1)
        return None

    def movimiento_aleatorio_seguro(self, pos_actual):
        """Movimiento aleatorio pero seguro"""
        direcciones_posibles = []
        
        for direccion, vecino in self.obtener_vecinos_con_direccion(pos_actual):
            if vecino is None:
                continue
            
            riesgo = self.riesgo_total[vecino[0]][vecino[1]]
            if riesgo < 0.5:  # Umbral seguro para movimiento aleatorio
                direcciones_posibles.append((direccion, vecino))
        
        if direcciones_posibles:
            # Preferir direcciones no intentadas recientemente
            for direccion, vecino in direcciones_posibles:
                if self.contador_intentos.get(direccion, 0) == 0:
                    return 'MOVER', direccion
            
            # Si todas han sido intentadas, elegir aleatoriamente
            direccion, vecino = random.choice(direcciones_posibles)
            return 'MOVER', direccion
        
        return 'RENDIRSE', None
    
    def obtener_vecinos_con_direccion(self, pos_actual):
        """Devuelve vecinos con sus direcciones"""
        x, y = pos_actual
        vecinos = []
        
        if x > 0:
            vecinos.append(('N', (x-1, y)))
        if x < self.p.n-1:
            vecinos.append(('S', (x+1, y)))
        if y > 0:
            vecinos.append(('O', (x, y-1)))
        if y < self.p.n-1:
            vecinos.append(('E', (x, y+1)))
        
        return vecinos
    
    def es_frontera(self, celda):
        """Determina si una celda está en la frontera de lo explorado"""
        if celda not in self.p.celdas_visitadas:
            vecinos = self.p.vecinos_de(celda)
            # Es frontera si tiene al menos un vecino visitado
            return any(v in self.p.celdas_visitadas for v in vecinos)
        return False
    
    def buscar_salida(self, pos_actual):
        """Busca dirección hacia salida más probable"""
        mejor_celda = None
        mejor_prob = -1
        
        for i in range(self.p.n):
            for j in range(self.p.n):
                celda = (i, j)
                prob = self.prob_salida.get(celda, 0)
                if prob > mejor_prob:
                    mejor_prob = prob
                    mejor_celda = celda
        
        if mejor_celda:
            return self.direccion_hacia(pos_actual, mejor_celda)
        return None
    
    def inferir_direccion_soldado(self, pos_actual):
        """Infere dirección del soldado"""
        mejores_direcciones = []
        
        for direccion, vecino in self.obtener_vecinos_con_direccion(pos_actual):
            if vecino is None:
                continue
            
            prob = self.prob_soldado.get(vecino, 0)
            if prob > 0.3:
                mejores_direcciones.append((direccion, prob))
        
        if mejores_direcciones:
            mejores_direcciones.sort(key=lambda x: x[1], reverse=True)
            return mejores_direcciones[0][0]
        
        return None
    
    def exploracion_forzada(self, pos_actual):
        """
        Estrategia de exploración forzada cuando estamos atrapados
        """
        print("  [EXPLORACIÓN FORZADA] Buscando celdas no visitadas...")
        
        # Obtener todas las celdas no visitadas
        celdas_no_visitadas = []
        for i in range(self.p.n):
            for j in range(self.p.n):
                celda = (i, j)
                if celda not in self.p.celdas_visitadas:
                    celdas_no_visitadas.append(celda)
        
        if not celdas_no_visitadas:
            print("  [EXPLORACIÓN FORZADA] ¡Todas las celdas visitadas!")
            return None
        
        # Ordenar por distancia a la posición actual
        celdas_no_visitadas.sort(key=lambda c: self.p.distancia_manhattan(pos_actual, c))
        
        # Intentar llegar a la celda más cercana
        for celda_objetivo in celdas_no_visitadas[:3]:  # Intentar las 3 más cercanas
            # Calcular dirección hacia la celda objetivo
            direccion = self.direccion_hacia(pos_actual, celda_objetivo)
            if direccion:
                # Verificar si es seguro mover en esa dirección
                nueva_pos = self.calcular_nueva_posicion(direccion)
                if nueva_pos:
                    riesgo = self.riesgo_total[nueva_pos[0]][nueva_pos[1]]
                    if riesgo < self.umbral_riesgo * 1.5:  # Permitir más riesgo en exploración
                        print(f"  [EXPLORACIÓN FORZADA] Mover {direccion} hacia celda no visitada {celda_objetivo}")
                        return 'MOVER', direccion
        
        return None

    def direccion_hacia(self, desde, hacia):
        """Calcula dirección para ir de una celda a otra"""
        dx = hacia[0] - desde[0]
        dy = hacia[1] - desde[1]
        
        if dx < 0 and abs(dx) >= abs(dy):
            return 'N'
        elif dx > 0 and abs(dx) >= abs(dy):
            return 'S'
        elif dy < 0:
            return 'O'
        elif dy > 0:
            return 'E'
        
        return None
    
    def mostrar_distribuciones(self):
        """Muestra distribuciones de probabilidad"""
        print("\n" + "="*60)
        print("DISTRIBUCIONES BAYESIANAS")
        print("="*60)
        
        # Crear matrices para visualización
        matriz_riesgo = np.zeros((self.p.n, self.p.n))
        matriz_salida = np.zeros((self.p.n, self.p.n))
        
        for i in range(self.p.n):
            for j in range(self.p.n):
                celda = (i, j)
                matriz_riesgo[i][j] = self.riesgo_total[i][j]
                matriz_salida[i][j] = self.prob_salida.get(celda, 0)
        
        print("\nMapa de Riesgo Total:")
        crear_heatmap_probabilidades(matriz_riesgo, "Riesgo Total")
        
        print("\nMapa de Probabilidad de Salida:")
        crear_heatmap_probabilidades(matriz_salida, "Probabilidad de Salida")
        
        # Mostrar probabilidades más altas
        print("\nProbabilidades más altas:")
        elementos = [
            ("Fuego", self.prob_fuego),
            ("Pinchos", self.prob_pinchos),
            ("Dardos", self.prob_dardos),
            ("Soldado", self.prob_soldado)
        ]
        
        for nombre, dist in elementos:
            if dist:
                max_celda = max(dist.items(), key=lambda x: x[1])
                if max_celda[1] > 0.1:
                    print(f"  {nombre}: {max_celda[0]} con {max_celda[1]:.2%}")
        
        print("="*60)
    
    def mostrar_estado_agente(self):
        """Muestra estado interno del agente"""
        print("\n" + "-"*40)
        print("ESTADO DEL AGENTE")
        print("-"*40)
        print(f"Umbral de riesgo: {self.umbral_riesgo}")
        print(f"Estrategia escape: {'ACTIVA' if self.estrategia_escape else 'inactiva'}")
        print(f"Pasos sin novedad: {self.pasos_sin_novedad}")
        print(f"Celdas visitadas: {len(self.p.celdas_visitadas)}")
        print(f"Contadores intentos: {self.contador_intentos}")
        print("-"*40)

# ============================================================================
# FUNCIÓN PRINCIPAL - MODO BAYESIANO MEJORADO
# ============================================================================

def modo_bayesiano():
    """Ejecuta el modo bayesiano con anti-bucles"""
    print("\n" + ">"*30)
    print("MODO: AGENTE BAYESIANO (CON ANTI-BUCLES)")
    print(">"*30)
    print("\nEl agente usará inferencia bayesiana para navegar.")
    print("Trampas específicas: Fuego, Pinchos, Dardos")
    print("Con mecanismos anti-bucle activados.")
    print("-"*40)
    
    try:
        umbral = float(input("Umbral de riesgo (0.1-0.5, default 0.3): ") or "0.3")
        if umbral < 0.1 or umbral > 0.5:
            print("Umbral fuera de rango, usando 0.3")
            umbral = 0.3
    except ValueError:
        print("Valor inválido, usando 0.3")
        umbral = 0.3
    
    # PASO 1: Ejecutar simulación interactiva detallada
    print("\n" + "="*60)
    print("INICIANDO SIMULACIÓN INTERACTIVA")
    print("="*60)
    
    resultado_detallado = ejecutar_simulacion_interactiva(umbral)
    
    # PASO 2: Preguntar si quiere hacer más simulaciones para estadísticas
    print("\n" + "="*60)
    print("¿ANÁLISIS ESTADÍSTICO?")
    print("="*60)
    
    continuar = input("\n¿Deseas ejecutar más simulaciones para análisis estadístico? (s/n): ").strip().lower()
    
    if continuar == 's':
        try:
            n_simulaciones = int(input(f"Número de simulaciones adicionales (recomendado 10-100): ") or "10")
            if n_simulaciones < 1:
                print("Número inválido, usando 10")
                n_simulaciones = 10
        except ValueError:
            print("Valor inválido, usando 10")
            n_simulaciones = 10
        
        # PASO 3: Ejecutar simulaciones adicionales
        print(f"\nEjecutando {n_simulaciones} simulaciones adicionales para análisis estadístico...")
        
        # Incluir la simulación detallada en las estadísticas
        resultados_totales = [resultado_detallado]
        
        # Ejecutar simulaciones adicionales
        for i in range(n_simulaciones):
            print(f"  Simulación adicional {i+1}/{n_simulaciones}...")
            
            # Crear nuevo palacio para cada simulación
            palacio = PalacioBayesiano()
            agente = AgenteBayesiano(palacio, umbral)
            
            # Ejecutar simulación sin mostrar detalles
            resultado = ejecutar_simulacion_rapida(palacio, agente)
            resultados_totales.append(resultado)
            
            # Mostrar progreso breve
            if resultado['exito']:
                print(f"     Éxito en {resultado['pasos']} pasos")
            else:
                print(f"     Fracaso ({resultado['motivo_fin']})")
        
        # PASO 4: Mostrar estadísticas completas
        mostrar_estadisticas_completas(resultados_totales, umbral)
    
    else:
        print("\nFinalizando modo bayesiano...")
        print("¡Gracias por usar el agente bayesiano!")

def ejecutar_simulacion_interactiva(umbral_riesgo=0.3, max_pasos=200):
    """
    Ejecuta una simulación interactiva detallada del agente bayesiano
    
    Returns:
        dict: Resultados de la simulación
    """
    palacio = PalacioBayesiano()
    agente = AgenteBayesiano(palacio, umbral_riesgo)
    
    exito = False
    motivo_fin = "límite de pasos"
    
    for paso in range(1, max_pasos + 1):
        print(f"\n" + "="*60)
        print(f"PASO {paso}")
        print(f"Posición: ({palacio.capitán_pos[0]+1},{palacio.capitán_pos[1]+1})")
        print("="*60)
        
        # Mostrar mapa conocido
        palacio.mostrar_mapa_conocido()
        
        # Obtener perceptos
        percepciones = palacio.que_siento()
        print("Perceptos:", ", ".join(percepciones) if percepciones else "(ninguno)")
        
        # Actualizar creencias
        agente.actualizar_creencias(percepciones)
        
        # Mostrar estado del agente (cada 10 pasos)
        if paso % 10 == 0:
            agente.mostrar_estado_agente()
        
        # Mostrar distribuciones (cada 10 pasos)
        if paso % 10 == 0:
            agente.mostrar_distribuciones()
        
        # Decidir y ejecutar acción
        accion, parametro = agente.decidir_movimiento()
        
        if accion == 'MOVER':
            print(f"\n[AGENTE] Decisión: Mover {parametro}")
            ok, msg = palacio.mover(parametro)
            print(f"Resultado: {msg}")
            
            if not ok:
                print("\n¡EL AGENTE MURIÓ!")
                motivo_fin = "muerte del agente"
                break
        
        elif accion == 'GRANADA':
            print(f"\n[AGENTE] Decisión: Tirar granada al {parametro}")
            ok, msg = palacio.tirar_granada(parametro)
            print(f"Resultado: {msg}")
        
        elif accion == 'RENDIRSE':
            print("\n[AGENTE] Se rinde - atrapado sin opciones")
            motivo_fin = "rendición"
            break
        
        # Verificar victoria
        if palacio.con_kurtz and palacio.capitán_pos == palacio.salida:
            print("\n" + "="*60)
            print("¡MISIÓN CUMPLIDA CON BAYES!")
            print("="*60)
            exito = True
            motivo_fin = "éxito"
            break
        
        # Pausa breve
        time.sleep(0.1)
    
    # Resultados finales
    print("\n" + "="*60)
    print("RESULTADOS FINALES DE LA SIMULACIÓN INTERACTIVA")
    print("="*60)
    print(f"Pasos: {palacio.pasos}")
    print(f"Kurtz encontrado: {'SÍ' if palacio.con_kurtz else 'NO'}")
    print(f"Soldado eliminado: {'SÍ' if not palacio.soldado_vivo else 'NO'}")
    print(f"Granada usada: {'SÍ' if not palacio.tengo_granada else 'NO'}")
    print(f"Celdas exploradas: {len(palacio.celdas_visitadas)}/{palacio.n*palacio.n}")
    
    if exito:
        print("\n¡AGENTE BAYESIANO EXITOSO!")
    else:
        print("\nMisión fallida o incompleta")
    
    print("="*60)
    
    # Mostrar análisis final
    if palacio.pasos > 0:
        agente.mostrar_distribuciones()
        
        print("\nMAPA REAL (para comparación):")
        print(f"Fuego: {palacio.trampa_fuego}")
        print(f"Pinchos: {palacio.trampa_pinchos}")
        print(f"Dardos: {palacio.trampa_dardos}")
        print(f"Soldado: {palacio.soldado}")
        print(f"Kurtz: {palacio.kurtz}")
        print(f"Salida: {palacio.salida}")
    
    # Devolver resultados
    return {
        'exito': exito,
        'motivo_fin': motivo_fin,
        'pasos': palacio.pasos,
        'kurtz_encontrado': palacio.con_kurtz,
        'soldado_eliminado': not palacio.soldado_vivo,
        'granada_usada': not palacio.tengo_granada,
        'celdas_exploradas': len(palacio.celdas_visitadas),
        'celdas_totales': palacio.n * palacio.n,
        'umbral_riesgo': umbral_riesgo
    }

def ejecutar_simulacion_rapida(palacio, agente, max_pasos=200):
    """
    Ejecuta una simulación rápida (sin mostrar detalles)
    
    Args:
        palacio: Instancia de PalacioBayesiano
        agente: Instancia de AgenteBayesiano
        max_pasos: Máximo número de pasos
    
    Returns:
        dict: Resultados de la simulación
    """
    exito = False
    motivo_fin = "límite de pasos"
    
    for paso in range(1, max_pasos + 1):
        # Obtener perceptos
        percepciones = palacio.que_siento()
        
        # Actualizar creencias
        agente.actualizar_creencias(percepciones)
        
        # Decidir y ejecutar acción
        accion, parametro = agente.decidir_movimiento()
        
        if accion == 'MOVER':
            ok, msg = palacio.mover(parametro)
            if not ok:
                motivo_fin = "muerte del agente"
                break
        
        elif accion == 'RENDIRSE':
            motivo_fin = "rendición"
            break
        
        # Verificar victoria
        if palacio.con_kurtz and palacio.capitán_pos == palacio.salida:
            exito = True
            motivo_fin = "éxito"
            break
    
    return {
        'exito': exito,
        'motivo_fin': motivo_fin,
        'pasos': palacio.pasos,
        'kurtz_encontrado': palacio.con_kurtz,
        'soldado_eliminado': not palacio.soldado_vivo,
        'granada_usada': not palacio.tengo_granada,
        'celdas_exploradas': len(palacio.celdas_visitadas),
        'celdas_totales': palacio.n * palacio.n,
        'umbral_riesgo': agente.umbral_riesgo
    }

def mostrar_estadisticas_completas(resultados, umbral):
    """
    Muestra estadísticas completas de todas las simulaciones
    """
    print("\n" + "="*60)
    print("ANÁLISIS ESTADÍSTICO COMPLETO")
    print("="*60)
    print(f"Total de simulaciones: {len(resultados)}")
    print(f"Umbral de riesgo: {umbral}")
    print("-"*60)
    
    # Separar la simulación detallada de las rápidas
    sim_detallada = resultados[0]
    sim_rapidas = resultados[1:]
    
    print("\nSIMULACIÓN INTERACTIVA DETALLADA:")
    print(f"  Resultado: {'ÉXITO' if sim_detallada['exito'] else 'FRACASO'}")
    print(f"  Pasos: {sim_detallada['pasos']}")
    print(f"  Motivo: {sim_detallada['motivo_fin']}")
    print(f"  Kurtz encontrado: {'SÍ' if sim_detallada['kurtz_encontrado'] else 'NO'}")
    print(f"  Celdas exploradas: {sim_detallada['celdas_exploradas']}/{sim_detallada['celdas_totales']}")
    
    if sim_rapidas:
        print("\n" + "-"*60)
        print(f"ESTADÍSTICAS DE {len(sim_rapidas)} SIMULACIONES RÁPIDAS:")
        print("-"*60)
        
        # Calcular estadísticas
        exitos = sum(1 for r in sim_rapidas if r['exito'])
        fracasos = len(sim_rapidas) - exitos
        
        # Incluir la detallada en el total si se desea
        total_con_detallada = len(resultados)
        exitos_con_detallada = exitos + (1 if sim_detallada['exito'] else 0)
        
        # Razones de fracaso
        razones_fracaso = {}
        for r in sim_rapidas:
            if not r['exito']:
                razon = r['motivo_fin']
                razones_fracaso[razon] = razones_fracaso.get(razon, 0) + 1
        
        # Métricas promedio
        pasos_promedio = sum(r['pasos'] for r in sim_rapidas) / len(sim_rapidas)
        exploracion_promedio = sum(r['celdas_exploradas'] for r in sim_rapidas) / len(sim_rapidas)
        celdas_totales = sim_rapidas[0]['celdas_totales']
        
        # Porcentajes
        kurtz_encontrados = sum(1 for r in sim_rapidas if r['kurtz_encontrado'])
        soldados_eliminados = sum(1 for r in sim_rapidas if r['soldado_eliminado'])
        granadas_usadas = sum(1 for r in sim_rapidas if r['granada_usada'])
        
        print(f"\nRESUMEN ESTADÍSTICO:")
        print(f"  Tasa de éxito (rápidas): {exitos/len(sim_rapidas)*100:.1f}% ({exitos}/{len(sim_rapidas)})")
        print(f"  Tasa de éxito (total): {exitos_con_detallada/total_con_detallada*100:.1f}% ({exitos_con_detallada}/{total_con_detallada})")
        
        if fracasos > 0:
            print(f"\nRazones de fracaso en simulaciones rápidas:")
            for razon, cuenta in razones_fracaso.items():
                print(f"  - {razon}: {cuenta} veces ({cuenta/fracasos*100:.1f}% de los fracasos)")
        
        print(f"\nMÉTRICAS PROMEDIO (simulaciones rápidas):")
        print(f"  Pasos promedio: {pasos_promedio:.1f}")
        print(f"  Exploración: {exploracion_promedio:.1f}/{celdas_totales} celdas ({exploracion_promedio/celdas_totales*100:.1f}%)")
        print(f"  Kurtz encontrado: {kurtz_encontrados/len(sim_rapidas)*100:.1f}%")
        print(f"  Soldado eliminado: {soldados_eliminados/len(sim_rapidas)*100:.1f}%")
        print(f"  Granada usada: {granadas_usadas/len(sim_rapidas)*100:.1f}%")
        
        # Distribución de pasos
        print(f"\nDISTRIBUCIÓN DE PASOS (simulaciones rápidas):")
        rangos = [(0, 50), (51, 100), (101, 150), (151, 200)]
        for rango_min, rango_max in rangos:
            en_rango = sum(1 for r in sim_rapidas if rango_min <= r['pasos'] <= rango_max)
            print(f"  {rango_min}-{rango_max} pasos: {en_rango} ({en_rango/len(sim_rapidas)*100:.1f}%)")
        
        # Análisis de correlación éxito/exploración
        print(f"\nANÁLISIS DE CORRELACIÓN:")
        if exitos > 0:
            pasos_exitos = [r['pasos'] for r in sim_rapidas if r['exito']]
            exploracion_exitos = [r['celdas_exploradas'] for r in sim_rapidas if r['exito']]
            
            print(f"  En simulaciones exitosas:")
            print(f"    - Pasos promedio: {sum(pasos_exitos)/len(pasos_exitos):.1f}")
            print(f"    - Exploración promedio: {sum(exploracion_exitos)/len(exploracion_exitos):.1f} celdas")
        
        # Comparativa con simulación detallada
        print(f"\nCOMPARATIVA CON SIMULACIÓN DETALLADA:")
        if sim_detallada['exito']:
            print("   La simulación detallada fue exitosa")
            if exitos/len(sim_rapidas) > 0.7:
                print("   Comportamiento consistente con las simulaciones rápidas")
            else:
                print("    La simulación detallada tuvo mejor desempeño que el promedio")
        else:
            print("   La simulación detallada fracasó")
            if exitos/len(sim_rapidas) < 0.3:
                print("    Comportamiento consistente (dificultad alta con este umbral)")
            else:
                print("    La simulación detallada tuvo peor desempeño que el promedio")
    
    print("\n" + "="*60)
    
    # Opción para guardar resultados
    guardar = input("\n¿Guardar resultados estadísticos en un archivo? (s/n): ").strip().lower()
    if guardar == 's':
        guardar_resultados_estadisticos(resultados, umbral)

def guardar_resultados_estadisticos(resultados, umbral):
    """
    Guarda los resultados estadísticos en un archivo
    """
    import csv
    from datetime import datetime
    
    # Crear nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"estadisticas_bayesianas_{timestamp}.csv"
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['simulacion', 'tipo', 'exito', 'pasos', 'kurtz_encontrado', 
                     'soldado_eliminado', 'granada_usada', 'celdas_exploradas',
                     'motivo_fin', 'umbral_riesgo', 'porcentaje_exploracion']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, resultado in enumerate(resultados):
            porcentaje_exploracion = (resultado['celdas_exploradas'] / resultado['celdas_totales']) * 100
            
            row = {
                'simulacion': i + 1,
                'tipo': 'detallada' if i == 0 else 'rapida',
                'exito': resultado['exito'],
                'pasos': resultado['pasos'],
                'kurtz_encontrado': resultado['kurtz_encontrado'],
                'soldado_eliminado': resultado['soldado_eliminado'],
                'granada_usada': resultado['granada_usada'],
                'celdas_exploradas': resultado['celdas_exploradas'],
                'motivo_fin': resultado['motivo_fin'],
                'umbral_riesgo': resultado['umbral_riesgo'],
                'porcentaje_exploracion': round(porcentaje_exploracion, 2)
            }
            writer.writerow(row)
    
    # Crear archivo de resumen
    crear_resumen_estadistico(resultados, umbral, filename.replace('.csv', '_resumen.txt'))
    
    print(f"\nResultados guardados en {filename}")
    print(f"Resumen guardado en {filename.replace('.csv', '_resumen.txt')}")

def crear_resumen_estadistico(resultados, umbral, filename):
    """
    Crea un archivo de resumen con las estadísticas principales
    """
    with open(filename, 'w') as f:
        f.write("="*60 + "\n")
        f.write("RESUMEN ESTADÍSTICO - AGENTE BAYESIANO\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Umbral de riesgo: {umbral}\n")
        f.write(f"Total de simulaciones: {len(resultados)}\n")
        f.write(f"  • Simulación detallada: 1\n")
        f.write(f"  • Simulaciones rápidas: {len(resultados)-1}\n\n")
        
        # Estadísticas básicas
        exitos = sum(1 for r in resultados if r['exito'])
        f.write(f"Tasa de éxito global: {exitos}/{len(resultados)} ({exitos/len(resultados)*100:.1f}%)\n\n")
        
        # Separar tipos de simulaciones
        detallada = resultados[0]
        rapidas = resultados[1:] if len(resultados) > 1 else []
        
        f.write("SIMULACIÓN DETALLADA:\n")
        f.write(f"  Resultado: {'ÉXITO' if detallada['exito'] else 'FRACASO'}\n")
        f.write(f"  Pasos: {detallada['pasos']}\n")
        f.write(f"  Kurtz encontrado: {'SÍ' if detallada['kurtz_encontrado'] else 'NO'}\n")
        f.write(f"  Exploración: {detallada['celdas_exploradas']}/{detallada['celdas_totales']} celdas\n\n")
        
        if rapidas:
            f.write(f"ESTADÍSTICAS DE {len(rapidas)} SIMULACIONES RÁPIDAS:\n")
            
            exitos_rapidas = sum(1 for r in rapidas if r['exito'])
            f.write(f"  Tasa de éxito: {exitos_rapidas}/{len(rapidas)} ({exitos_rapidas/len(rapidas)*100:.1f}%)\n")
            
            pasos_promedio = sum(r['pasos'] for r in rapidas) / len(rapidas)
            f.write(f"  Pasos promedio: {pasos_promedio:.1f}\n")
            
            exploracion_promedio = sum(r['celdas_exploradas'] for r in rapidas) / len(rapidas)
            porcentaje_exploracion = (exploracion_promedio / rapidas[0]['celdas_totales']) * 100
            f.write(f"  Exploración promedio: {exploracion_promedio:.1f} celdas ({porcentaje_exploracion:.1f}%)\n\n")
            
            # Razones de fracaso
            razones = {}
            for r in rapidas:
                if not r['exito']:
                    razon = r['motivo_fin']
                    razones[razon] = razones.get(razon, 0) + 1
            
            if razones:
                f.write("RAZONES DE FRACASO:\n")
                for razon, cuenta in razones.items():
                    f.write(f"  • {razon}: {cuenta} veces\n")
        
        f.write("\n" + "="*60 + "\n")
        f.write("FIN DEL RESUMEN\n")
        f.write("="*60 + "\n")

if __name__ == "__main__":
    modo_bayesiano()