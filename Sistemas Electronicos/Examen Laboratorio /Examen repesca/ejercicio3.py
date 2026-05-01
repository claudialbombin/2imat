#!/usr/bin/env python3
"""
EJERCICIO 1 - MANEJO DE ENTRADAS Y SALIDAS DIGITALES
====================================================

QUÉ HACE ESTE PROGRAMA:
- Muestra el porcentaje de agua con una barra de LEDs
- 0% -> ningún LED encendido
- 0-25% -> solo el LED 24
- 25-50% -> LEDs 24 y 25
- 50-75% -> LEDs 24, 25 y 26
- 75-100% -> LEDs 24, 25, 26, 27, 28 y 29
- Mantén pulsado el botón izquierdo 2 segundos para poner la humedad a 0%
- Al salir con Ctrl+C, apaga los LEDs
"""

# LIBRERÍAS NECESARIAS
from gpiozero import LED, Button, PWMLED  # Para controlar LEDs y botones
import random
import time

# ═══════════════════════════════════════════════════════════════════
# 1. CONFIGURACIÓN - CAMBIA AQUÍ LOS PINES SEGÚN TU MONTAJE
# ═══════════════════════════════════════════════════════════════════

# Lista de pines donde están conectados los LEDs del indicador de agua
LEDS_PINS = [24, 25, 26, 27]
led_riego = LED(21)
led_humedad_baja = PWMLED(20)
led_humedad_alta = PWMLED(22)

TIEMPO_RESET = 2.0  # Tiempo en segundos para considerar una pulsación larga (reset)
humedad = 50
ref = 40

# Pines de los botones
BTN_IZQ_PIN = 17    # Botón izquierdo (también sirve para reset si mantienes)
BTN_DER_PIN = 19    # Botón derecho
BTN_RESET_PIN = 16 # Botón de salto aleatorio

# ═══════════════════════════════════════════════════════════════════
# 2. CREAR LOS OBJETOS (LEDs y Botones)
# ═══════════════════════════════════════════════════════════════════

# Crear una lista de objetos LED (uno por cada pin)
# Ej: leds[0] controla el LED del pin 24
leds = [LED(pin) for pin in LEDS_PINS]


# Crear botones con pull_up=True (el botón conecta a GND cuando se pulsa)
# pull_up=True significa que el pin está en HIGH (3.3V) cuando NO se pulsa
btn_izq = Button(BTN_IZQ_PIN, pull_up=True)
btn_der = Button(BTN_DER_PIN, pull_up=True)
btn_reset = Button(BTN_RESET_PIN, pull_up=True)


# ═══════════════════════════════════════════════════════════════════
# 4. FUNCIONES BÁSICAS DEL JUEGO
# ═══════════════════════════════════════════════════════════════════

def inicializar():
    """
    Apaga TODOS los LEDs al empezar.
    Esto asegura que no quede ningún LED encendido de un valor anterior.
    """
    for led in leds:
        led.off()
    led_humedad_baja.off()
    led_humedad_alta.off()


def actualizar_leds(porcentaje):
    """
    Enciende una barra de LEDs según el porcentaje de agua.

    porcentaje: valor entre 0 y 100.
    """
    porcentaje = max(0, min(100, porcentaje))

    if porcentaje == 0:
        leds_encendidos = 0
    elif porcentaje <= 25:
        leds_encendidos = 1
    elif porcentaje <= 50:
        leds_encendidos = 2
    elif porcentaje <= 75:
        leds_encendidos = 3
    else:
        leds_encendidos = len(leds)

    for i, led in enumerate(leds):
        if i < leds_encendidos:
            led.on()   # Enciende el LED de la posición actual
        else:
            led.off()  # Apaga los demás


def mostrar_humedad_actual():
    print(f"💧 Humedad actual: {humedad}%")


def actualizar_leds_desviacion_humedad():
    """Muestra con PWM cuánto se aleja la humedad de la referencia."""
    diferencia = abs(humedad - ref)
    intensidad = min(1.0, diferencia / 100.0)

    if humedad < ref:
        led_humedad_baja.value = intensidad
        led_humedad_alta.off()
    elif humedad > ref:
        led_humedad_alta.value = intensidad
        led_humedad_baja.off()
    else:
        led_humedad_baja.off()
        led_humedad_alta.off()

def ajustar_humedad(delta):
    global humedad
    humedad = max(0, min(100, humedad + delta))
    actualizar_leds(humedad)
    actualizar_leds_desviacion_humedad()
    mostrar_humedad_actual()





# ═══════════════════════════════════════════════════════════════════
# 7. LÓGICA PRINCIPAL DEL INDICADOR
# ═══════════════════════════════════════════════════════════════════

def jugar():
    global humedad
    """Ejecuta el indicador de humedad."""

    inicializar()
    actualizar_leds(humedad)
    actualizar_leds_desviacion_humedad()

    print("Indicador de humedad activo")
    print("Botón 17: baja 25% | Botón 19: sube 25% | Botón 16: pone 0%")
    print("Umbrales: 0%, 25%, 50%, 75%, 100%")

    siguiente_cambio_humedad = time.monotonic() + 3.0

    izq_anterior = btn_izq.is_pressed
    der_anterior = btn_der.is_pressed
    reset_anterior = btn_reset.is_pressed
    inicio_pulsacion_izq = None
    reset_largo_izq = False
    
    while True:
        ahora = time.monotonic()

        if ahora >= siguiente_cambio_humedad:
            humedad = random.randint(0, 100)
            actualizar_leds(humedad)
            actualizar_leds_desviacion_humedad()
            mostrar_humedad_actual()
            siguiente_cambio_humedad += 3.0

        if humedad < ref:
            led_riego.on()
        else:
            led_riego.off()

        izq_actual = btn_izq.is_pressed
        der_actual = btn_der.is_pressed
        reset_actual = btn_reset.is_pressed

        if izq_actual and not izq_anterior:
            inicio_pulsacion_izq = ahora
            reset_largo_izq = False

        if izq_actual and inicio_pulsacion_izq is not None and not reset_largo_izq:
            if ahora - inicio_pulsacion_izq >= TIEMPO_RESET:
                humedad = 0
                actualizar_leds(humedad)
                actualizar_leds_desviacion_humedad()
                mostrar_humedad_actual()
                led_riego.off()
                reset_largo_izq = True

        if (not izq_actual) and izq_anterior:
            if inicio_pulsacion_izq is not None and not reset_largo_izq:
                ajustar_humedad(-1)
            inicio_pulsacion_izq = None
            reset_largo_izq = False

        if (not der_actual) and der_anterior:
            ajustar_humedad(1)

        if (not reset_actual) and reset_anterior:
            humedad = 0
            actualizar_leds(humedad)
            actualizar_leds_desviacion_humedad()
            mostrar_humedad_actual()

        if humedad == 0:
            led_riego.off()

        izq_anterior = izq_actual
        der_anterior = der_actual
        reset_anterior = reset_actual

# ═══════════════════════════════════════════════════════════════════
# 8. PUNTO DE ENTRADA DEL PROGRAMA (donde empieza todo)
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Esta parte se ejecuta SOLO si ejecutamos este archivo directamente.
    Si importamos este archivo como módulo, NO se ejecuta.
    """
    
    
    try:
        jugar()
            
    except KeyboardInterrupt:
        for led in leds:
            led.off()
        led_humedad_baja.off()
        led_humedad_alta.off()