#!/usr/bin/env python3
"""
EJERCICIO 2 - MODIFICACIÓN CON PWM (Intensidad de LEDs)
========================================================
ESQUELETO ADAPTABLE para el examen.

CONCEPTO: Asignar intensidades PWM a los LEDs en función de algo
          (distancia al centro, tiempo transcurrido, posición, etc.)

PINES (CAMBIAR SEGÚN ENUNCIADO):
  LEDs del tablero: 20, 21, 22, 23, 24
  Botones         : igual que ejercicio 1

IMPORTANTE: La función PWM en iMAT es:
    hat.PWMLED(pin, frequency=X, dutycycle=Y)
      - frequency : Hz  (ej. 100)
      - dutycycle : 0.0 (apagado) a 1.0 (máxima intensidad)
              ← 0.3 = 30%, 0.6 = 60%, 1.0 = 100%
"""

from imatpy import iMAT
import time
import random

# ──────────────────────────────────────────────
# 1. CONFIGURACIÓN GLOBAL  ← TOCA AQUÍ PRIMERO
# ──────────────────────────────────────────────

LEDS       = [20, 21, 22, 23, 24]   # ← Orden izquierda → derecha
LED_EXTRA  = 23                      # ← LED para PWM permanente (ej. ejercicio 4)

BTN_IZQ    = 16
BTN_DER    = 19
BTN_RANDOM = 26

# Frecuencia PWM por defecto  ← CAMBIAR si el enunciado especifica otra
FREQ_PWM = 100   # Hz

# ──────────────────────────────────────────────────────────────────────────
# 2. INTENSIDADES SEGÚN POSICIÓN RELATIVA AL CENTRO  ← ADAPTAR AL ENUNCIADO
# ──────────────────────────────────────────────────────────────────────────
#
# Distancia 0 (es el LED activo)   → 100%
# Distancia 1 (vecinos inmediatos) →  60%
# Distancia 2 (bordes)             →  20%
#
# Si el enunciado dice otra cosa, cambia este diccionario:
INTENSIDAD_POR_DISTANCIA = {
    0: 1.0,    # LED activo          → 100%
    1: 0.6,    # A 1 posición        →  60%
    2: 0.2,    # A 2 posiciones      →  20%
    # 3: 0.0  # ← Descomentar si hay más LEDs
}

hat = iMAT()

# ──────────────────────────────────────────────
# 3. FUNCIONES AUXILIARES GENERALES
# ──────────────────────────────────────────────

def boton_pulsado(btn):
    """Detecta flanco de bajada (pulsación) con anti-rebote."""
    if hat.BTN(btn) == 0:
        time.sleep(0.05)
        if hat.BTN(btn) == 0:
            while hat.BTN(btn) == 0:
                pass
            return True
    return False


def apagar_todos_pwm():
    """Pone todos los LEDs del tablero a 0% (apagado limpio con PWM)."""
    for led in LEDS:
        hat.PWMLED(led, frequency=FREQ_PWM, dutycycle=0)


# ──────────────────────────────────────────────
# 4. FUNCIONES PWM  ← NÚCLEO DEL EJERCICIO 2
# ──────────────────────────────────────────────

def aplicar_pwm_por_distancia(posicion):
    """
    CASO MÁS COMÚN: intensidad proporcional a la distancia al LED activo.
    posicion = índice del LED encendido dentro de LEDS.

    Resultado con LEDS=[20,21,22,23,24] y posicion=2 (centro):
      LED 20 → distancia 2 → 20%
      LED 21 → distancia 1 → 60%
      LED 22 → distancia 0 → 100%   ← activo
      LED 23 → distancia 1 → 60%
      LED 24 → distancia 2 → 20%
    """
    for i, led in enumerate(LEDS):
        distancia = abs(i - posicion)                           # Distancia al activo
        duty = INTENSIDAD_POR_DISTANCIA.get(distancia, 0.0)    # Busca en tabla, 0 si no existe
        hat.PWMLED(led, frequency=FREQ_PWM, dutycycle=duty)
        print(f"  LED {led} → distancia {distancia} → {duty*100:.0f}%")


def aplicar_pwm_fijo(led, duty, freq=FREQ_PWM):
    """
    Pone UN led a una intensidad fija.
    duty entre 0.0 y 1.0
    USO: aplicar_pwm_fijo(23, 0.30)  → LED 23 al 30%
    """
    hat.PWMLED(led, frequency=freq, dutycycle=duty)
    print(f"PWM LED {led}: {duty*100:.0f}% @ {freq}Hz")


def aplicar_pwm_lista(intensidades):
    """
    Aplica una lista de intensidades directamente a LEDS.
    intensidades = lista del mismo tamaño que LEDS, valores 0.0-1.0

    EJEMPLO: aplicar_pwm_lista([0.2, 0.6, 1.0, 0.6, 0.2])
    """
    assert len(intensidades) == len(LEDS), "La lista debe tener el mismo nº de elementos que LEDS"
    for led, duty in zip(LEDS, intensidades):
        hat.PWMLED(led, frequency=FREQ_PWM, dutycycle=duty)
        print(f"  LED {led} → {duty*100:.0f}%")


def pwm_proporcional_tiempo(led_pronto, led_tarde, t_antes, t_random):
    """
    CASO DEL EXAMEN ANTERIOR:
      - LED 'pronto' (pulsaste antes de tiempo): duty ∝ tiempo antes (min 0, max 1 si >1s)
      - LED 'tarde'  (tardaste más del random):  duty ∝ retraso      (min 0, max 1 si >1s)

    t_antes  = tiempo que anticipaste el botón (s)  [positivo = pulsaste antes]
    t_random = tiempo aleatorio total de la ronda    (s)

    ADAPTAR: cambia la fórmula si el enunciado lo pide de otra forma.
    """
    # ── LED pronto ──
    duty_pronto = min(t_antes / 1.0, 1.0) if t_antes > 0 else 0.0
    hat.PWMLED(led_pronto, frequency=FREQ_PWM, dutycycle=duty_pronto)
    print(f"Antes/Después: {t_antes:.2f} s → LED pronto {duty_pronto*100:.0f}%")

    # ── LED tarde ──
    retraso = t_random + 0.5   # el enunciado anterior sumaba 0.5 s al tiempo aleatorio
    duty_tarde = min(retraso / 1.0, 1.0) if retraso > 0 else 0.0
    hat.PWMLED(led_tarde, frequency=FREQ_PWM, dutycycle=duty_tarde)
    print(f"Antes/Después: {retraso:.2f} s → LED tarde  {duty_tarde*100:.0f}%")


# ──────────────────────────────────────────────
# 5. BUCLE PRINCIPAL (igual que ej.1 + PWM)
# ──────────────────────────────────────────────

def jugar():
    pos = 2       # ← Posición inicial (centro)
    apagar_todos_pwm()
    aplicar_pwm_por_distancia(pos)   # ← Estado inicial con intensidades
    print(f"Inicio: posición {pos}, LED {LEDS[pos]}")

    while True:
        if boton_pulsado(BTN_DER):
            pos = min(pos + 1, len(LEDS) - 1)    # Límite derecho
            print(f"→ Derecha | LED {LEDS[pos]}")

        elif boton_pulsado(BTN_IZQ):
            pos = max(pos - 1, 0)                 # Límite izquierdo
            print(f"← Izquierda | LED {LEDS[pos]}")

        elif boton_pulsado(BTN_RANDOM):
            salto = random.randint(-2, 2)
            pos = max(0, min(pos + salto, len(LEDS) - 1))   # Clamp al rango
            print(f"🎲 Salto {salto:+d} | LED {LEDS[pos]}")

        else:
            continue

        # Actualizar intensidades tras moverse
        aplicar_pwm_por_distancia(pos)


if __name__ == "__main__":
    print("=== EJERCICIO 2: PWM ===")
    try:
        jugar()
    except KeyboardInterrupt:
        apagar_todos_pwm()
        print("Fin.")
