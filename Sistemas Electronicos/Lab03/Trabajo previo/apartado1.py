import RPi.GPIO as GPIO
from signal import pause


# Pin 20 como salida para el LED
def main() -> None:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(20, GPIO.OUT)  # GPIO20 como salida
    GPIO.output(20, GPIO.HIGH)  # Encender LED
    pause()  # Mantiene el programa en ejecución

# Pin 20 como entrada para el LED
# def main() -> None:
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(20, GPIO.IN)  # GPIO20 como entrada
#     GPIO.output(20, GPIO.HIGH)  # Encender LED
#     pause()  # Mantiene el programa en ejecución

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("\rFin del programa")
        
        
'''
Que hace el programa?
Configura el pin GPIO 20 de la Raspberry Pi como una salida y enciende un LED conectado a ese pin. El programa permanece en ejecución hasta que se interrumpe manualmente (por ejemplo, con Ctrl+C).

Configure GPIO20 como entrada. Que sucede? Es coherente?
Si se cambia el OUT por IN, el programa intenta escribir en un pin configurado como entrada,
lo que causa un error/comportamiento indefinido.
No es coherente porque un pin configurado como entrada no puede ser controlado con GPIO.output()
'''