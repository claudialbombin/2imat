# Botón GPIO14 alterna LEDs impares (con variables)
from gpiozero import LED, Button
from signal import pause

leds_pares = [LED(20), LED(22), LED(24), LED(26)]
leds_impares = [LED(21), LED(23), LED(25), LED(27)]
boton19 = Button(19, pull_up=True)
boton14 = Button(14, pull_up=True)

impares_encendidos = False
boton14_anterior = False

def control_boton19():
    if boton19.is_pressed:
        for led in leds_pares:
            led.on()
    else:
        for led in leds_pares:
            led.off()

def cuando_presiona_boton19():
    for led in leds_pares:
        led.on()

def cuando_suelta_boton19():
    for led in leds_pares:
        led.off()

def cuando_presiona_boton14():
    global impares_encendidos
    impares_encendidos = not impares_encendidos
    for led in leds_impares:
        led.on() if impares_encendidos else led.off()

# Conectar eventos a los botones
boton19.when_pressed = cuando_presiona_boton19
boton19.when_released = cuando_suelta_boton19
boton14.when_pressed = cuando_presiona_boton14

try:
    pause()
except KeyboardInterrupt:
    for led in leds_pares + leds_impares:
        led.off()