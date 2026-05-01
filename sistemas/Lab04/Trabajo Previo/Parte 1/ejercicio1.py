from gpiozero import LED
from time import sleep
from threading import Thread

led20 = LED(20)

def parpadear_2_5hz():
    """Función que hace parpadear el LED a 2.5 Hz (200ms encendido, 200ms apagado)"""
    while True:
        led20.on()
        sleep(0.2)  # 200 ms encendido
        led20.off()
        sleep(0.2)  # 200 ms apagado

t = Thread(target=parpadear_2_5hz)
t.daemon = True  # El hilo se cerrará cuando termine el programa principal
t.start()

# Mantener el programa vivo
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    print("\nPrograma terminado")
    led20.off()

