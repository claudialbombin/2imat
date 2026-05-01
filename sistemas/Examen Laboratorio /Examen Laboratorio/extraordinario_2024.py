#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXAMEN: Luz de bicicleta - Máquina de estados
Ejercicio 1, 2 y 3 del examen extraordinario

ESTADOS: APAGADA -> PARPADEO_1HZ -> PARPADEO_2HZ -> APAGADA
- Botón: GPIO16
- LED: GPIO20
- Sensor luz: potenciómetro CH7 (0V=0lx, 3V=1500lx)
- Si luz < 1000lx: LED siempre encendido (no parpadea)
"""

import time
from gpiozero import Button, LED, MCP3008

# ============================================================
# PARTE 1: maquina_1.py - Solo transiciones (3 puntos)
# ============================================================

def maquina_1():
    """Solo imprime el estado por consola"""
    boton = Button(16)
    PERIODO_SCAN = 0.05  # 50 ms
    
    ESTADOS = ["APAGADA", "PARPADEO_1_HZ", "PARPADEO_2_HZ"]
    indice_estado = 0  # 0=APAGADA, 1=1Hz, 2=2Hz
    
    # Detección de flanco
    boton_anterior = boton.is_pressed
    
    print("Máquina de estados - Versión 1")
    print(f"Estado inicial: {ESTADOS[indice_estado]}")
    
    try:
        while True:
            inicio_ciclo = time.time()
            
            # Leer botón
            boton_actual = boton.is_pressed
            
            # Detectar flanco de bajada (pulsación)
            if boton_anterior and not boton_actual:
                # Transición de estado
                indice_estado = (indice_estado + 1) % 3
                print(f"Nuevo estado: {ESTADOS[indice_estado]}")
            
            boton_anterior = boton_actual
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")

# ============================================================
# PARTE 2: maquina_2.py - Con salida LED (4 puntos)
# ============================================================

def maquina_2():
    """Añade control del LED con parpadeo manual"""
    boton = Button(16)
    led = LED(20)
    PERIODO_SCAN = 0.05
    
    ESTADOS = ["APAGADA", "PARPADEO_1_HZ", "PARPADEO_2_HZ"]
    indice_estado = 0
    
    # Variables para parpadeo
    tiempo_ultimo_cambio = time.time()
    estado_led = False
    # Para 1Hz: medio período = 0.5s, para 2Hz: medio período = 0.25s
    MEDIO_PERIODO = [0, 0.5, 0.25]  # índice 0 no se usa
    
    # Detección de flanco
    boton_anterior = boton.is_pressed
    
    print("Máquina de estados - Versión 2")
    print(f"Estado inicial: {ESTADOS[indice_estado]}")
    
    try:
        while True:
            inicio_ciclo = time.time()
            tiempo_actual = time.time()
            
            # Leer botón
            boton_actual = boton.is_pressed
            
            # Detectar pulsación
            if boton_anterior and not boton_actual:
                indice_estado = (indice_estado + 1) % 3
                print(f"Nuevo estado: {ESTADOS[indice_estado]}")
                
                # Reiniciar parpadeo al cambiar de estado
                tiempo_ultimo_cambio = tiempo_actual
                estado_led = True  # Empezar encendido
                if indice_estado == 0:  # APAGADA
                    led.off()
            
            boton_anterior = boton_actual
            
            # Control del LED según estado
            if indice_estado == 0:  # APAGADA
                led.off()
                
            else:  # PARPADEO_1HZ o PARPADEO_2HZ
                medio_periodo = MEDIO_PERIODO[indice_estado]
                
                if tiempo_actual - tiempo_ultimo_cambio >= medio_periodo:
                    estado_led = not estado_led
                    tiempo_ultimo_cambio = tiempo_actual
                    
                    if estado_led:
                        led.on()
                    else:
                        led.off()
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        led.off()

# ============================================================
# PARTE 3: maquina_3.py - Con control día/noche (3 puntos)
# ============================================================

def maquina_3():
    """Añade sensor de luz (potenciómetro CH7)"""
    boton = Button(16)
    led = LED(20)
    sensor = MCP3008(channel=7)  # Potenciómetro
    PERIODO_SCAN = 0.05
    
    ESTADOS = ["APAGADA", "PARPADEO_1_HZ", "PARPADEO_2_HZ"]
    indice_estado = 0
    
    tiempo_ultimo_cambio = time.time()
    estado_led = False
    MEDIO_PERIODO = [0, 0.5, 0.25]
    
    boton_anterior = boton.is_pressed
    
    # Constantes para sensor de luz
    V_MAX = 3.0      # 3V = 1500 lx
    LUX_MAX = 1500
    UMBRAL_LUX = 1000
    
    print("Máquina de estados - Versión 3 (con control día/noche)")
    print(f"Estado inicial: {ESTADOS[indice_estado]}")
    
    try:
        while True:
            inicio_ciclo = time.time()
            tiempo_actual = time.time()
            
            # Leer sensor de luz
            voltios = sensor.voltage
            lux = (voltios / V_MAX) * LUX_MAX
            poca_luz = (lux < UMBRAL_LUX)
            
            # Leer botón
            boton_actual = boton.is_pressed
            
            # Detectar pulsación
            if boton_anterior and not boton_actual:
                indice_estado = (indice_estado + 1) % 3
                print(f"Nuevo estado: {ESTADOS[indice_estado]}")
                tiempo_ultimo_cambio = tiempo_actual
                estado_led = True
            
            boton_anterior = boton_actual
            
            # Control del LED con reglas día/noche
            if indice_estado == 0:  # APAGADA
                led.off()
                
            else:  # PARPADEO
                if poca_luz:
                    # Si hay poca luz, LED siempre encendido
                    led.on()
                else:
                    # Comportamiento normal de parpadeo
                    medio_periodo = MEDIO_PERIODO[indice_estado]
                    
                    if tiempo_actual - tiempo_ultimo_cambio >= medio_periodo:
                        estado_led = not estado_led
                        tiempo_ultimo_cambio = tiempo_actual
                        
                        if estado_led:
                            led.on()
                        else:
                            led.off()
            
            # Mostrar lux cada segundo
            if int(tiempo_actual) > int(tiempo_actual - 0.05):
                print(f"Luz: {lux:.0f} lx {'(POCA LUZ)' if poca_luz else ''}")
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        led.off()

if __name__ == "__main__":
    # Descomentar la versión que se quiera probar
    # maquina_1()
    # maquina_2()
    maquina_3()