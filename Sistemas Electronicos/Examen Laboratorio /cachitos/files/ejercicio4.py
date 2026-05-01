#!/usr/bin/env python3
"""
EJERCICIO 4 - PWM PERMANENTE + MEDICIÓN (OSCILOSCOPIO / POLÍMETRO)
====================================================================
ESQUELETO ADAPTABLE para el examen.

CONCEPTO: Generar una señal PWM continua en un LED mientras el juego
          corre. En el examen hay que medir con el osciloscopio/polímetro
          y anotar los valores.

PINES (CAMBIAR SEGÚN ENUNCIADO):
  LED_PWM_PERMANENTE = 23   ← LED donde se mide la señal PWM
  Frecuencia         = 2 Hz (como en el enunciado del examen anterior)
  Duty cycle         = 30%

FÓRMULAS ÚTILES PARA EL OSCILOSCOPIO:
  Periodo   T  = 1 / frecuencia         (ej: 1/2 = 0.5 s)
  t_HIGH       = T × duty_cycle         (ej: 0.5 × 0.3 = 0.15 s)
  t_LOW        = T × (1 - duty_cycle)   (ej: 0.5 × 0.7 = 0.35 s)
  V_alto (3.3 V en Raspberry Pi)
  V_medio      = V_alto × duty_cycle    (ej: 3.3 × 0.3 = 0.99 V  ← lo que mide el polímetro DC)
"""

from imatpy import iMAT
import time
import random

# ──────────────────────────────────────────────
# 1. CONFIGURACIÓN  ← TOCA AQUÍ PRIMERO
# ──────────────────────────────────────────────

LEDS             = [20, 21, 22, 23, 24]
LED_PWM_PERMANENTE = 23      # ← LED que se mide. CAMBIAR si el enunciado dice otro
FREQ_PWM_PERM    =  2        # ← Frecuencia en Hz.  CAMBIAR según enunciado
DUTY_PWM_PERM    =  0.30     # ← Duty cycle 0.0-1.0. 0.30 = 30%. CAMBIAR según enunciado

FREQ_JUEGO       = 100       # ← Frecuencia PWM para los LEDs del juego (normal)

BTN_IZQ    = 16
BTN_DER    = 19
BTN_RANDOM = 26

TIMEOUT_ACCION = 10.0        # ← Segundos de inactividad → acción automática

hat = iMAT()

# ──────────────────────────────────────────────
# 2. FUNCIONES ÚTILES
# ──────────────────────────────────────────────

def boton_pulsado(btn):
    if hat.BTN(btn) == 0:
        time.sleep(0.05)
        if hat.BTN(btn) == 0:
            while hat.BTN(btn) == 0:
                pass
            return True
    return False


def iniciar_pwm_permanente():
    """
    Arranca la señal PWM continua en LED_PWM_PERMANENTE.
    Debe llamarse UNA VEZ al inicio y no tocarse más.
    """
    hat.PWMLED(LED_PWM_PERMANENTE,
               frequency=FREQ_PWM_PERM,
               dutycycle=DUTY_PWM_PERM)
    print(f"PWM permanente: LED {LED_PWM_PERMANENTE} | "
          f"{FREQ_PWM_PERM} Hz | {DUTY_PWM_PERM*100:.0f}% duty")
    # Imprime los valores teóricos para el osciloscopio
    T = 1 / FREQ_PWM_PERM
    print(f"  → Periodo T      = {T:.3f} s")
    print(f"  → t_HIGH         = {T * DUTY_PWM_PERM:.3f} s")
    print(f"  → t_LOW          = {T * (1-DUTY_PWM_PERM):.3f} s")
    print(f"  → V_medio (DC)   ≈ {3.3 * DUTY_PWM_PERM:.2f} V  (si V_alto=3.3V)")


def actualizar_leds_juego(posicion):
    """Actualiza los LEDs del juego SIN tocar el LED_PWM_PERMANENTE."""
    for i, led in enumerate(LEDS):
        if led == LED_PWM_PERMANENTE:
            continue    # ← NO tocar el LED de medición
        hat.LED(led, i == posicion)


def aplicar_pwm_juego(posicion):
    """Aplica PWM a los LEDs del juego SIN tocar el LED_PWM_PERMANENTE."""
    tabla = {0: 1.0, 1: 0.6, 2: 0.2}
    for i, led in enumerate(LEDS):
        if led == LED_PWM_PERMANENTE:
            continue    # ← NO sobreescribir el PWM permanente
        duty = tabla.get(abs(i - posicion), 0.0)
        hat.PWMLED(led, frequency=FREQ_JUEGO, dutycycle=duty)


def comprobar_derrota(pos):
    return pos < 0 or pos >= len(LEDS)

def comprobar_victoria(pos):
    return pos == len(LEDS) - 1   # ← ADAPTAR


# ──────────────────────────────────────────────
# 3. BUCLE PRINCIPAL (igual que ej.3 + PWM permanente)
# ──────────────────────────────────────────────

def jugar():
    pos = 2
    t_ultimo = time.time()

    iniciar_pwm_permanente()     # ← Arranca PWM ANTES del bucle del juego
    actualizar_leds_juego(pos)
    # aplicar_pwm_juego(pos)     # ← Descomentar si el ej.2 y 3 también están activos

    print("Juego iniciado.")

    while True:
        ahora = time.time()

        # ── Timeout ───────────────────────────────────────
        if ahora - t_ultimo >= TIMEOUT_ACCION:
            salto = random.randint(-2, 2)
            pos  += salto
            t_ultimo = time.time()
            print(f"⏰ Salto automático {salto:+d}")

            if comprobar_derrota(pos):
                print("PERDISTE (timeout).")
                return False
            actualizar_leds_juego(pos)
            continue

        # ── Botones ───────────────────────────────────────
        if boton_pulsado(BTN_DER):
            pos += 1
            t_ultimo = time.time()
        elif boton_pulsado(BTN_IZQ):
            pos -= 1
            t_ultimo = time.time()
        elif boton_pulsado(BTN_RANDOM):
            pos += random.randint(-2, 2)
            t_ultimo = time.time()
        else:
            time.sleep(0.01)
            continue

        if comprobar_derrota(pos):
            print("PERDISTE.")
            return False

        actualizar_leds_juego(pos)
        # aplicar_pwm_juego(pos)   # ← Descomentar si hay PWM en los LEDs del juego

        if comprobar_victoria(pos):
            print("¡GANASTE!")
            return True


# ──────────────────────────────────────────────
# 4. HOJA DE REFERENCIA PARA EL OSCILOSCOPIO
# ──────────────────────────────────────────────
"""
MEDICIONES A MOSTRAR AL PROFESOR (las más habituales):

  1. Amplitud (V_pp)        → pico a pico de la señal PWM (≈ 3.3 V en RPi)
  2. Periodo (T)            → duración de un ciclo completo (T = 1/f)
  3. Frecuencia (f)         → pulsar el botón de medida en el osci
  4. Duty cycle (%)         → t_HIGH / T × 100
  5. Tensión media (V_DC)   → medir con polímetro en DC = V_alto × duty
  6. t_HIGH / t_LOW         → cambiar duty cycle y mostrar cómo varía

CÓMO CAMBIAR DUTY CYCLE EN VIVO (para mostrar al profesor):
"""

def cambiar_duty(nuevo_duty):
    """
    Cambia el duty cycle del PWM permanente en caliente.
    nuevo_duty: 0.0 a 1.0
    EJEMPLO: cambiar_duty(0.5) → 50%
    """
    hat.PWMLED(LED_PWM_PERMANENTE,
               frequency=FREQ_PWM_PERM,
               dutycycle=nuevo_duty)
    T = 1 / FREQ_PWM_PERM
    print(f"Duty cambiado a {nuevo_duty*100:.0f}%")
    print(f"  t_HIGH = {T*nuevo_duty:.3f} s | t_LOW = {T*(1-nuevo_duty):.3f} s")
    print(f"  V_medio ≈ {3.3*nuevo_duty:.2f} V")


def cambiar_frecuencia(nueva_freq):
    """
    Cambia la frecuencia del PWM permanente en caliente.
    EJEMPLO: cambiar_frecuencia(5) → 5 Hz
    """
    hat.PWMLED(LED_PWM_PERMANENTE,
               frequency=nueva_freq,
               dutycycle=DUTY_PWM_PERM)
    print(f"Frecuencia cambiada a {nueva_freq} Hz | T = {1/nueva_freq:.3f} s")


# ──────────────────────────────────────────────
# PUNTO DE ENTRADA
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=== EJERCICIO 4: PWM PERMANENTE + MEDICIÓN ===")
    try:
        while True:
            resultado = jugar()
            print("Resultado:", "Victoria" if resultado else "Derrota")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Fin.")
