from gpiozero import PWMLED
from threading import Thread, Event
from time import sleep

# Variables globales para control
evento = Event()

# Dividir los LEDs en dos grupos:
# Grupo 1: GPIO20 a GPIO23 (primeros 4 LEDs)
# Grupo 2: GPIO24 a GPIO27 (últimos 4 LEDs)
grupo1 = [PWMLED(pin) for pin in range(20, 24)]
grupo2 = [PWMLED(pin) for pin in range(24, 28)]

def control_grupo(grupo, intervalo):
    """
    Controla un grupo de LEDs con incremento gradual de brillo
    Args:
        grupo: Lista de objetos PWMLED
        intervalo: Tiempo entre cambios de brillo (en segundos)
    """
    while not evento.is_set():
        # Ciclo de brillo de 0% a 100% en pasos del 20%
        for duty in [0, 0.2, 0.4, 0.6, 0.8, 1.0]:
            # Aplicar el duty cycle a todos los LEDs del grupo
            for led in grupo:
                led.value = duty
            sleep(intervalo)  # Esperar el intervalo específico

# Crear hilos para cada grupo
t1 = Thread(target=control_grupo, args=(grupo1, 1.0))   # Cambio cada 1 segundo
t2 = Thread(target=control_grupo, args=(grupo2, 0.5))   # Cambio cada 0.5 segundos

# Configurar como daemon para terminación automática
t1.daemon = True
t2.daemon = True

# Iniciar los hilos
t1.start()
t2.start()

# Programa principal
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    print("\nPrograma terminado")
    evento.set()  # Señalizar a los hilos que deben terminar
    # Cerrar todos los LEDs
    for led in grupo1 + grupo2:
        led.close()

