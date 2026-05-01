#!/usr/bin/env python3
"""
EJERCICIO 3 - AUTOMATIZACIÓN CON TEMPORIZADOR
==============================================
ESQUELETO ADAPTABLE para el examen.

CONCEPTO: Si pasa X segundos sin que el jugador haga algo,
          se ejecuta una acción automática (salto random, nueva ronda, etc.)

DOS APROXIMACIONES INCLUIDAS:
  A) Sin threading  → bucle principal revisa el tiempo (más simple, recomendada)
  B) Con threading  → hilo separado ejecuta la acción (más robusta)

PINES (CAMBIAR SEGÚN ENUNCIADO):
  Igual que ejercicios anteriores.
"""

from imatpy import iMAT
import time
import random
import threading   # Solo necesario si usas la opción B

# ──────────────────────────────────────────────
# 1. CONFIGURACIÓN GLOBAL  ← TOCA AQUÍ PRIMERO
# ──────────────────────────────────────────────

LEDS       = [20, 21, 22, 23, 24]
BTN_IZQ    = 16
BTN_DER    = 19
BTN_RANDOM = 26

FREQ_PWM   = 100    # Hz (para PWM)

# ── Temporizador ──
TIMEOUT_ACCION = 4.0    # ← CAMBIAR: segundos de inactividad antes de acción automática
                         #   (en el examen anterior eran 4 s → salto random)
                         #   (en el examen del enunciado eran 10 s → nueva ronda)

SALTO_MIN = -2           # ← Rango del salto automático
SALTO_MAX =  2

hat = iMAT()

# ──────────────────────────────────────────────
# 2. FUNCIONES AUXILIARES
# ──────────────────────────────────────────────

def boton_pulsado(btn):
    """Detecta pulsación con anti-rebote."""
    if hat.BTN(btn) == 0:
        time.sleep(0.05)
        if hat.BTN(btn) == 0:
            while hat.BTN(btn) == 0:
                pass
            return True
    return False


def actualizar_leds(posicion):
    """Enciende solo el LED de la posición actual."""
    for i, led in enumerate(LEDS):
        hat.LED(led, i == posicion)


def aplicar_pwm_por_distancia(posicion, freq=FREQ_PWM):
    """Intensidad proporcional a la distancia al LED activo."""
    tabla = {0: 1.0, 1: 0.6, 2: 0.2}    # ← CAMBIAR intensidades si es necesario
    for i, led in enumerate(LEDS):
        duty = tabla.get(abs(i - posicion), 0.0)
        hat.PWMLED(led, frequency=freq, dutycycle=duty)


def accion_automatica(posicion):
    """
    ACCIÓN QUE SE EJECUTA AUTOMÁTICAMENTE al superar el timeout.
    ← ADAPTAR AL ENUNCIADO:
      - Salto aleatorio (ejemplo anterior)
      - Iniciar nueva ronda
      - Mover al personaje un paso fijo
      - etc.
    """
    salto = random.randint(SALTO_MIN, SALTO_MAX)
    nueva_pos = posicion + salto
    print(f"⏰ TIMEOUT: salto automático {salto:+d}")
    return nueva_pos    # Devuelve la nueva posición (puede estar fuera del rango → derrota)


def comprobar_derrota(posicion):
    """Fuera del tablero → derrota."""
    return posicion < 0 or posicion >= len(LEDS)


def comprobar_victoria(posicion):
    """← ADAPTAR AL ENUNCIADO."""
    return posicion == len(LEDS) - 1   # Ejemplo: llegar al extremo derecho


# ══════════════════════════════════════════════
# OPCIÓN A: SIN THREADING (recomendada en examen)
# ══════════════════════════════════════════════
"""
CÓMO FUNCIONA:
  - Guardamos el tiempo del último movimiento (t_ultimo_movimiento).
  - En cada iteración del bucle comprobamos cuánto ha pasado.
  - Si supera TIMEOUT_ACCION → ejecutamos accion_automatica().
  - Si se pulsa un botón → reseteamos el temporizador.
"""

def jugar_sin_threading():
    pos = 2                                  # Posición inicial
    t_ultimo_movimiento = time.time()        # ← Temporizador: marca el tiempo de inicio

    actualizar_leds(pos)
    # aplicar_pwm_por_distancia(pos)         # ← Descomentar si hay PWM (ej. 2+3 combinados)
    print("Juego iniciado. Tienes", TIMEOUT_ACCION, "s para moverte.")

    while True:
        ahora = time.time()
        tiempo_inactivo = ahora - t_ultimo_movimiento   # Segundos sin pulsar nada

        # ── Comprobar timeout ─────────────────────────────────────────────
        if tiempo_inactivo >= TIMEOUT_ACCION:
            pos = accion_automatica(pos)
            t_ultimo_movimiento = time.time()            # ← Resetea el temporizador

            if comprobar_derrota(pos):
                print("PERDISTE (salto automático fuera de rango).")
                return False
            actualizar_leds(pos)
            # aplicar_pwm_por_distancia(pos)             # ← Descomentar si hay PWM
            continue

        # ── Botón DERECHA ─────────────────────────────────────────────────
        if boton_pulsado(BTN_DER):
            pos += 1
            t_ultimo_movimiento = time.time()            # ← Resetea el temporizador
            print(f"→ Derecha | LED {LEDS[pos] if 0 <= pos < len(LEDS) else 'FUERA'}")

        # ── Botón IZQUIERDA ───────────────────────────────────────────────
        elif boton_pulsado(BTN_IZQ):
            pos -= 1
            t_ultimo_movimiento = time.time()            # ← Resetea el temporizador
            print(f"← Izquierda | LED {LEDS[pos] if 0 <= pos < len(LEDS) else 'FUERA'}")

        # ── Botón RANDOM ──────────────────────────────────────────────────
        elif boton_pulsado(BTN_RANDOM):
            salto = random.randint(SALTO_MIN, SALTO_MAX)
            pos += salto
            t_ultimo_movimiento = time.time()            # ← Resetea el temporizador
            print(f"🎲 Salto manual {salto:+d}")

        else:
            time.sleep(0.01)   # Pequeña pausa anti-CPU
            continue           # Ningún botón → volvemos al inicio del while

        # ── Comprobar derrota ─────────────────────────────────────────────
        if comprobar_derrota(pos):
            print("PERDISTE.")
            return False

        # ── Actualizar visualización ──────────────────────────────────────
        actualizar_leds(pos)
        # aplicar_pwm_por_distancia(pos)     # ← Descomentar si hay PWM

        # ── Comprobar victoria ────────────────────────────────────────────
        if comprobar_victoria(pos):
            print("¡GANASTE!")
            return True


# ══════════════════════════════════════════════
# OPCIÓN B: CON THREADING (más avanzada)
# ══════════════════════════════════════════════
"""
CÓMO FUNCIONA:
  - Un hilo secundario duerme TIMEOUT_ACCION segundos.
  - Si nadie lo cancela antes, ejecuta accion_automatica().
  - Cada vez que se pulsa un botón, se cancela y relanza el hilo.
"""

class Temporizador:
    """Temporizador cancelable que lanza una función tras X segundos."""

    def __init__(self, segundos, funcion, *args):
        self.segundos = segundos
        self.funcion  = funcion
        self.args     = args
        self._hilo    = None

    def iniciar(self):
        """Arranca (o reinicia) el temporizador."""
        self.cancelar()
        self._hilo = threading.Timer(self.segundos, self.funcion, self.args)
        self._hilo.daemon = True
        self._hilo.start()

    def cancelar(self):
        """Cancela el temporizador (si estaba corriendo)."""
        if self._hilo is not None:
            self._hilo.cancel()


# Estado compartido entre hilos (usa lock si la variable se escribe desde dos sitios)
estado = {"pos": 2, "en_juego": True}
lock   = threading.Lock()


def accion_auto_threading():
    """Versión para threading: modifica 'estado' directamente."""
    salto = random.randint(SALTO_MIN, SALTO_MAX)
    with lock:
        estado["pos"] += salto
    print(f"⏰ TIMEOUT (threading): salto {salto:+d}")
    if comprobar_derrota(estado["pos"]):
        with lock:
            estado["en_juego"] = False
        print("PERDISTE (timeout).")
    else:
        actualizar_leds(estado["pos"])
    # Relanza el temporizador para el siguiente ciclo
    timer.iniciar()


# Creamos el objeto temporizador (aún no arranca)
timer = Temporizador(TIMEOUT_ACCION, accion_auto_threading)


def jugar_con_threading():
    estado["pos"]      = 2
    estado["en_juego"] = True
    actualizar_leds(estado["pos"])
    timer.iniciar()    # ← Arranca el temporizador

    while estado["en_juego"]:
        if boton_pulsado(BTN_DER):
            timer.iniciar()              # ← Reinicia temporizador al pulsar
            with lock:
                estado["pos"] += 1
            print(f"→ Derecha")

        elif boton_pulsado(BTN_IZQ):
            timer.iniciar()
            with lock:
                estado["pos"] -= 1
            print(f"← Izquierda")

        elif boton_pulsado(BTN_RANDOM):
            timer.iniciar()
            salto = random.randint(SALTO_MIN, SALTO_MAX)
            with lock:
                estado["pos"] += salto
            print(f"🎲 Salto manual {salto:+d}")

        else:
            time.sleep(0.01)
            continue

        if comprobar_derrota(estado["pos"]):
            timer.cancelar()
            print("PERDISTE.")
            estado["en_juego"] = False
            break

        actualizar_leds(estado["pos"])

        if comprobar_victoria(estado["pos"]):
            timer.cancelar()
            print("¡GANASTE!")
            estado["en_juego"] = False


# ──────────────────────────────────────────────
# PUNTO DE ENTRADA  ← Elige qué opción usar
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=== EJERCICIO 3: AUTOMATIZACIÓN ===")
    print(f"Timeout de inactividad: {TIMEOUT_ACCION} s")

    # ← DESCOMENTA la opción que quieras usar:
    jugar_sin_threading()   # Opción A (recomendada, más sencilla)
    # jugar_con_threading() # Opción B (con hilos)
