#!/usr/bin/env python3
"""
EJERCICIO 1 - MANEJO DE ENTRADAS Y SALIDAS DIGITALES
====================================================

QUÉ HACE ESTE PROGRAMA:
- Un personaje (representado por un LED encendido) se mueve por 5 LEDs
- Botones: izquierda, derecha, y salto aleatorio
- Si te sales del tablero (posición <0 o >4) PIERDES
- Si llegas al extremo derecho (LED 24) GANAS
- Mantén pulsado el botón izquierdo 2 segundos para REINICIAR
"""

# LIBRERÍAS NECESARIAS
from gpiozero import LED, Button  # Para controlar LEDs y botones
import time                        # Para esperas y medir tiempos
import random                      # Para generar números aleatorios

# ═══════════════════════════════════════════════════════════════════
# 1. CONFIGURACIÓN - CAMBIA AQUÍ LOS PINES SEGÚN TU MONTAJE
# ═══════════════════════════════════════════════════════════════════

# Lista de pines donde están conectados los LEDs del juego
# Índices: 0=izquierda, 2=centro, 4=derecha
LEDS_PINS = [20, 21, 22, 23, 24]

# Posición donde empieza el personaje (2 = centro, LED 22)
pos_inicial = 2

# Pines de los botones
BTN_IZQ_PIN = 16    # Botón izquierdo (también sirve para reset si mantienes)
BTN_DER_PIN = 19    # Botón derecho
BTN_RANDOM_PIN = 26 # Botón de salto aleatorio

# LEDs auxiliares
LED_VICTORIA_PIN = 25  # Se enciende cuando ganas
LED_SEMAFORO_PIN = 27  # Semáforo (no se usa en este ejercicio)

# Configuración del juego
SALTO_MIN = -2   # Salto aleatorio mínimo (puede saltar 2 atrás)
SALTO_MAX = 2    # Salto aleatorio máximo (puede saltar 2 adelante)
TIEMPO_RESET = 2.0  # Segundos que hay que mantener pulsado para resetear

# ═══════════════════════════════════════════════════════════════════
# 2. CREAR LOS OBJETOS (LEDs y Botones)
# ═══════════════════════════════════════════════════════════════════

# Crear una lista de objetos LED (uno por cada pin)
# Ej: leds[0] controla el LED del pin 20
leds = [LED(pin) for pin in LEDS_PINS]

# LEDs auxiliares individuales
led_victoria = LED(LED_VICTORIA_PIN)
led_semaforo = LED(LED_SEMAFORO_PIN)

# Crear botones con pull_up=True (el botón conecta a GND cuando se pulsa)
# pull_up=True significa que el pin está en HIGH (3.3V) cuando NO se pulsa
btn_izq = Button(BTN_IZQ_PIN, pull_up=True)
btn_der = Button(BTN_DER_PIN, pull_up=True)
btn_random = Button(BTN_RANDOM_PIN, pull_up=True)

# ═══════════════════════════════════════════════════════════════════
# 3. FUNCIONES BÁSICAS DEL JUEGO
# ═══════════════════════════════════════════════════════════════════

def inicializar():
    """
    Apaga TODOS los LEDs al empezar una partida.
    Esto asegura que no quede ningún LED encendido de partidas anteriores.
    """
    # Recorremos todos los LEDs del juego
    for led in leds:
        led.off()  # .off() apaga el LED
    
    # Apagamos también los LEDs auxiliares
    led_victoria.off()
    led_semaforo.off()

def actualizar_leds(posicion):
    """
    Enciende SOLO el LED que está en la 'posicion' indicada.
    Apaga todos los demás.
    
    posicion: número entre 0 y 4 (porque tenemos 5 LEDs)
              0 = LED más izquierdo (pin 20)
              4 = LED más derecho (pin 24)
    """
    # Recorremos todos los LEDs con su índice (i) y el objeto led
    for i, led in enumerate(leds):
        if i == posicion:
            led.on()   # Enciende el LED de la posición actual
        else:
            led.off()  # Apaga los demás

# ═══════════════════════════════════════════════════════════════════
# 4. FUNCIÓN PARA DETECTAR PULSACIÓN LARGA (RESET)
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

# ═══════════════════════════════════════════════════════════════════
# 5. CONDICIONES DE VICTORIA Y DERROTA
# ═══════════════════════════════════════════════════════════════════

def comprobar_victoria(posicion):
    """
    Comprueba si el jugador ha GANADO.
    En este juego: GANAS si llegas al extremo derecho (último LED).
    
    posicion: posición actual (0 a 4)
    Devuelve True si has ganado, False si no.
    """
    # len(leds) es 5, entonces len(leds)-1 es 4 (último índice)
    return posicion == len(leds) - 1

def comprobar_derrota(posicion):
    """
    Comprueba si el jugador ha PERDIDO.
    En este juego: PIERDES si te sales del tablero.
    
    posicion: posición actual
    Devuelve True si has perdido, False si no.
    """
    # Si posición es menor que 0 (izquierda del todo) O
    # Si posición es mayor o igual que 5 (derecha del todo)
    return posicion < 0 or posicion >= len(leds)

def gestionar_victoria():
    """
    Acciones que se ejecutan cuando el jugador GANA:
    - Muestra mensaje en consola
    - Enciende el LED de victoria durante 2 segundos
    - Apaga el LED de victoria
    """
    print("¡¡¡GANASTE!!!")
    led_victoria.on()      # Enciende LED
    time.sleep(2)          # Espera 2 segundos
    led_victoria.off()     # Apaga LED

def gestionar_derrota():
    """
    Acciones cuando el jugador PIERDE:
    - Muestra mensaje
    - Parpadea el LED de victoria (rojo) 3 veces para indicar derrota
    - No requiere reset automático, el bucle principal se encarga
    """
    print("PERDISTE :(")
    # Parpadea 3 veces (encender/apagar)
    for _ in range(3):
        led_victoria.on()
        time.sleep(0.3)
        led_victoria.off()
        time.sleep(0.3)

# ═══════════════════════════════════════════════════════════════════
# 6. LÓGICA PRINCIPAL DEL JUEGO
# ═══════════════════════════════════════════════════════════════════

def jugar():
    """
    Ejecuta UNA partida completa.
    Devuelve:
        True  → si el jugador GANÓ
        False → si el jugador PERDIÓ
        None  → si se pidió RESET (pulsación larga)
    """
    
    # Posición inicial del personaje (centro)
    posicion = pos_inicial
    
    # Apagar todo y encender la posición inicial
    inicializar()
    actualizar_leds(posicion)
    
    print(f"Posición inicial: LED {LEDS_PINS[posicion]} (índice {posicion})")
    print(f"(Mantén botón izquierdo {TIEMPO_RESET}s para reiniciar)")
    
    # BUCLE PRINCIPAL DE LA PARTIDA
    # Se ejecuta hasta que el jugador gane, pierda o pida reset
    while True:
        
        # ============================================================
        # 1. COMPROBAR RESET (lo más prioritario)
        # ============================================================
        if comprobar_reset():
            return None  # None significa "reinicia la partida"
        
        # ============================================================
        # 2. LEER BOTÓN DERECHO (mover a la derecha)
        # ============================================================
        # .is_pressed es True si el botón está pulsado en este momento
        if btn_der.is_pressed:
            # Anti-rebote: esperamos 0.05 segundos para confirmar
            time.sleep(0.05)
            
            # Verificamos que no sea pulsación larga (para no confundir)
            if pulsacion_larga(btn_der):
                continue  # Si es larga, ignoramos y volvemos al inicio
            
            # Movemos a la derecha (sumamos 1 a la posición)
            posicion += 1
            print(f"→ Derecha | Nueva posición: {posicion} (LED {LEDS_PINS[posicion] if 0 <= posicion < len(leds) else 'FUERA'})")
            
            # Esperamos a que suelte el botón (para no detectar múltiples pulsaciones)
            while btn_der.is_pressed:
                time.sleep(0.01)
        
        # ============================================================
        # 3. LEER BOTÓN IZQUIERDO (mover a la izquierda)
        # ============================================================
        elif btn_izq.is_pressed:
            time.sleep(0.05)
            
            # Si es pulsación larga, ya la detectó comprobar_reset()
            # Aquí solo manejamos pulsación corta
            if pulsacion_larga(btn_izq):
                continue
            
            # Movemos a la izquierda (restamos 1)
            posicion -= 1
            print(f"← Izquierda | Nueva posición: {posicion} (LED {LEDS_PINS[posicion] if 0 <= posicion < len(leds) else 'FUERA'})")
            
            while btn_izq.is_pressed:
                time.sleep(0.01)
        
        # ============================================================
        # 4. LEER BOTÓN RANDOM (salto aleatorio)
        # ============================================================
        elif btn_random.is_pressed:
            time.sleep(0.05)
            
            if pulsacion_larga(btn_random):
                continue
            
            # Generamos un número aleatorio entre SALTO_MIN y SALTO_MAX
            salto = random.randint(SALTO_MIN, SALTO_MAX)
            posicion += salto
            print(f"🎲 Salto aleatorio: {salto:+d} | Nueva posición: {posicion} (LED {LEDS_PINS[posicion] if 0 <= posicion < len(leds) else 'FUERA'})")
            
            while btn_random.is_pressed:
                time.sleep(0.01)
        
        # ============================================================
        # 5. SI NO HAY NINGÚN BOTÓN PULSADO, ESPERAMOS Y REPETIMOS
        # ============================================================
        else:
            time.sleep(0.01)  # Pausa pequeña para no saturar la CPU
            continue          # Volvemos al inicio del while
        
        # ============================================================
        # 6. COMPROBAR DERROTA (después de cada movimiento)
        # ============================================================
        if comprobar_derrota(posicion):
            gestionar_derrota()
            return False  # Perdió
        
        # ============================================================
        # 7. ACTUALIZAR LEDs (encender solo la posición actual)
        # ============================================================
        actualizar_leds(posicion)
        
        # ============================================================
        # 8. COMPROBAR VICTORIA
        # ============================================================
        if comprobar_victoria(posicion):
            gestionar_victoria()
            return True  # Ganó

# ═══════════════════════════════════════════════════════════════════
# 7. PUNTO DE ENTRADA DEL PROGRAMA (donde empieza todo)
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Esta parte se ejecuta SOLO si ejecutamos este archivo directamente.
    Si importamos este archivo como módulo, NO se ejecuta.
    """
    
    print("=" * 50)
    print("=== INICIO DEL JUEGO ===")
    print("=" * 50)
    
    try:
        # Bucle infinito: juega partidas una tras otra
        while True:
            # Jugamos una partida
            resultado = jugar()
            
            # resultado puede ser:
            #   True  → Victoria
            #   False → Derrota  
            #   None  → Reset solicitado (reinicia sin mostrar mensaje)
            
            if resultado is None:
                print("🔄 Reiniciando partida...")
                time.sleep(0.5)  # Pequeña pausa antes de reiniciar
                continue  # Vuelve a empezar el bucle, nueva partida
            
            # Si llegamos aquí, la partida terminó por victoria o derrota
            print("Victoria!" if resultado else "Derrota.")
            time.sleep(1)  # Pausa antes de empezar otra partida
            
    except KeyboardInterrupt:
        # Esto ocurre cuando el usuario pulsa Ctrl+C
        print("\n\nFin del programa")