# Encender LEDs pares con clase LED
from gpiozero import LED
from signal import pause

led20 = LED(20)
led22 = LED(22)
led24 = LED(24)
led26 = LED(26)

led20.on()
led22.on()
led24.on()
led26.on()

pause()