# LEDs pares solo mientras se presiona GPIO19
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
leds_pares = [20, 22, 24, 26]
for led in leds_pares:
    GPIO.setup(led, GPIO.OUT)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        estado_boton = GPIO.input(19)
        if estado_boton == GPIO.LOW:
            for led in leds_pares:
                GPIO.output(led, GPIO.HIGH)
        else:
            for led in leds_pares:
                GPIO.output(led, GPIO.LOW)
        sleep(0.05)
except KeyboardInterrupt:
    GPIO.cleanup()