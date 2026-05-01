# LEDs pares solo con botón GPIO19 (LED y Button)
from gpiozero import LED, Button
from signal import pause

leds_pares = [LED(20), LED(22), LED(24), LED(26)]
boton = Button(19, pull_up=True)

def presionar():
    for led in leds_pares:
        led.on()

def soltar():
    for led in leds_pares:
        led.off()

boton.when_pressed = presionar
boton.when_released = soltar
pause()