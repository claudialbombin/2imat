#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXAMEN: Juego de números binarios
Ejercicios típicos:
- Generar número aleatorio (1-15) y mostrarlo en LEDs referencia (GPIO20-23)
- Jugador replica en LEDs respuesta (GPIO24-27) con pulsadores (GPIO7,16,17,19)
- Al coincidir, reiniciar con nuevo número
- Añadir tiempo límite (10s) con parpadeo en últimos 5s
- Añadir LDR para modo memorización (poca luz)
"""

import time
import random
from gpiozero import LED, Button, LEDBoard, MCP3008

# ============================================================
# PARTE 1: Versión básica (3 puntos)
# ============================================================

def juego_binario_basico():
    """
    Versión básica del juego:
    - LEDs referencia: GPIO20 (LSB) a GPIO23 (MSB)
    - LEDs respuesta: GPIO24 (LSB) a GPIO27 (MSB)
    - Pulsadores: GPIO7 (toggle LED24), GPIO16 (LED25), 
                  GPIO17 (LED26), GPIO19 (LED27)
    """
    # LEDs
    ref_leds = LEDBoard(20, 21, 22, 23)  # Referencia
    resp_leds = LEDBoard(24, 25, 26, 27)  # Respuesta
    
    # Pulsadores
    botones = [
        Button(7),   # índice 0 -> LED24
        Button(16),  # índice 1 -> LED25
        Button(17),  # índice 2 -> LED26
        Button(19)   # índice 3 -> LED27
    ]
    
    # Variables de juego
    numero_referencia = 0
    numero_respuesta = 0
    
    # Estados anteriores de botones (para detección de flanco)
    botones_anteriores = [b.is_pressed for b in botones]
    
    PERIODO_SCAN = 0.05
    
    def nuevo_numero():
        """Genera nuevo número aleatorio y actualiza LEDs"""
        nonlocal numero_referencia, numero_respuesta
        numero_referencia = random.randint(1, 15)
        numero_respuesta = 0
        
        # Mostrar en LEDs de referencia
        bits_ref = [(numero_referencia >> i) & 1 for i in range(4)]
        for i, led in enumerate(ref_leds):
            if bits_ref[i]:
                led.on()
            else:
                led.off()
        
        # Apagar LEDs de respuesta
        resp_leds.off()
        
        print(f"Nuevo número: {numero_referencia} (bin: {bits_ref})")
    
    # Empezar juego
    nuevo_numero()
    
    try:
        while True:
            inicio_ciclo = time.time()
            
            # Leer todos los botones
            botones_actuales = [b.is_pressed for b in botones]
            
            # Procesar cada botón (detección de flanco)
            for i in range(4):
                if botones_anteriores[i] and not botones_actuales[i]:
                    # Toggle del bit correspondiente
                    numero_respuesta ^= (1 << i)
                    print(f"Botón {i} pulsado, respuesta: {numero_respuesta}")
            
            botones_anteriores = botones_actuales.copy()
            
            # Actualizar LEDs de respuesta
            bits_resp = [(numero_respuesta >> i) & 1 for i in range(4)]
            for i, led in enumerate(resp_leds):
                if bits_resp[i]:
                    led.on()
                else:
                    led.off()
            
            # Comprobar coincidencia
            if numero_respuesta == numero_referencia:
                print("¡COINCIDENCIA! Nuevo número...")
                nuevo_numero()
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        ref_leds.off()
        resp_leds.off()

# ============================================================
# PARTE 2: Con tiempo límite (4 puntos)
# ============================================================

def juego_binario_tiempo():
    """
    Añade tiempo límite de 10 segundos
    - Cuando quedan <5s: LEDs referencia parpadean a 1Hz sincronizados
    - Si tiempo agotado: reiniciar juego
    """
    ref_leds = LEDBoard(20, 21, 22, 23)
    resp_leds = LEDBoard(24, 25, 26, 27)
    
    botones = [Button(7), Button(16), Button(17), Button(19)]
    
    numero_referencia = 0
    numero_respuesta = 0
    
    botones_anteriores = [b.is_pressed for b in botones]
    
    # Variables de tiempo
    tiempo_inicio_partida = time.time()
    TIEMPO_LIMITE = 10  # segundos
    UMBRAL_PARPADEO = 5  # segundos (cuando quedan <5)
    
    # Variables para parpadeo
    tiempo_ultimo_parpadeo = time.time()
    estado_parpadeo = True
    PERIODO_PAR_PARPADEO = 0.5  # 1Hz (medio período)
    
    PERIODO_SCAN = 0.05
    
    def nuevo_numero():
        nonlocal numero_referencia, numero_respuesta, tiempo_inicio_partida
        nonlocal tiempo_ultimo_parpadeo, estado_parpadeo
        
        numero_referencia = random.randint(1, 15)
        numero_respuesta = 0
        
        # Mostrar referencia
        bits_ref = [(numero_referencia >> i) & 1 for i in range(4)]
        for i, led in enumerate(ref_leds):
            if bits_ref[i]:
                led.on()
            else:
                led.off()
        
        resp_leds.off()
        
        # Reiniciar temporizadores
        tiempo_inicio_partida = time.time()
        tiempo_ultimo_parpadeo = time.time()
        estado_parpadeo = True
        
        print(f"Nuevo número: {numero_referencia}")
    
    nuevo_numero()
    
    try:
        while True:
            inicio_ciclo = time.time()
            tiempo_actual = time.time()
            
            # Calcular tiempo restante
            tiempo_transcurrido = tiempo_actual - tiempo_inicio_partida
            tiempo_restante = TIEMPO_LIMITE - tiempo_transcurrido
            
            # Leer botones
            botones_actuales = [b.is_pressed for b in botones]
            
            for i in range(4):
                if botones_anteriores[i] and not botones_actuales[i]:
                    numero_respuesta ^= (1 << i)
            
            botones_anteriores = botones_actuales.copy()
            
            # Actualizar LEDs respuesta
            bits_resp = [(numero_respuesta >> i) & 1 for i in range(4)]
            for i, led in enumerate(resp_leds):
                if bits_resp[i]:
                    led.on()
                else:
                    led.off()
            
            # Comprobar condiciones
            if numero_respuesta == numero_referencia:
                print("¡Coincidencia!")
                nuevo_numero()
            elif tiempo_restante <= 0:
                print("¡Tiempo agotado!")
                nuevo_numero()
            
            # Control de parpadeo (cuando quedan <5s)
            if 0 < tiempo_restante < UMBRAL_PARPADEO:
                if tiempo_actual - tiempo_ultimo_parpadeo >= PERIODO_PAR_PARPADEO:
                    estado_parpadeo = not estado_parpadeo
                    tiempo_ultimo_parpadeo = tiempo_actual
                    
                    if estado_parpadeo:
                        # Encender solo los bits que deberían estar encendidos
                        bits_ref = [(numero_referencia >> i) & 1 for i in range(4)]
                        for i, led in enumerate(ref_leds):
                            if bits_ref[i]:
                                led.on()
                            else:
                                led.off()
                    else:
                        # Apagar todos
                        ref_leds.off()
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        ref_leds.off()
        resp_leds.off()

# ============================================================
# PARTE 3: Con LDR - Modo memorización (3 puntos)
# ============================================================

def juego_binario_ldr():
    """
    Añade LDR para modo memorización:
    - Si hay poca luz al iniciar: LEDs referencia se apagan tras 1s
    - Usuario debe memorizar el número
    - En este modo NO hay parpadeo en últimos 5s
    """
    ref_leds = LEDBoard(20, 21, 22, 23)
    resp_leds = LEDBoard(24, 25, 26, 27)
    
    botones = [Button(7), Button(16), Button(17), Button(19)]
    
    # Sensor LDR (conectado a CH0 con divisor de tensión)
    ldr = MCP3008(channel=0)
    
    numero_referencia = 0
    numero_respuesta = 0
    
    botones_anteriores = [b.is_pressed for b in botones]
    
    tiempo_inicio_partida = time.time()
    TIEMPO_LIMITE = 10
    UMBRAL_PARPADEO = 5
    
    tiempo_ultimo_parpadeo = time.time()
    estado_parpadeo = True
    PERIODO_PAR_PARPADEO = 0.5
    
    # Variables para modo memorización
    UMBRAL_LUZ = 1.5  # Voltios: por debajo = poca luz (ajustar)
    TIEMPO_MEMORIZACION = 1.0  # segundos que duran LEDs encendidos
    tiempo_apagado_ref = 0
    modo_oscuro = False
    
    PERIODO_SCAN = 0.05
    
    def nuevo_numero():
        nonlocal numero_referencia, numero_respuesta, tiempo_inicio_partida
        nonlocal tiempo_ultimo_parpadeo, estado_parpadeo, tiempo_apagado_ref, modo_oscuro
        
        numero_referencia = random.randint(1, 15)
        numero_respuesta = 0
        
        # Leer luz al iniciar partida
        voltios_luz = ldr.voltage
        modo_oscuro = (voltios_luz < UMBRAL_LUZ)
        
        # Mostrar número referencia
        bits_ref = [(numero_referencia >> i) & 1 for i in range(4)]
        for i, led in enumerate(ref_leds):
            if bits_ref[i]:
                led.on()
            else:
                led.off()
        
        # Registrar tiempo para apagado en modo oscuro
        if modo_oscuro:
            tiempo_apagado_ref = time.time()
            print("MODO MEMORIZACIÓN: LEDs se apagarán en 1s")
        
        resp_leds.off()
        
        tiempo_inicio_partida = time.time()
        tiempo_ultimo_parpadeo = time.time()
        estado_parpadeo = True
        
        print(f"Nuevo número: {numero_referencia} (Luz: {voltios_luz:.2f}V)")
    
    nuevo_numero()
    
    try:
        while True:
            inicio_ciclo = time.time()
            tiempo_actual = time.time()
            
            # Leer luz actual (por si cambia durante la partida)
            voltios_luz = ldr.voltage
            
            tiempo_transcurrido = tiempo_actual - tiempo_inicio_partida
            tiempo_restante = TIEMPO_LIMITE - tiempo_transcurrido
            
            # Control de LEDs referencia en modo oscuro
            if modo_oscuro:
                # En modo oscuro, apagar después de 1 segundo
                if tiempo_actual - tiempo_apagado_ref >= TIEMPO_MEMORIZACION:
                    ref_leds.off()
            
            # Leer botones
            botones_actuales = [b.is_pressed for b in botones]
            
            for i in range(4):
                if botones_anteriores[i] and not botones_actuales[i]:
                    numero_respuesta ^= (1 << i)
            
            botones_anteriores = botones_actuales.copy()
            
            # Actualizar LEDs respuesta
            bits_resp = [(numero_respuesta >> i) & 1 for i in range(4)]
            for i, led in enumerate(resp_leds):
                if bits_resp[i]:
                    led.on()
                else:
                    led.off()
            
            # Comprobar condiciones
            if numero_respuesta == numero_referencia:
                print("¡Coincidencia!")
                nuevo_numero()
            elif tiempo_restante <= 0:
                print("¡Tiempo agotado!")
                nuevo_numero()
            
            # Control de parpadeo (solo si NO estamos en modo oscuro)
            if not modo_oscuro and 0 < tiempo_restante < UMBRAL_PARPADEO:
                if tiempo_actual - tiempo_ultimo_parpadeo >= PERIODO_PAR_PARPADEO:
                    estado_parpadeo = not estado_parpadeo
                    tiempo_ultimo_parpadeo = tiempo_actual
                    
                    if estado_parpadeo:
                        bits_ref = [(numero_referencia >> i) & 1 for i in range(4)]
                        for i, led in enumerate(ref_leds):
                            if bits_ref[i]:
                                led.on()
                    else:
                        ref_leds.off()
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        ref_leds.off()
        resp_leds.off()

if __name__ == "__main__":
    # Elegir versión
    # juego_binario_basico()
    # juego_binario_tiempo()
    juego_binario_ldr()