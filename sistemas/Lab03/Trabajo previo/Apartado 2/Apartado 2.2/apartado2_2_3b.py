# Con callbacks y lambda
from gpiozero import LED, Button
from signal import pause

leds_pares = [LED(20), LED(22), LED(24), LED(26)]
leds_impares = [LED(21), LED(23), LED(25), LED(27)]
boton19 = Button(19, pull_up=True)
boton14 = Button(14, pull_up=True)

impares_encendidos = False

def encender_pares():
    for led in leds_pares:
        led.on()

def apagar_pares():
    for led in leds_pares:
        led.off()

def alternar_impares():
    global impares_encendidos
    impares_encendidos = not impares_encendidos
    for led in leds_impares:
        led.on() if impares_encendidos else led.off()

boton19.when_pressed = encender_pares
boton19.when_released = apagar_pares
boton14.when_pressed = alternar_impares

pause()