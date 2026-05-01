import RPi.GPIO as GPIO
from signal import pause

def main() -> None:
    GPIO.setmode(GPIO.BCM)
    # LEDs en pines GPIO20 a GPIO27
    leds_pares = [20, 22, 24, 26]
    
    for led in leds_pares:
        GPIO.setup(led, GPIO.OUT)
        GPIO.output(led, GPIO.HIGH)  # Encender LEDs pares
    
    pause()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()