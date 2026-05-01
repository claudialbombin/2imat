#Importamos
from gpiozero import PWMLED 
from gpiozero import Button
import time 
leds_pwm = [
    PWMLED(24, frequency = 100),
    PWMLED(25, frequency = 100),
    PWMLED(26, frequency = 100),
    PWMLED(27, frequency = 100)
]
# Botones
btn_jugador = Button(16)   # Mover derecha (+1)
btn_iniciar = Button(20) 
btn_perseguidor = Button(19)  

# Constantes de posición
POS_INICIAL = 2  # Índice 2 = GPIO26
LIMITE_IZQ = 0   # Índice 0 = GPIO20
LIMITE_DER = 4   # Índice 4 = GPIO24

# Variables de juego
posicion_actual = POS_INICIAL
posicion_actual_p = 0
juego_activo = False
gana_m = 0
pasos_por_led26 = 0  # Contador de veces que pasa por LED 26

# Variables para tiempo de inactividad (ejercicio 3)
TIEMPO_MAX_INACTIVIDAD = 4.0  # segundos
ultima_pulsacion = time.time()
INTENSIDADES = [1, 1, 1, 1]

# Variables para detección de pulsación larga de reinicio
tiempo_pulsacion_izquierda = 0
TIEMPO_REINICIO = 2.0  # segundos necesarios para reiniciar

# Detección de flanco para botones
ant_jug = btn_jugador.is_pressed
ant_iniciar = btn_iniciar.is_pressed
ant_perseguidor = btn_perseguidor.is_pressed

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
    # Primero apagamos todos
    for led in leds_pwm:
        led.off()
    
    # Encendemos los LEDs de ambos personajes
    leds_pwm[posicion_actual].value = INTENSIDADES[posicion_actual]
    leds_pwm[posicion_actual_p].value = INTENSIDADES[posicion_actual_p]

def reiniciar_juego():
    """Reinicia el juego a su estado inicial"""
    global posicion_actual_p, posicion_actual, juego_activo, pasos_por_led26, gana_m
    posicion_actual = POS_INICIAL
    posicion_actual_p = 0
    juego_activo = True
    
    # Verificar si el jugador ha ganado
    if pasos_por_led26 >= 3:
        print("🏆 ¡JUGADOR GANA! Pasó 3 veces por LED 26")
        gana_m += 1
        pasos_por_led26 = 0
        juego_activo = False
    else:
        actualizar_personaje()
        print("🔄 Juego reiniciado")

def mover_derecha():
    """Mueve el personaje a la derecha (+1)"""
    global posicion_actual, juego_activo, ultima_pulsacion, pasos_por_led26
    if not juego_activo:
        return
    print("Mover derecha")
    
    nueva_pos = posicion_actual + 1
    if nueva_pos >= 4:
        nueva_pos = 0
    else:
        posicion_actual = nueva_pos
    
    # Verificar si pasó por LED 26 (posición 2)
    if posicion_actual == 2:
        pasos_por_led26 += 1
        print(f"✅ Paso {pasos_por_led26}/3 por LED 26")
    
    actualizar_personaje()
    print(f"Posición: GPIO{24+posicion_actual}")

def mover_derecha_p():
    """Mueve el personaje perseguidor a la derecha (+1)"""
    global posicion_actual_p, juego_activo, ultima_pulsacion
    if not juego_activo:
        return
    print("Mover derecha_p")
    
    nueva_pos = posicion_actual_p + 1
    if nueva_pos >= 4:
        nueva_pos = 0
    else:
        posicion_actual_p = nueva_pos
    
    actualizar_personaje()
    print(f"Posición perseguidor: GPIO{24+posicion_actual_p}")

# ============================================================
# BUCLE PRINCIPAL
# ============================================================

# Estado inicial
aplicar_intensidades()
actualizar_personaje()
print("🎮 Juego iniciado - Personaje en posición central (GPIO26)")
print("Objetivo: Pasar 3 veces por LED 26 para ganar")
print("  GPIO16: jugador (+1)")
print("  GPIO20: iniciar")
print("  GPIO19: perseguidor")

try:
    while True:
        juego_activo = True
        
        # Botón jugador
        act_jugador = btn_jugador.is_pressed
        if act_jugador and juego_activo:
            print('pulso1')
            mover_derecha()
            act_jugador = btn_jugador.is_pressed
        
        # Botón iniciar (reinicio)
        act_iniciar = btn_iniciar.is_pressed
        if act_iniciar and juego_activo:
            reiniciar_juego()
            juego_activo = False
            act_iniciar = btn_iniciar.is_pressed
        ant_iniciar = act_iniciar

        # Botón perseguidor
        act_perseguidor = btn_perseguidor.is_pressed
        if act_perseguidor and juego_activo:
            print('pulso2')
            mover_derecha_p()
        ant_perseguidor = act_perseguidor

        # Verificar colisión
        if posicion_actual == posicion_actual_p:
            print('💥 Te han pillado')
            posicion_actual = POS_INICIAL
            posicion_actual_p = 0   
            pasos_por_led26 = 0  # Reiniciar contador al ser atrapado
            reiniciar_juego()
        
        # Verificar victoria del jugador
        if pasos_por_led26 >= 3:
            reiniciar_juego()
                
except KeyboardInterrupt:
    print("\nPrograma terminado")
finally:
    for led in leds_pwm:
        led.off()