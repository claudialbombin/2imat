#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXAMEN: Juego del personaje con LEDs y control de intensidad
- LEDs: GPIO20 a GPIO24 (5 LEDs)
- Personaje: un LED encendido que se mueve
- GPIO16: derecha (+1)
- GPIO17: izquierda (-1) y también reinicio (pulsación larga 2s)
- GPIO19: movimiento aleatorio (-2 a +2)
- Intensidades: centro 100%, adyacentes 60%, bordes 20%
- Si 4s sin pulsar: movimiento aleatorio automático
"""

import time
import random
from gpiozero import PWMLED, Button

# ============================================================
# CONFIGURACIÓN
# ============================================================

# LEDs con PWM para control de intensidad (GPIO20 a GPIO24)
leds_pwm = [
    PWMLED(20, frequency=100),  # Borde izquierdo (20% intensidad)
    PWMLED(21, frequency=100),  # Adyacente izquierdo (60%)
    PWMLED(22, frequency=100),  # Centro (100%)
    PWMLED(23, frequency=100),  # Adyacente derecho (60%)
    PWMLED(24, frequency=100)   # Borde derecho (20%)
]

# Botones
btn_derecha = Button(16)   # Mover derecha (+1)
btn_izquierda = Button(17)  # Mover izquierda (-1) y reinicio (pulsación larga)
btn_aleatorio = Button(19)  # Movimiento aleatorio (-2 a +2)

# Constantes de posición
POS_INICIAL = 2  # Índice 2 = GPIO22 (centro)
LIMITE_IZQ = 0   # Índice 0 = GPIO20
LIMITE_DER = 4   # Índice 4 = GPIO24

# Intensidades fijas por posición (ejercicio 2)
INTENSIDADES = [0.2, 0.6, 1.0, 0.6, 0.2]  # 20%, 60%, 100%, 60%, 20%

# Variables de juego
posicion_actual = POS_INICIAL
juego_activo = True

# Variables para tiempo de inactividad (ejercicio 3)
TIEMPO_MAX_INACTIVIDAD = 4.0  # segundos
ultima_pulsacion = time.time()

# Variables para detección de pulsación larga de reinicio
tiempo_pulsacion_izquierda = 0
TIEMPO_REINICIO = 2.0  # segundos necesarios para reiniciar

# Detección de flanco para botones
ant_derecha = btn_derecha.is_pressed
ant_izquierda = btn_izquierda.is_pressed
ant_aleatorio = btn_aleatorio.is_pressed

PERIODO_SCAN = 0.05  # 50 ms

# ============================================================
# FUNCIONES DEL JUEGO
# ============================================================

def aplicar_intensidades():
    """Aplica las intensidades fijas a todos los LEDs"""
    for i, led in enumerate(leds_pwm):
        led.value = INTENSIDADES[i]

def actualizar_personaje():
    """
    Actualiza la visualización: el LED del personaje se enciende
    con su intensidad correspondiente, los demás con la suya
    """
    # Primero apagamos todos (aunque luego los encenderemos con su intensidad)
    for led in leds_pwm:
        led.off()
    
    # Encendemos el LED del personaje con su intensidad correspondiente
    leds_pwm[posicion_actual].value = INTENSIDADES[posicion_actual]
    
    # Los demás LEDs también deben tener su intensidad base
    # pero como están apagados, no se ven. Esto es correcto.

def game_over():
    """Maneja la condición de derrota"""
    global juego_activo
    juego_activo = False
    # Apagar todos los LEDs
    for led in leds_pwm:
        led.off()
    print("💀 GAME OVER - Mantén GPIO17 pulsado 2s para reiniciar")

def reiniciar_juego():
    """Reinicia el juego a su estado inicial"""
    global posicion_actual, juego_activo, ultima_pulsacion
    posicion_actual = POS_INICIAL
    juego_activo = True
    ultima_pulsacion = time.time()
    actualizar_personaje()
    print("🔄 Juego reiniciado")

def mover_derecha():
    """Mueve el personaje a la derecha (+1)"""
    global posicion_actual, juego_activo, ultima_pulsacion
    if not juego_activo:
        return
    
    ultima_pulsacion = time.time()
    print("➡️ Mover derecha")
    
    nueva_pos = posicion_actual + 1
    if nueva_pos > LIMITE_DER:
        print("¡Fuera del tablero! GAME OVER")
        game_over()
    else:
        posicion_actual = nueva_pos
        actualizar_personaje()
        print(f"Posición: GPIO{20+posicion_actual}")

def mover_izquierda():
    """Mueve el personaje a la izquierda (-1)"""
    global posicion_actual, juego_activo, ultima_pulsacion
    if not juego_activo:
        return
    
    ultima_pulsacion = time.time()
    print("⬅️ Mover izquierda")
    
    nueva_pos = posicion_actual - 1
    if nueva_pos < LIMITE_IZQ:
        print("¡Fuera del tablero! GAME OVER")
        game_over()
    else:
        posicion_actual = nueva_pos
        actualizar_personaje()
        print(f"Posición: GPIO{20+posicion_actual}")

def mover_aleatorio():
    """Mueve el personaje un número aleatorio entre -2 y +2"""
    global posicion_actual, juego_activo, ultima_pulsacion
    if not juego_activo:
        return
    
    ultima_pulsacion = time.time()
    desplazamiento = random.randint(-2, 2)
    print(f"🎲 Movimiento aleatorio: {desplazamiento}")
    
    nueva_pos = posicion_actual + desplazamiento
    
    if nueva_pos < LIMITE_IZQ or nueva_pos > LIMITE_DER:
        print("¡Fuera del tablero! GAME OVER")
        game_over()
    else:
        posicion_actual = nueva_pos
        actualizar_personaje()
        print(f"Posición: GPIO{20+posicion_actual}")

# ============================================================
# BUCLE PRINCIPAL
# ============================================================

# Estado inicial
aplicar_intensidades()  # Configurar intensidades base
actualizar_personaje()
print("🎮 Juego iniciado - Personaje en posición central (GPIO22)")
print(f"Intensidades: 20% (bordes), 60% (adyacentes), 100% (centro)")
print("Controles:")
print("  GPIO16: derecha (+1)")
print("  GPIO17: izquierda (-1) y reinicio (pulsar 2s en game over)")
print("  GPIO19: movimiento aleatorio (-2 a +2)")
print(f"  Inactividad {TIEMPO_MAX_INACTIVIDAD}s: movimiento aleatorio automático")

try:
    while True:
        inicio_ciclo = time.time()
        tiempo_actual = time.time()
        
        # ====================================================
        # EJERCICIO 3: Movimiento automático por inactividad
        # ====================================================
        if juego_activo:
            tiempo_inactividad = tiempo_actual - ultima_pulsacion
            if tiempo_inactividad >= TIEMPO_MAX_INACTIVIDAD:
                print(f"⏰ {TIEMPO_MAX_INACTIVIDAD}s sin pulsar - Movimiento aleatorio automático")
                mover_aleatorio()
                ultima_pulsacion = tiempo_actual  # Reiniciar contador después del movimiento
        
        # ====================================================
        # LECTURA DE BOTONES
        # ====================================================
        
        # Botón derecha (GPIO16)
        act_derecha = btn_derecha.is_pressed
        if ant_derecha and not act_derecha and juego_activo:
            mover_derecha()
        ant_derecha = act_derecha
        
        # Botón izquierda (GPIO17) - Movimiento y reinicio
        act_izquierda = btn_izquierda.is_pressed
        
        # Detectar flanco de bajada (pulsación) para movimiento
        if ant_izquierda and not act_izquierda and juego_activo:
            mover_izquierda()
        
        # Detectar pulsación larga para reinicio (en cualquier estado)
        if act_izquierda:
            if tiempo_pulsacion_izquierda == 0:
                tiempo_pulsacion_izquierda = tiempo_actual
            elif tiempo_actual - tiempo_pulsacion_izquierda >= TIEMPO_REINICIO:
                print("🔄 Pulsación larga detectada - Reiniciando juego")
                reiniciar_juego()
                tiempo_pulsacion_izquierda = 0  # Reiniciar contador
        else:
            tiempo_pulsacion_izquierda = 0  # Botón soltado, reiniciar contador
        
        ant_izquierda = act_izquierda
        
        # Botón aleatorio (GPIO19)
        act_aleatorio = btn_aleatorio.is_pressed
        if ant_aleatorio and not act_aleatorio and juego_activo:
            mover_aleatorio()
        ant_aleatorio = act_aleatorio
        
        # Mantener período de scan
        tiempo_ejecucion = time.time() - inicio_ciclo
        if tiempo_ejecucion < PERIODO_SCAN:
            time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
except KeyboardInterrupt:
    print("\nPrograma terminado")
finally:
    for led in leds_pwm:
        led.off()
