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
import time                        # Para esperas y medir tiempos

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

# ═══════════════════════════════════════════════════════════════════
# 5. FUNCIÓN PARA DETECTAR PULSACIÓN LARGA (RESET)
# ═══════════════════════════════════════════════════════════════════

def pulsacion_larga(btn, segundos=TIEMPO_RESET):
    """
    Detecta si un botón ha estado pulsado durante 'segundos' segundos.
    
    CÓMO FUNCIONA:
    1. Mira si el botón está pulsado ahora mismo
    2. Espera 0.05 segundos (anti-rebote, evita lecturas falsas)
    3. Si sigue pulsado, empieza a contar el tiempo
    4. Si el tiempo supera 'segundos', espera a que suelte el botón
    5. Devuelve True si se cumplió, False si no
    
    btn: objeto Button de gpiozero
    segundos: cuánto tiempo hay que mantener (default 2.0)
    """
    # ¿Está pulsado el botón ahora mismo?
    if btn.is_pressed:
        # Pequeña pausa para evitar rebotes (el botón puede vibrar al pulsar)
        time.sleep(0.05)
        
        # ¿Sigue pulsado después del anti-rebote?
        if btn.is_pressed:
            # Guardamos el momento en que empezó a pulsarse
            inicio = time.time()
            
            # Mientras el botón siga pulsado...
            while btn.is_pressed:
                # ¿Ya pasó el tiempo requerido?
                if time.time() - inicio >= segundos:
                    # Esperamos a que suelte el botón (para no contar varias veces)
                    while btn.is_pressed:
                        time.sleep(0.01)
                    return True  # ¡Pulsación larga detectada!
                
                # Pequeña pausa para no saturar el procesador
                time.sleep(0.01)
    
    # Si llegamos aquí, no hubo pulsación larga
    return False

def comprobar_reset():
    """
    Comprueba si se debe reiniciar el juego.
    Reinicia si se mantiene pulsado el botón izquierdo 2 segundos.
    Devuelve True si hay que reiniciar, False si no.
    """
    if pulsacion_larga(btn_izq):
        print("🔄 RESET por pulsación larga (2 segundos)")
        return True
    return False


def procesar_boton_izquierdo():
    """Devuelve 'mover', 'reset' o None según la pulsación del botón 17."""
    if not btn_izq.is_pressed:
        return None

    time.sleep(0.05)

    if not btn_izq.is_pressed:
        return None

    inicio_presion = time.time()

    while btn_izq.is_pressed:
        if time.time() - inicio_presion >= TIEMPO_RESET:
            while btn_izq.is_pressed:
                time.sleep(0.01)
            return "reset"
        time.sleep(0.01)

    return "mover"


def procesar_boton_normal(btn):
    """Devuelve True si el botón se pulsa y se suelta, False si no."""
    if not btn.is_pressed:
        return False

    time.sleep(0.05)

    if not btn.is_pressed:
        return False

    while btn.is_pressed:
        time.sleep(0.01)

    return True


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
    
    while True:
        accion = procesar_boton_izquierdo()
        if humedad <ref:
            led_riego.on()
        else:
            led_riego.off()

        if accion == "reset":
            humedad = 0
            actualizar_leds(humedad)
            actualizar_leds_desviacion_humedad()
            mostrar_humedad_actual()
            led_riego.off()
            continue

        if accion == "mover":
            ajustar_humedad(-1)
            continue

        if procesar_boton_normal(btn_der):
            ajustar_humedad(1)
            continue

        if procesar_boton_normal(btn_reset):
            humedad = 0
            actualizar_leds(humedad)
            actualizar_leds_desviacion_humedad()
            mostrar_humedad_actual()
            continue
        if humedad ==0:
            led_riego.off()
        time.sleep(0.01)

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