#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXAMEN: Juego de código Morse
Ejercicios:
- Generar número aleatorio (10-15) -> letra hex A-F
- Mostrar en LEDs GPIO20-23 (MSB a LSB)
- Jugador introduce Morse con GPIO16 (punto) y GPIO17 (raya)
- Validar con GPIO19
- Contador de fallos en GPIO26-27 (satura en 3)
- Añadir tiempo máximo entre pulsaciones (4s)
- Atenuación progresiva de LEDs cada segundo (75%, 50%, 25%)
- Añadir LDRs para punto y raya analógicos
"""

import time
import random
from gpiozero import LED, Button, LEDBoard, PWMLED, MCP3008

# ============================================================
# PARTE 1: Versión básica (3 puntos)
# ============================================================

def morse_basico():
    """
    Tabla Morse:
    A (10): .-      (punto, raya)
    B (11): -...    (raya, punto, punto, punto)
    C (12): -.-.    (raya, punto, raya, punto)
    D (13): -..     (raya, punto, punto)
    E (14): .       (punto)
    F (15): ..-.    (punto, punto, raya, punto)
    """
    # Mapeo número -> secuencia Morse
    # Usamos 1 para punto, 2 para raya (para facilitar)
    MORSE = {
        10: [1, 2],           # A: .-
        11: [2, 1, 1, 1],     # B: -...
        12: [2, 1, 2, 1],     # C: -.-.
        13: [2, 1, 1],        # D: -..
        14: [1],              # E: .
        15: [1, 1, 2, 1]      # F: ..-.
    }
    
    # LEDs
    numero_leds = LEDBoard(20, 21, 22, 23)  # Muestran el número
    fallos_leds = LEDBoard(26, 27)          # Muestran contador fallos (2 bits)
    
    # Botones
    boton_punto = Button(16)   # GPIO16 para punto
    boton_raya = Button(17)    # GPIO17 para raya
    boton_validar = Button(19)  # GPIO19 para validar
    
    # Variables de juego
    numero_actual = 0
    secuencia_correcta = []
    secuencia_introducida = []
    contador_fallos = 0
    
    # Detección de flanco
    ant_punto = boton_punto.is_pressed
    ant_raya = boton_raya.is_pressed
    ant_validar = boton_validar.is_pressed
    
    PERIODO_SCAN = 0.05
    
    def nuevo_numero():
        nonlocal numero_actual, secuencia_correcta, secuencia_introducida
        numero_actual = random.randint(10, 15)
        secuencia_correcta = MORSE[numero_actual]
        secuencia_introducida = []
        
        # Mostrar número en LEDs (GPIO20-23)
        # Números 10-15 caben en 4 bits
        bits_num = [(numero_actual >> i) & 1 for i in range(4)]
        # GPIO20 es LSB, pero queremos MSB primero? El enunciado dice GPIO20 es MSB
        # Así que invertimos
        bits_num.reverse()
        for i, led in enumerate(numero_leds):
            if bits_num[i]:
                led.on()
            else:
                led.off()
        
        # Actualizar LEDs de fallos
        actualizar_leds_fallos()
        
        print(f"Nuevo número: {numero_actual} (hex: {hex(numero_actual)[2].upper()})")
        print(f"Secuencia correcta: {secuencia_correcta}")
    
    def actualizar_leds_fallos():
        """Muestra contador de fallos (satura en 3)"""
        bits_fallos = [(contador_fallos >> i) & 1 for i in range(2)]
        for i, led in enumerate(fallos_leds):
            if bits_fallos[i]:
                led.on()
            else:
                led.off()
    
    def comprobar_respuesta():
        nonlocal contador_fallos, secuencia_introducida
        
        if secuencia_introducida == secuencia_correcta:
            print("¡CORRECTO!")
            contador_fallos = 0
            nuevo_numero()
        else:
            contador_fallos = min(contador_fallos + 1, 3)
            secuencia_introducida = []  # Reiniciar intento
            actualizar_leds_fallos()
            print(f"INCORRECTO - Fallos: {contador_fallos}")
    
    # Iniciar juego
    nuevo_numero()
    
    try:
        while True:
            inicio_ciclo = time.time()
            
            # Botón punto
            act_punto = boton_punto.is_pressed
            if ant_punto and not act_punto:
                secuencia_introducida.append(1)  # 1 = punto
                print(f"Punto - Secuencia: {secuencia_introducida}")
            ant_punto = act_punto
            
            # Botón raya
            act_raya = boton_raya.is_pressed
            if ant_raya and not act_raya:
                secuencia_introducida.append(2)  # 2 = raya
                print(f"Raya - Secuencia: {secuencia_introducida}")
            ant_raya = act_raya
            
            # Botón validar
            act_validar = boton_validar.is_pressed
            if ant_validar and not act_validar:
                comprobar_respuesta()
            ant_validar = act_validar
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        numero_leds.off()
        fallos_leds.off()

# ============================================================
# PARTE 2: Con tiempo máximo entre pulsaciones (4 puntos)
# ============================================================

def morse_tiempo():
    """
    Añade:
    - Máximo 4 segundos entre pulsaciones
    - Cada segundo, LEDs pierden 25% de intensidad
    - Usar PWMLED para atenuación
    """
    # Usamos PWMLED para poder atenuar
    numero_leds = [PWMLED(20), PWMLED(21), PWMLED(22), PWMLED(23)]
    fallos_leds = LEDBoard(26, 27)  # Estos siguen siendo digitales
    
    boton_punto = Button(16)
    boton_raya = Button(17)
    boton_validar = Button(19)
    
    MORSE = {
        10: [1, 2],
        11: [2, 1, 1, 1],
        12: [2, 1, 2, 1],
        13: [2, 1, 1],
        14: [1],
        15: [1, 1, 2, 1]
    }
    
    numero_actual = 0
    secuencia_correcta = []
    secuencia_introducida = []
    contador_fallos = 0
    
    # Variables para tiempo entre pulsaciones
    tiempo_ultima_pulsacion = time.time()
    TIEMPO_MAXIMO = 4  # segundos
    
    # Para atenuación progresiva
    intensidad_actual = 1.0  # 100%
    
    ant_punto = boton_punto.is_pressed
    ant_raya = boton_raya.is_pressed
    ant_validar = boton_validar.is_pressed
    
    PERIODO_SCAN = 0.05
    
    def nuevo_numero():
        nonlocal numero_actual, secuencia_correcta, secuencia_introducida
        nonlocal tiempo_ultima_pulsacion, intensidad_actual
        
        numero_actual = random.randint(10, 15)
        secuencia_correcta = MORSE[numero_actual]
        secuencia_introducida = []
        
        # Mostrar número con intensidad 100%
        intensidad_actual = 1.0
        actualizar_leds_numero()
        
        tiempo_ultima_pulsacion = time.time()
        
        actualizar_leds_fallos()
        
        print(f"Nuevo número: {numero_actual}")
    
    def actualizar_leds_numero():
        """Actualiza LEDs con la intensidad actual"""
        bits_num = [(numero_actual >> i) & 1 for i in range(4)]
        bits_num.reverse()  # GPIO20 es MSB
        for i, led in enumerate(numero_leds):
            if bits_num[i]:
                led.value = intensidad_actual
            else:
                led.value = 0
    
    def actualizar_leds_fallos():
        bits_fallos = [(contador_fallos >> i) & 1 for i in range(2)]
        for i, led in enumerate(fallos_leds):
            if bits_fallos[i]:
                led.on()
            else:
                led.off()
    
    def comprobar_respuesta():
        nonlocal contador_fallos, secuencia_introducida, intensidad_actual
        
        if secuencia_introducida == secuencia_correcta:
            print("¡CORRECTO!")
            contador_fallos = 0
            nuevo_numero()
        else:
            contador_fallos = min(contador_fallos + 1, 3)
            secuencia_introducida = []
            intensidad_actual = 1.0  # Reiniciar intensidad
            actualizar_leds_numero()
            actualizar_leds_fallos()
            tiempo_ultima_pulsacion = time.time()
            print(f"INCORRECTO - Fallos: {contador_fallos}")
    
    nuevo_numero()
    
    try:
        while True:
            inicio_ciclo = time.time()
            tiempo_actual = time.time()
            
            # Calcular tiempo desde última pulsación
            tiempo_sin_pulsar = tiempo_actual - tiempo_ultima_pulsacion
            
            # Atenuación progresiva (cada segundo, 25% menos)
            if tiempo_sin_pulsar >= 1.0 and tiempo_sin_pulsar < 2.0:
                intensidad_actual = 0.75
            elif tiempo_sin_pulsar >= 2.0 and tiempo_sin_pulsar < 3.0:
                intensidad_actual = 0.50
            elif tiempo_sin_pulsar >= 3.0 and tiempo_sin_pulsar < 4.0:
                intensidad_actual = 0.25
            elif tiempo_sin_pulsar >= 4.0:
                intensidad_actual = 0.0
            
            actualizar_leds_numero()
            
            # Comprobar si se superó el tiempo máximo
            if tiempo_sin_pulsar > TIEMPO_MAXIMO and len(secuencia_introducida) > 0:
                print("Tiempo máximo superado - FALLO")
                contador_fallos = min(contador_fallos + 1, 3)
                secuencia_introducida = []
                intensidad_actual = 1.0
                actualizar_leds_numero()
                actualizar_leds_fallos()
                tiempo_ultima_pulsacion = tiempo_actual
            
            # Botón punto
            act_punto = boton_punto.is_pressed
            if ant_punto and not act_punto:
                secuencia_introducida.append(1)
                print(f"Punto - Secuencia: {secuencia_introducida}")
                tiempo_ultima_pulsacion = tiempo_actual
                intensidad_actual = 1.0
                actualizar_leds_numero()
            ant_punto = act_punto
            
            # Botón raya
            act_raya = boton_raya.is_pressed
            if ant_raya and not act_raya:
                secuencia_introducida.append(2)
                print(f"Raya - Secuencia: {secuencia_introducida}")
                tiempo_ultima_pulsacion = tiempo_actual
                intensidad_actual = 1.0
                actualizar_leds_numero()
            ant_raya = act_raya
            
            # Botón validar
            act_validar = boton_validar.is_pressed
            if ant_validar and not act_validar:
                comprobar_respuesta()
            ant_validar = act_validar
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        for led in numero_leds:
            led.off()
        fallos_leds.off()

# ============================================================
# PARTE 3: Con LDRs analógicos (3 puntos)
# ============================================================

def morse_ldr():
    """
    Añade dos LDRs para punto y raya:
    - LDR1 (CH0) -> detecta punto
    - LDR2 (CH1) -> detecta raya
    - Al tapar, se registra el símbolo
    - Los pulsadores siguen funcionando
    """
    numero_leds = LEDBoard(20, 21, 22, 23)
    fallos_leds = LEDBoard(26, 27)
    
    # Pulsadores digitales
    boton_punto = Button(16)
    boton_raya = Button(17)
    boton_validar = Button(19)
    
    # LDRs analógicos
    ldr_punto = MCP3008(channel=0)  # Para punto
    ldr_raya = MCP3008(channel=1)   # Para raya
    
    MORSE = {
        10: [1, 2],
        11: [2, 1, 1, 1],
        12: [2, 1, 2, 1],
        13: [2, 1, 1],
        14: [1],
        15: [1, 1, 2, 1]
    }
    
    numero_actual = 0
    secuencia_correcta = []
    secuencia_introducida = []
    contador_fallos = 0
    
    # Estados para detectar cambio en LDRs
    ldr_punto_cubierto = False
    ldr_raya_cubierto = False
    
    ant_punto = boton_punto.is_pressed
    ant_raya = boton_raya.is_pressed
    ant_validar = boton_validar.is_pressed
    
    PERIODO_SCAN = 0.05
    UMBRAL_LDR = 1.0  # Voltios: por debajo = tapado (ajustar)
    
    def nuevo_numero():
        nonlocal numero_actual, secuencia_correcta, secuencia_introducida
        
        numero_actual = random.randint(10, 15)
        secuencia_correcta = MORSE[numero_actual]
        secuencia_introducida = []
        
        bits_num = [(numero_actual >> i) & 1 for i in range(4)]
        bits_num.reverse()
        for i, led in enumerate(numero_leds):
            if bits_num[i]:
                led.on()
            else:
                led.off()
        
        actualizar_leds_fallos()
        
        print(f"Nuevo número: {numero_actual}")
    
    def actualizar_leds_fallos():
        bits_fallos = [(contador_fallos >> i) & 1 for i in range(2)]
        for i, led in enumerate(fallos_leds):
            if bits_fallos[i]:
                led.on()
            else:
                led.off()
    
    def comprobar_respuesta():
        nonlocal contador_fallos, secuencia_introducida
        
        if secuencia_introducida == secuencia_correcta:
            print("¡CORRECTO!")
            contador_fallos = 0
            nuevo_numero()
        else:
            contador_fallos = min(contador_fallos + 1, 3)
            secuencia_introducida = []
            actualizar_leds_fallos()
            print(f"INCORRECTO - Fallos: {contador_fallos}")
    
    nuevo_numero()
    
    try:
        while True:
            inicio_ciclo = time.time()
            
            # Leer LDRs
            valor_punto = ldr_punto.voltage
            valor_raya = ldr_raya.voltage
            
            punto_actual = (valor_punto < UMBRAL_LDR)
            raya_actual = (valor_raya < UMBRAL_LDR)
            
            # Detectar flanco en LDR punto (cuando se tapa)
            if not ldr_punto_cubierto and punto_actual:
                print("LDR Punto tapado")
                secuencia_introducida.append(1)
                print(f"Secuencia: {secuencia_introducida}")
            
            # Detectar flanco en LDR raya
            if not ldr_raya_cubierto and raya_actual:
                print("LDR Raya tapado")
                secuencia_introducida.append(2)
                print(f"Secuencia: {secuencia_introducida}")
            
            ldr_punto_cubierto = punto_actual
            ldr_raya_cubierto = raya_actual
            
            # Botón punto digital
            act_punto = boton_punto.is_pressed
            if ant_punto and not act_punto:
                secuencia_introducida.append(1)
                print(f"Punto digital - Secuencia: {secuencia_introducida}")
            ant_punto = act_punto
            
            # Botón raya digital
            act_raya = boton_raya.is_pressed
            if ant_raya and not act_raya:
                secuencia_introducida.append(2)
                print(f"Raya digital - Secuencia: {secuencia_introducida}")
            ant_raya = act_raya
            
            # Botón validar
            act_validar = boton_validar.is_pressed
            if ant_validar and not act_validar:
                comprobar_respuesta()
            ant_validar = act_validar
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        numero_leds.off()
        fallos_leds.off()

if __name__ == "__main__":
    # Elegir versión
    # morse_basico()
    # morse_tiempo()
    morse_ldr()