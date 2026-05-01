# Botón externo en GPIO14 alterna LEDs impares
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
for pin in range(20, 28):
    GPIO.setup(pin, GPIO.OUT)

GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_UP)

leds_impares_estado = False
boton14_anterior = GPIO.HIGH

try:
    while True:
        # Control botón GPIO19 (nivel)
        if GPIO.input(19) == GPIO.LOW:
            for pin in [20, 22, 24, 26]:
                GPIO.output(pin, GPIO.HIGH)
        else:
            for pin in [20, 22, 24, 26]:
                GPIO.output(pin, GPIO.LOW)
        
        # Control botón GPIO14 (flanco)
        boton14_actual = GPIO.input(14)
        if boton14_anterior == GPIO.HIGH and boton14_actual == GPIO.LOW:
            leds_impares_estado = not leds_impares_estado
            for pin in [21, 23, 25, 27]:
                GPIO.output(pin, GPIO.HIGH if leds_impares_estado else GPIO.LOW)
        
        boton14_anterior = boton14_actual
        sleep(0.05)
except KeyboardInterrupt:
    GPIO.cleanup() 