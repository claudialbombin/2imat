import RPi.GPIO as GPIO
from time import sleep
import signal
import sys

# Desactivar warnings
GPIO.setwarnings(False)

# Limpiar configuraciones previas
GPIO.cleanup()

# Configurar modo
GPIO.setmode(GPIO.BCM)

# Configurar LEDs
leds = [20, 21, 22, 23, 24, 25, 26, 27]
for led in leds:
    GPIO.setup(led, GPIO.OUT)
    GPIO.output(led, GPIO.LOW)  # Asegurar que empiezan apagados

# Configurar botón
BOTON_PIN = 19
GPIO.setup(BOTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

contador = 0

def evento_boton(channel):
    """Callback para cuando cambia el estado del botón"""
    global contador
    
    # Esperar un poco para estabilizar (debounce software)
    sleep(0.01)
    
    # Leer estado actual del botón
    estado = GPIO.input(BOTON_PIN)
    
    if estado == GPIO.LOW:  # Botón presionado
        contador += 1
        if contador > 255:  # Límite para 8 bits
            contador = 0
        print(f"Botón presionado. Contador: {contador} (binario: {bin(contador)[2:].zfill(8)})")
        
        # Mostrar contador en binario
        for i, led in enumerate(leds):
            bit = (contador >> i) & 0x1
            GPIO.output(led, GPIO.HIGH if bit else GPIO.LOW)

def limpiar_y_salir(signum, frame):
    """Función para limpiar GPIO al salir"""
    print("\nLimpiando GPIO y saliendo...")
    GPIO.cleanup()
    sys.exit(0)

# Registrar manejador de señal para Ctrl+C
signal.signal(signal.SIGINT, limpiar_y_salir)

# Registrar evento para flanco de bajada (solo presionar)
try:
    GPIO.add_event_detect(BOTON_PIN, GPIO.FALLING, 
                         callback=evento_boton, bouncetime=300)
except RuntimeError as e:
    print(f"Error al configurar evento: {e}")
    print("Probando con otro método...")
    # Método alternativo sin eventos
    print("Usando polling en lugar de eventos...")
    try:
        while True:
            if GPIO.input(BOTON_PIN) == GPIO.LOW:
                # Botón presionado
                sleep(0.05)  # Debounce
                if GPIO.input(BOTON_PIN) == GPIO.LOW:  # Confirmar
                    contador += 1
                    if contador > 255:
                        contador = 0
                    print(f"Contador: {contador}")
                    
                    for i, led in enumerate(leds):
                        bit = (contador >> i) & 0x1
                        GPIO.output(led, GPIO.HIGH if bit else GPIO.LOW)
                    
                    # Esperar a que se suelte el botón
                    while GPIO.input(BOTON_PIN) == GPIO.LOW:
                        sleep(0.01)
            sleep(0.01)
    except KeyboardInterrupt:
        limpiar_y_salir(None, None)

print("Presione el botón en GPIO19 para incrementar contador")
print("Presione Ctrl+C para salir")

# Mantener el programa en ejecución
try:
    if 'evento_boton' in locals():
        # Si usamos eventos, mantener el programa activo
        signal.pause()
except KeyboardInterrupt:
    limpiar_y_salir(None, None)