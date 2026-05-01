"""
Parte 2 - Cruzar el Río: MDP y Value Iteration
Implementación del proceso de decisión de Markov para cruzar el río

Este archivo implementa:
1. Modelado del río como Proceso de Decisión de Markov (MDP)
2. Algoritmo Value Iteration para calcular política óptima
3. Simulación de trayectorias siguiendo la política
4. Análisis estadístico de resultados
"""

import numpy as np
import random
import time
from funciones_comunes import *

# ============================================================================
# CLASE RÍO MDP
# ============================================================================

class RioMDP:
    """
    Modela el problema de cruzar el río como un MDP (Proceso de Decisión de Markov)
    
    Componentes del MDP:
    - Estados: Posiciones (i,j) en la cuadrícula del río
    - Acciones: 'up', 'down', 'left', 'right', 'stay'
    - Transiciones: Probabilísticas (dependen de corriente y obstáculos)
    - Recompensas: +100 por salida, -100 por trampa, -1 por movimiento
    - Factor de descuento (gamma): 0.9
    
    Características especiales:
    - Corriente variable por columna (empuja hacia abajo)
    - Islas como obstáculos infranqueables
    - Transiciones no deterministas por efecto de la corriente
    """
    
    def __init__(self, filas=6, columnas=8, num_islas=2):
        """
        Inicializa el entorno del río MDP
        
        Args:
            filas: Número de filas de la cuadrícula
            columnas: Número de columnas de la cuadrícula
            num_islas: Número de islas/peligros en el río
        """
        self.filas = filas
        self.columnas = columnas
        self.num_islas = num_islas
        
        # Inicializar la cuadrícula del río con islas aleatorias
        self.river = self.inicializar_rio()
        
        # Calcular fuerza de corriente para cada columna
        self.corriente = self.calcular_corrientes()
        
        # Posiciones fijas (configuración estándar)
        self.pos_inicial = (0, 0)            # Esquina superior izquierda
        self.pos_salida = (filas-1, columnas-1)  # Esquina inferior derecha
        self.pos_actual = self.pos_inicial   # Posición actual del agente
        
        # Sistema de recompensas
        self.recompensa_salida = 100     # Llegar a la salida
        self.recompensa_trampa = -100    # Caer en isla/peligro
        self.recompensa_movimiento = -1  # Costo por cada movimiento
        
        # Parámetros del algoritmo Value Iteration
        self.gamma = 0.9      # Factor de descuento (futuro vs presente)
        self.epsilon = 1e-6   # Criterio de convergencia
        
        # Resultados del algoritmo
        self.valores = None   # V*(s) - valores óptimos de cada estado
        self.politica = None  # π*(s) - política óptima para cada estado
        
        print(f"Río MDP inicializado: {filas}x{columnas} con {num_islas} islas")
    
    def inicializar_rio(self):
        """
        Crea la cuadrícula del río con islas colocadas aleatoriamente
        
        Reglas para colocación de islas:
        - No pueden estar en la primera fila (entrada)
        - No pueden estar en la última fila (salida)
        - No pueden superponerse
        
        Returns:
            numpy.ndarray: Matriz donde 0 = río seguro, 1 = isla/peligro
        """
        # Crear matriz de ceros (todas celdas son río seguro inicialmente)
        river = np.zeros((self.filas, self.columnas), dtype=int)
        
        # Colocar islas aleatoriamente respetando restricciones
        islas_generadas = 0
        intentos = 0
        max_intentos = 100  # Evitar bucle infinito
        
        while islas_generadas < self.num_islas and intentos < max_intentos:
            # Generar posición aleatoria (evitando primera y última fila)
            fila = random.randint(1, self.filas - 2)  # Rango: 1 a filas-2
            columna = random.randint(0, self.columnas - 1)
            
            # Verificar que la posición está libre
            if river[fila][columna] == 0:
                river[fila][columna] = 1  # Marcar como isla
                islas_generadas += 1
            
            intentos += 1
        
        # Advertencia si no se pudieron colocar todas las islas
        if islas_generadas < self.num_islas:
            print(f"Advertencia: Solo se pudieron colocar {islas_generadas} de {self.num_islas} islas")
        
        return river
    
    def calcular_corrientes(self):
        """
        Calcula la fuerza de la corriente para cada columna del río
        
        Reglas:
        - Columnas de los bordes (primera y última): corriente = 0
        - Columnas interiores: corriente aleatoria entre 0.06 y 0.94
        
        Returns:
            list: Lista de fuerzas de corriente por columna
        """
        corrientes = []
        
        for j in range(self.columnas):
            if j == 0 or j == self.columnas - 1:
                # Bordes: sin corriente (orillas)
                corrientes.append(0.0)
            else:
                # Interiores: corriente aleatoria uniforme
                fuerza = round(random.uniform(0.06, 0.94), 2)
                corrientes.append(fuerza)
        
        return corrientes
    
    def es_valida(self, pos):
        """
        Verifica si una posición es válida (transitable)
        
        Una posición es válida si:
        1. Está dentro de los límites de la cuadrícula
        2. No es una isla (valor 1 en matriz river)
        
        Args:
            pos: Tupla (fila, columna)
            
        Returns:
            bool: True si es válida, False en caso contrario
        """
        fila, col = pos
        
        # Verificar límites
        if not (0 <= fila < self.filas and 0 <= col < self.columnas):
            return False
        
        # Verificar que no sea isla
        if self.river[fila][col] == 1:
            return False
        
        return True
    
    def transicion(self, estado, accion):
        """
        Modelo de transición del MDP
        
        Calcula las probabilidades de transición desde un estado al ejecutar una acción
        Considera:
        - Movimiento deseado (acción del agente)
        - Empuje de la corriente (siempre hacia abajo excepto acción 'down')
        - Colisiones con bordes e islas
        
        Args:
            estado: Estado actual (fila, columna)
            accion: Acción a ejecutar ('up', 'down', 'left', 'right', 'stay')
            
        Returns:
            list: Lista de tuplas (probabilidad, nuevo_estado, recompensa, terminado)
        """
        fila, col = estado
        transiciones = []
        
        # Mapeo de acciones a desplazamientos
        acciones_dict = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1),
            'stay': (0, 0)
        }
        
        if accion not in acciones_dict:
            return transiciones  # Acción no reconocida
        
        # 1. Calcular estado deseado (según acción del agente)
        df, dc = acciones_dict[accion]
        nuevo_estado_deseado = (fila + df, col + dc)
        
        # Si el movimiento deseado no es válido, quedarse en el mismo lugar
        if not self.es_valida(nuevo_estado_deseado):
            nuevo_estado_deseado = estado
        
        # 2. Calcular efecto de la corriente (siempre empuja hacia abajo)
        if accion != 'down':
            # La corriente empuja hacia abajo cuando no es la acción 'down'
            nuevo_estado_corriente = (fila + 1, col)
            if not self.es_valida(nuevo_estado_corriente):
                nuevo_estado_corriente = estado
        else:
            # Si acción es 'down', no hay empuje adicional de corriente
            nuevo_estado_corriente = estado
        
        # 3. Calcular probabilidades según fórmula del enunciado
        p_dir = 1.0 - self.corriente[col]  # Probabilidad de movimiento deseado
        p_down = self.corriente[col]       # Probabilidad de empuje por corriente
        
        if accion != 'down':
            # Caso general: dos posibles transiciones
            
            # Transición 1: Movimiento en dirección deseada
            recompensa1 = self.calcular_recompensa(estado, nuevo_estado_deseado)
            terminado1 = self.es_estado_terminal(nuevo_estado_deseado)
            transiciones.append((p_dir, nuevo_estado_deseado, recompensa1, terminado1))
            
            # Transición 2: Empujado por la corriente
            if p_down > 0:
                recompensa2 = self.calcular_recompensa(estado, nuevo_estado_corriente)
                terminado2 = self.es_estado_terminal(nuevo_estado_corriente)
                transiciones.append((p_down, nuevo_estado_corriente, recompensa2, terminado2))
        else:
            # Acción 'down': solo movimiento deseado (100% probabilidad)
            recompensa = self.calcular_recompensa(estado, nuevo_estado_deseado)
            terminado = self.es_estado_terminal(nuevo_estado_deseado)
            transiciones.append((1.0, nuevo_estado_deseado, recompensa, terminado))
        
        return transiciones
    
    def calcular_recompensa(self, estado_actual, estado_siguiente):
        """
        Calcula la recompensa por una transición
        
        Sistema de recompensas:
        - +100: llegar a la salida
        - -100: caer en isla/peligro
        - -1: cualquier otro movimiento (costo por paso)
        
        Args:
            estado_actual: Estado de origen
            estado_siguiente: Estado de destino
            
        Returns:
            float: Recompensa de la transición
        """
        # Recompensa por llegar a la salida
        if estado_siguiente == self.pos_salida:
            return self.recompensa_salida
        
        # Penalización por caer en trampa (isla)
        if not self.es_valida(estado_siguiente):
            return self.recompensa_trampa
        
        # Costo por movimiento (incentiva caminos cortos)
        return self.recompensa_movimiento
    
    def es_estado_terminal(self, estado):
        """
        Determina si un estado es terminal
        
        Estados terminales:
        1. Estado de salida (victoria)
        2. Estado no válido (isla o fuera de límites - derrota)
        
        Args:
            estado: Estado a verificar
            
        Returns:
            bool: True si es terminal, False en caso contrario
        """
        # Victoria: llegar a la salida
        if estado == self.pos_salida:
            return True
        
        # Derrota: estado no válido (isla o fuera de límites)
        if not self.es_valida(estado):
            return True
        
        return False  # Estado no terminal
    
    def value_iteration(self, max_iteraciones=1000):
        """
        Implementa el algoritmo Value Iteration para resolver el MDP
        
        Algoritmo:
        1. Inicializar V(s) = 0 para todos los estados
        2. Repetir hasta convergencia:
           Para cada estado s:
             V(s) = max_a Σ_s' P(s'|s,a)[R(s,a,s') + γV(s')]
        3. Extraer política óptima: π*(s) = argmax_a Q(s,a)
        
        Args:
            max_iteraciones: Límite de iteraciones para evitar bucles infinitos
        """
        print("\nCalculando política óptima con Value Iteration...")
        
        # PASO 1: Inicializar valores a 0 para todos los estados
        self.valores = np.zeros((self.filas, self.columnas))
        
        # Listar todos los estados válidos (no terminales)
        estados = []
        for i in range(self.filas):
            for j in range(self.columnas):
                if self.es_valida((i, j)):
                    estados.append((i, j))
        
        # PASO 2: Iterar hasta convergencia
        for iteracion in range(max_iteraciones):
            delta = 0  # Cambio máximo en esta iteración
            nuevo_valores = self.valores.copy()  # Copia para actualización sincronizada
            
            for estado in estados:
                # Estados terminales no se actualizan (valor fijo)
                if self.es_estado_terminal(estado):
                    continue
                
                # Calcular valor Q para cada acción posible
                mejor_valor = -float('inf')  # Inicializar con valor muy bajo
                
                for accion in ['up', 'down', 'left', 'right', 'stay']:
                    valor_accion = 0
                    transiciones = self.transicion(estado, accion)
                    
                    # Sumar sobre posibles estados siguientes
                    for prob, next_state, recompensa, terminado in transiciones:
                        if terminado:
                            # Estado terminal: valor futuro = 0
                            valor_futuro = 0
                        else:
                            # Estado no terminal: usar valor actual estimado
                            valor_futuro = self.valores[next_state]
                        
                        # Ecuación de Bellman:
                        # Q(s,a) = Σ P(s'|s,a)[R + γV(s')]
                        valor_accion += prob * (recompensa + self.gamma * valor_futuro)
                    
                    # Mantener el mejor valor encontrado
                    if valor_accion > mejor_valor:
                        mejor_valor = valor_accion
                
                # Actualizar valor del estado con el mejor encontrado
                nuevo_valores[estado] = mejor_valor
                delta = max(delta, abs(mejor_valor - self.valores[estado]))
            
            # Actualizar valores para la siguiente iteración
            self.valores = nuevo_valores
            
            # Verificar criterio de convergencia
            if delta < self.epsilon:
                print(f"Convergencia alcanzada en iteración {iteracion + 1}")
                break
        
        # PASO 3: Calcular política óptima basada en valores óptimos
        self.calcular_politica()
        
        print("Value Iteration completado")
    
    def calcular_politica(self):
        """
        Calcula la política óptima π*(s) basada en los valores V*(s)
        
        Para cada estado s:
        π*(s) = argmax_a Σ_s' P(s'|s,a)[R(s,a,s') + γV*(s')]
        """
        self.politica = {}  # Diccionario estado -> mejor acción
        
        # Para cada estado válido no terminal
        for i in range(self.filas):
            for j in range(self.columnas):
                estado = (i, j)
                
                # Saltar estados no válidos o terminales
                if not self.es_valida(estado) or self.es_estado_terminal(estado):
                    continue
                
                # Encontrar acción que maximiza el valor esperado
                mejor_accion = None
                mejor_valor = -float('inf')
                
                for accion in ['up', 'down', 'left', 'right', 'stay']:
                    valor_accion = 0
                    transiciones = self.transicion(estado, accion)
                    
                    for prob, next_state, recompensa, terminado in transiciones:
                        if terminado:
                            valor_futuro = 0
                        else:
                            valor_futuro = self.valores[next_state]
                        
                        valor_accion += prob * (recompensa + self.gamma * valor_futuro)
                    
                    # Actualizar mejor acción si encontramos valor mayor
                    if valor_accion > mejor_valor:
                        mejor_valor = valor_accion
                        mejor_accion = accion
                
                # Guardar política óptima para este estado
                self.politica[estado] = mejor_accion
    
    def seguir_politica(self, estado):
        """
        Devuelve la acción recomendada por la política óptima para un estado
        
        Args:
            estado: Estado actual (fila, columna)
            
        Returns:
            str: Acción óptima según la política calculada
        """
        return self.politica.get(estado, 'stay')  # Default: quedarse
    
    def simular_trayectoria(self, max_pasos=50):
        """
        Simula una trayectoria siguiendo la política óptima
        
        Args:
            max_pasos: Máximo número de pasos antes de abortar
            
        Returns:
            tuple: (trayectoria, recompensa_total)
            - trayectoria: Lista de estados visitados
            - recompensa_total: Suma de recompensas obtenidas
        """
        print("\n" + "="*60)
        print("SIMULACIÓN DE TRAYECTORIA ÓPTIMA")
        print("="*60)
        
        estado = self.pos_inicial
        trayectoria = [estado]  # Lista para registrar el camino
        recompensa_total = 0
        terminado = False
        
        print(f"Estado inicial: {estado}")
        print(f"Salida: {self.pos_salida}")
        print("\nIniciando simulación...\n")
        
        # Bucle principal de simulación
        for paso in range(1, max_pasos + 1):
            if terminado:
                break
            
            # 1. Obtener acción según política óptima
            accion = self.seguir_politica(estado)
            
            # 2. Obtener posibles transiciones para esta acción
            transiciones = self.transicion(estado, accion)
            
            if not transiciones:
                print(f"Paso {paso}: Sin transiciones válidas desde {estado}")
                break
            
            # 3. Seleccionar transición aleatoria según probabilidades
            probs = [t[0] for t in transiciones]
            idx = random.choices(range(len(transiciones)), weights=probs)[0]
            prob, next_state, recompensa, terminado = transiciones[idx]
            
            # 4. Actualizar estado y registros
            estado = next_state
            trayectoria.append(estado)
            recompensa_total += recompensa
            
            # 5. Mostrar información del paso
            print(f"Paso {paso}:")
            print(f"  Estado: {trayectoria[-2]} -> Acción: {accion} -> Estado: {estado}")
            print(f"  Recompensa: {recompensa} (Total: {recompensa_total})")
            
            if terminado:
                if estado == self.pos_salida:
                    print(f"  ¡LLEGÓ A LA SALIDA!")
                else:
                    print(f"  ¡CAYÓ EN UNA TRAMPA!")
            
            # Pausa breve para legibilidad
            time.sleep(0.3)
        
        # Mostrar resultados finales de la simulación
        print("\n" + "="*60)
        print("RESULTADO DE LA SIMULACIÓN")
        print("="*60)
        print(f"Pasos totales: {len(trayectoria)-1}")
        print(f"Recompensa total: {recompensa_total}")
        print(f"Estado final: {estado}")
        print(f"¿Llegó a salida?: {'SÍ' if estado == self.pos_salida else 'NO'}")
        print(f"Trayectoria: {trayectoria}")
        
        return trayectoria, recompensa_total
    
    def mostrar_rio(self, trayectoria=None):
        """
        Muestra una representación visual del río
        
        Args:
            trayectoria: Lista de estados visitados (opcional, para mostrar camino)
        """
        print("\n" + "="*60)
        print("REPRESENTACIÓN DEL RÍO")
        print("="*60)
        
        # Dibujar cada fila del río
        for i in range(self.filas):
            fila_str = ""
            for j in range(self.columnas):
                pos = (i, j)
                
                # Determinar símbolo según contenido de la celda
                if trayectoria and pos in trayectoria:
                    # Celda en el camino recorrido
                    if pos == trayectoria[0]:
                        fila_str += "[CK]"  # Inicio (Capitán con Kurtz)
                    elif pos == trayectoria[-1]:
                        fila_str += "[F]"   # Final
                    else:
                        fila_str += "[*] "  # Camino intermedio
                elif pos == self.pos_salida:
                    fila_str += "[E] "     # Salida
                elif self.river[i][j] == 1:
                    fila_str += "[I] "     # Isla/peligro
                else:
                    fila_str += "[R] "     # Río seguro
            
            print(f"Fila {i+1}: {fila_str}")
        
        # Mostrar información de corrientes
        print("\nFuerza de la corriente por columna:")
        for j, fuerza in enumerate(self.corriente):
            print(f"  Col {j+1}: {fuerza:.2f}")
        
        print("="*60)
    
    def mostrar_valores_politica(self):
        """
        Muestra los valores óptimos y política calculados
        
        Muestra:
        1. Valores V*(s) para cada estado
        2. Política óptima π*(s) con símbolos direccionales
        """
        print("\n" + "="*60)
        print("VALORES Y POLÍTICA ÓPTIMA")
        print("="*60)
        
        # 1. Mostrar valores de los estados
        print("\nValores de los estados (V*):")
        for i in range(self.filas):
            fila_str = ""
            for j in range(self.columnas):
                if self.es_valida((i, j)):
                    valor = self.valores[i][j]
                    fila_str += f"{valor:6.1f} "  # Formato: 6 caracteres, 1 decimal
                else:
                    fila_str += "   X   "  # Estado no válido
            print(f"Fila {i+1}: {fila_str}")
        
        # 2. Mostrar política óptima con símbolos direccionales
        print("\nPolítica óptima (π*):")
        simbolos_accion = {
            'up': '↑',
            'down': '↓',
            'left': '←',
            'right': '→',
            'stay': '•'
        }
        
        for i in range(self.filas):
            fila_str = ""
            for j in range(self.columnas):
                estado = (i, j)
                if self.es_valida(estado) and not self.es_estado_terminal(estado):
                    # Estado válido no terminal: mostrar acción óptima
                    accion = self.politica.get(estado, 'stay')
                    fila_str += f"  {simbolos_accion.get(accion, '?')}  "
                else:
                    # Estado terminal o no válido: mostrar símbolo especial
                    if estado == self.pos_salida:
                        fila_str += "  E  "  # Salida
                    elif self.river[i][j] == 1:
                        fila_str += "  I  "  # Isla
                    else:
                        fila_str += "     "  # Espacio vacío
            print(f"Fila {i+1}: {fila_str}")
        
        print("="*60)

# ============================================================================
# FUNCIÓN PRINCIPAL - MODO RÍO MDP
# ============================================================================

def modo_rio_mdp():
    """
    Función principal para ejecutar el modo Río MDP
    
    Flujo:
    1. Configurar parámetros del río
    2. Crear entorno MDP
    3. Ejecutar Value Iteration para calcular política óptima
    4. Mostrar resultados (valores y política)
    5. Simular trayectorias siguiendo la política
    6. Realizar análisis estadístico con múltiples simulaciones
    """
    print("\n" + ">"*30)
    print("MODO: CRUZAR EL RÍO (MDP)")
    print(">"*30)
    print("\nModelado como Proceso de Decisión de Markov")
    print("Objetivo: Llegar a la salida minimizando riesgo y pasos")
    print("-"*40)
    
    # 1. CONFIGURACIÓN DE PARÁMETROS
    print("\nConfiguración del río:")
    try:
        filas = int(input("Filas (default 6): ") or "6")
        columnas = int(input("Columnas (default 8): ") or "8")
        num_islas = int(input("Número de islas (default 2): ") or "2")
    except ValueError:
        print("Valores inválidos, usando valores por defecto")
        filas, columnas, num_islas = 6, 8, 2
    
    # 2. CREAR ENTORNO MDP
    rio = RioMDP(filas=filas, columnas=columnas, num_islas=num_islas)
    
    # Mostrar río inicial (sin trayectoria)
    rio.mostrar_rio()
    
    # 3. EJECUTAR VALUE ITERATION
    input("\nPresiona Enter para calcular política óptima con Value Iteration...")
    rio.value_iteration()
    
    # 4. MOSTRAR RESULTADOS DEL ALGORITMO
    rio.mostrar_valores_politica()
    
    # 5. SIMULAR TRAYECTORIA ÓPTIMA
    input("\nPresiona Enter para simular trayectoria óptima...")
    trayectoria, recompensa = rio.simular_trayectoria()
    
    # Mostrar río con la trayectoria simulada
    rio.mostrar_rio(trayectoria)
    
    # 6. ANÁLISIS ESTADÍSTICO CON MÚLTIPLES SIMULACIONES
    print("\n" + "="*60)
    print("ESTADÍSTICAS DE MÚLTIPLES SIMULACIONES")
    print("="*60)
    
    try:
        n_simulaciones = int(input("Número de simulaciones (default 10): ") or "10")
    except ValueError:
        n_simulaciones = 10
    
    # Variables para estadísticas
    exitos = 0           # Veces que llegó a la salida
    pasos_totales = 0    # Suma de pasos en todas las simulaciones
    recompensas_totales = 0  # Suma de recompensas
    
    print(f"\nEjecutando {n_simulaciones} simulaciones...")
    
    for sim in range(n_simulaciones):
        print(f"\nSimulación {sim + 1}:")
        
        # Configurar simulación individual
        estado = rio.pos_inicial
        pasos = 0
        terminado = False
        recompensa_sim = 0
        
        # Bucle de simulación individual
        while not terminado and pasos < 50:
            # Seguir política óptima
            accion = rio.seguir_politica(estado)
            transiciones = rio.transicion(estado, accion)
            
            if not transiciones:
                break
            
            # Seleccionar transición aleatoria según probabilidades
            probs = [t[0] for t in transiciones]
            idx = random.choices(range(len(transiciones)), weights=probs)[0]
            prob, next_state, recompensa, terminado = transiciones[idx]
            
            # Actualizar para siguiente iteración
            estado = next_state
            pasos += 1
            recompensa_sim += recompensa
        
        # Registrar resultados de esta simulación
        if estado == rio.pos_salida:
            exitos += 1
            print(f"  Éxito en {pasos} pasos (recompensa: {recompensa_sim})")
        else:
            print(f"  Fracaso en {pasos} pasos (recompensa: {recompensa_sim})")
        
        # Acumular estadísticas
        pasos_totales += pasos
        recompensas_totales += recompensa_sim
    
    # 7. MOSTRAR ESTADÍSTICAS FINALES
    print(f"\nResultados de {n_simulaciones} simulaciones:")
    print(f"  Tasa de éxito: {exitos/n_simulaciones*100:.1f}%")
    print(f"  Pasos promedio: {pasos_totales/n_simulaciones:.1f}")
    print(f"  Recompensa promedio: {recompensas_totales/n_simulaciones:.1f}")
    
    # Análisis adicional
    if exitos > 0:
        print(f"\nAnálisis de simulaciones exitosas:")
        print(f"  Porcentaje de éxitos: {exitos/n_simulaciones*100:.1f}%")
    else:
        print("\nAdvertencia: Ninguna simulación llegó a la salida")
        print("Posibles causas:")
        print("  - Corrientes muy fuertes")
        print("  - Demasiadas islas bloqueando el camino")
        print("  - Configuración inicial desfavorable")
    
    print("="*60)

if __name__ == "__main__":
    # Punto de entrada cuando se ejecuta este archivo directamente
    modo_rio_mdp()