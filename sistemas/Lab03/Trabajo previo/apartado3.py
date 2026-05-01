from gpiozero import LED, Button
from signal import pause

leds = [LED(pin) for pin in range(20, 28)]
boton_suma = Button(7, pull_up=True)
boton_resta = Button(16, pull_up=True)
boton_reset = Button(17, pull_up=True)

contador = 0

def actualizar_leds():
    for i, led in enumerate(leds):
        bit = (contador >> i) & 0x1
        led.on() if bit else led.off()

def incrementar():
    global contador
    if contador < 255:
        contador += 1
    actualizar_leds()

def decrementar():
    global contador
    if contador > 0:
        contador -= 1
    actualizar_leds()

def reset():
    global contador
    contador = 0
    actualizar_leds()

boton_suma.when_pressed = incrementar
boton_resta.when_pressed = decrementar
boton_reset.when_pressed = reset
actualizar_leds()

pause()

'''
Explica esta linea de codigo: bits = [(contador >> bit) & 0x1 for bit in range(8)]

- range(8): Genera los numeros del 0 al 7, representando las posiciones de los bits
- contados >> bit: Desplaza los bits del contador hacia la derecha bit posiciones
  - Si bit = 0: no hay desplazamiento
  - Si bit = 1: desplaza un bit a derecha
- & 0x1: Aplica una mascara de tipo AND con 1 para extraer solo bit menos significativo
En resumen, crea una lista de 8 elementos donde cada elemento es 0 o 1 representando los bits del contador
'''