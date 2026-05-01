#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║         SNIPPETS - COPIA Y PEGA LO QUE NECESITES            ║
║   Cada bloque es independiente y está listo para usar        ║
╚══════════════════════════════════════════════════════════════╝
"""

from imatpy import iMAT
import time, random, threading

hat = iMAT()

# ════════════════════════════════════════════════════
# ① DETECCIÓN DE BOTONES
# ════════════════════════════════════════════════════

# ── Sin función (inline) ──────────────────────────────────────
BTN = 16
if hat.BTN(BTN) == 0:          # ← botón activo a nivel bajo
    time.sleep(0.05)            # anti-rebote
    if hat.BTN(BTN) == 0:
        while hat.BTN(BTN) == 0:
            pass                # espera a que se suelte
        print("Botón pulsado (inline)")

# ── Con función ───────────────────────────────────────────────
def boton_pulsado(btn):
    """True en flanco de bajada."""
    if hat.BTN(btn) == 0:
        time.sleep(0.05)
        if hat.BTN(btn) == 0:
            while hat.BTN(btn) == 0:
                pass
            return True
    return False

# ── Esperar botón con/sin timeout ────────────────────────────
def esperar_boton(btn, timeout=None):
    """True si pulsado antes del timeout, False si tiempo agotado."""
    t0 = time.time()
    while True:
        if boton_pulsado(btn):
            return True
        if timeout and (time.time() - t0) > timeout:
            return False
        time.sleep(0.01)

# EJEMPLO: if esperar_boton(19, timeout=3): print("pulsado a tiempo")


# ════════════════════════════════════════════════════
# ② CONTROL DE LEDs (ON/OFF)
# ════════════════════════════════════════════════════

LEDS = [20, 21, 22, 23, 24]   # lista de pines

# ── Encender solo uno ────────────────────────────────────────
def encender_led(posicion):
    for i, led in enumerate(LEDS):
        hat.LED(led, i == posicion)   # True solo si i == posición

# ── Encender/apagar uno concreto ─────────────────────────────
hat.LED(22, True)    # enciende
hat.LED(22, False)   # apaga

# ── Apagar todos ─────────────────────────────────────────────
for led in LEDS:
    hat.LED(led, False)

# ── Parpadear un LED N veces ─────────────────────────────────
def parpadear(led, veces=3, pausa=0.3):
    for _ in range(veces):
        hat.LED(led, True);  time.sleep(pausa)
        hat.LED(led, False); time.sleep(pausa)

# ── Contador binario en dos LEDs (bits 1 y 0) ────────────────
def mostrar_contador_binario(valor, led_bit1=24, led_bit0=25):
    """Muestra valor (0-3) en dos LEDs como bits."""
    hat.LED(led_bit1, bool(valor & 0b10))   # bit 1
    hat.LED(led_bit0, bool(valor & 0b01))   # bit 0


# ════════════════════════════════════════════════════
# ③ CONTROL PWM
# ════════════════════════════════════════════════════

# ── Poner un LED a X% ────────────────────────────────────────
hat.PWMLED(23, frequency=100, dutycycle=0.30)   # 30%
hat.PWMLED(23, frequency=100, dutycycle=0.60)   # 60%
hat.PWMLED(23, frequency=100, dutycycle=1.00)   # 100%
hat.PWMLED(23, frequency=100, dutycycle=0.00)   # apagado

# ── Intensidades por distancia al centro ─────────────────────
def pwm_distancia(posicion, freq=100):
    tabla = {0: 1.0, 1: 0.6, 2: 0.2}   # ← CAMBIAR intensidades
    for i, led in enumerate(LEDS):
        duty = tabla.get(abs(i - posicion), 0.0)
        hat.PWMLED(led, frequency=freq, dutycycle=duty)

# ── Intensidades fijas en lista ──────────────────────────────
intensidades = [0.2, 0.6, 1.0, 0.6, 0.2]   # ← CAMBIAR
for led, duty in zip(LEDS, intensidades):
    hat.PWMLED(led, frequency=100, dutycycle=duty)

# ── PWM proporcional a tiempo (examen anterior) ──────────────
def pwm_tiempo(led_pronto, led_tarde, t_antes, t_random):
    duty_p = min(t_antes / 1.0, 1.0) if t_antes > 0 else 0.0
    hat.PWMLED(led_pronto, frequency=100, dutycycle=duty_p)
    retraso = t_random + 0.5
    duty_t  = min(retraso / 1.0, 1.0) if retraso > 0 else 0.0
    hat.PWMLED(led_tarde, frequency=100, dutycycle=duty_t)
    print(f"Pronto: {duty_p*100:.0f}%  |  Tarde: {duty_t*100:.0f}%")

# ── PWM permanente (ej.4) ────────────────────────────────────
def iniciar_pwm_permanente(led=23, freq=2, duty=0.30):
    hat.PWMLED(led, frequency=freq, dutycycle=duty)
    T = 1/freq
    print(f"PWM {led}: {freq}Hz, {duty*100:.0f}%  |  T={T:.3f}s  t_HIGH={T*duty:.3f}s  V≈{3.3*duty:.2f}V")


# ════════════════════════════════════════════════════
# ④ MOVIMIENTO Y POSICIÓN
# ════════════════════════════════════════════════════

pos = 2   # posición actual (índice en LEDS)

# ── Mover derecha (con límite) ───────────────────────────────
pos = min(pos + 1, len(LEDS) - 1)

# ── Mover izquierda (con límite) ─────────────────────────────
pos = max(pos - 1, 0)

# ── Mover derecha SIN límite (puede salirse → derrota) ───────
pos += 1

# ── Salto aleatorio ──────────────────────────────────────────
salto = random.randint(-2, 2)   # ← CAMBIAR rango
pos  += salto
print(f"Salto aleatorio: {salto:+d} → posición {pos}")

# ── Salto aleatorio con clamp (no se sale del rango) ─────────
pos = max(0, min(pos + random.randint(-2, 2), len(LEDS) - 1))

# ── Teleportar a posición concreta ───────────────────────────
pos = 0   # extremo izquierdo
pos = len(LEDS) - 1   # extremo derecho
pos = len(LEDS) // 2  # centro


# ════════════════════════════════════════════════════
# ⑤ TEMPORIZADORES
# ════════════════════════════════════════════════════

# ── Medir tiempo transcurrido ────────────────────────────────
t_inicio = time.time()
# ... código ...
transcurrido = time.time() - t_inicio
print(f"Han pasado {transcurrido:.2f} s")

# ── Esperar X segundos (bloqueante) ──────────────────────────
time.sleep(2.5)   # espera 2.5 s

# ── Timeout en bucle (no bloqueante) ─────────────────────────
TIMEOUT = 4.0
t_reset = time.time()   # ← se resetea cada vez que hay actividad

# Dentro del bucle:
if time.time() - t_reset >= TIMEOUT:
    print("Timeout alcanzado")
    t_reset = time.time()   # ← resetear para el siguiente ciclo
    # acción automática aquí

# ── Tiempo aleatorio y espera ─────────────────────────────────
t_random = random.randint(2, 5)   # ← CAMBIAR rango
print(f"Prepárate! tienes {t_random} s")
time.sleep(t_random)
# aquí: encender LED semáforo, medir tiempo de reacción...

# ── Medir tiempo de reacción ─────────────────────────────────
t_semaforo = time.time()
esperar_boton(19)                          # bloquea hasta que pulsen
reaccion = time.time() - t_semaforo
print(f"Tiempo de reacción: {reaccion:.3f} s")
gano = reaccion < 0.5                      # ← CAMBIAR umbral


# ════════════════════════════════════════════════════
# ⑥ CONDICIONES DE VICTORIA Y DERROTA
# ════════════════════════════════════════════════════

# ── Victoria: llegar al extremo ──────────────────────────────
def victoria_extremo(pos):
    return pos == len(LEDS) - 1   # llega al extremo derecho

# ── Victoria: pasar N veces por un punto ─────────────────────
veces_en_meta = 0
META = len(LEDS) - 1   # ← posición objetivo
N_VICTORIAS = 3        # ← cuántas veces hay que pasar

def victoria_n_veces(pos):
    global veces_en_meta
    if pos == META:
        veces_en_meta += 1
        print(f"Pasaste por meta {veces_en_meta}/{N_VICTORIAS} veces")
    return veces_en_meta >= N_VICTORIAS

# ── Derrota: salirse del rango ───────────────────────────────
def derrota_fuera(pos):
    return pos < 0 or pos >= len(LEDS)

# ── Derrota: colisión con perseguidor ────────────────────────
pos_jugador    = 2
pos_perseguidor = 0

def derrota_colision():
    return pos_jugador == pos_perseguidor

# ── Derrota: tiempo agotado ──────────────────────────────────
def derrota_timeout(t_inicio, limite=30):
    return (time.time() - t_inicio) >= limite

# ── Gestionar victoria ───────────────────────────────────────
def gestionar_victoria(led_ok=21, contador=None):
    hat.LED(led_ok, True)
    if contador is not None:
        contador = min(contador + 1, 3)   # máximo 3
        print(f"Ganó: {contador}")
    return contador

# ── Gestionar derrota ────────────────────────────────────────
def gestionar_derrota(led_ok=21, contador=None):
    hat.LED(led_ok, False)
    if contador is not None:
        contador = max(contador - 1, 0)   # mínimo 0
        print(f"Falló: {contador}")
    return contador


# ════════════════════════════════════════════════════
# ⑦ PERSEGUIDOR AUTOMÁTICO (bonus)
# ════════════════════════════════════════════════════

pos_jugador     = 2
pos_perseguidor = 0
LED_PERSEGUIDOR = None   # ← Si hay un LED extra para el perseguidor

def mover_perseguidor():
    """El perseguidor se acerca un paso al jugador."""
    global pos_perseguidor
    if pos_perseguidor < pos_jugador:
        pos_perseguidor += 1
    elif pos_perseguidor > pos_jugador:
        pos_perseguidor -= 1
    # Si son iguales → colisión → derrota
    print(f"Perseguidor → posición {pos_perseguidor}")


# ════════════════════════════════════════════════════
# ⑧ CONTADOR DE PUNTUACIÓN (examen anterior: LEDs 24-25)
# ════════════════════════════════════════════════════

contador = 0
LED_BIT1 = 24   # bit 1 (valor 2)
LED_BIT0 = 25   # bit 0 (valor 1)

def actualizar_contador(delta):
    """Suma delta al contador (clamp 0-3) y actualiza los LEDs."""
    global contador
    contador = max(0, min(contador + delta, 3))
    hat.LED(LED_BIT1, bool(contador & 0b10))
    hat.LED(LED_BIT0, bool(contador & 0b01))
    print(f"Contador: {contador}")


# ════════════════════════════════════════════════════
# ⑨ THREADING - TEMPORIZADOR CANCELABLE
# ════════════════════════════════════════════════════

class Temporizador:
    def __init__(self, seg, func, *args):
        self.seg  = seg
        self.func = func
        self.args = args
        self._t   = None

    def iniciar(self):
        self.cancelar()
        self._t = threading.Timer(self.seg, self.func, self.args)
        self._t.daemon = True
        self._t.start()

    def cancelar(self):
        if self._t:
            self._t.cancel()

# USO:
# def accion(): print("timeout!")
# t = Temporizador(4.0, accion)
# t.iniciar()          # arranca
# t.iniciar()          # reinicia (cancela el anterior)
# t.cancelar()         # cancela


# ════════════════════════════════════════════════════
# ⑩ HOJA DE FÓRMULAS OSCILOSCOPIO / POLÍMETRO
# ════════════════════════════════════════════════════
"""
FÓRMULAS CLAVE:
  f   = frecuencia (Hz)
  T   = 1 / f                           Periodo (s)
  D   = duty cycle (ej: 0.30)
  t_H = T × D                           Tiempo en alto (s)
  t_L = T × (1 - D)                     Tiempo en bajo (s)
  V+  = 3.3 V  (Raspberry Pi GPIO)
  Vdc = V+ × D                          Tensión media (DC)

EJEMPLO con f=2 Hz, D=30%:
  T   = 0.500 s
  t_H = 0.150 s
  t_L = 0.350 s
  Vdc = 3.3 × 0.30 = 0.99 V

CAMBIOS QUE PUEDES MOSTRAR AL PROFESOR:
  hat.PWMLED(23, frequency=2, dutycycle=0.50)  → Vdc = 1.65 V
  hat.PWMLED(23, frequency=2, dutycycle=0.80)  → Vdc = 2.64 V
  hat.PWMLED(23, frequency=5, dutycycle=0.30)  → T = 0.2 s (mismo duty, más rápido)
"""
