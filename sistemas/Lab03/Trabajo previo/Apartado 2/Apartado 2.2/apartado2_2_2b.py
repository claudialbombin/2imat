# Con LEDBoard
from gpiozero import LEDBoard, Button
from signal import pause

leds = LEDBoard(20, 22, 24, 26)
boton = Button(19, pull_up=True)

def presionar():
    leds.on()

def soltar():
    leds.off()

boton.when_pressed = presionar
boton.when_released = soltar
pause()