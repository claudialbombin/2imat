from gpiozero import PWMLED
from threading import Thread, Event
from time import sleep

# Crear lista de LEDs PWM en los pines GPIO20 a GPIO27
leds = [PWMLED(pin) for pin in range(20, 28)]
evento = Event()  # Evento para controlar la terminación del hilo

def ciclo_pwm():
    """
    Ciclo que incrementa gradualmente el brillo de todos los LEDs
    de 0% a 100% en pasos del 20%, con transiciones cada segundo.
    Frecuencia PWM: 100 Hz (por defecto en PWMLED)
    """
    while not evento.is_set():
        # Ciclo de 0% a 100% en pasos del 20%
        for duty in [0, 0.2, 0.4, 0.6, 0.8, 1.0]:
            # Aplicar el mismo duty cycle a todos los LEDs
            for led in leds:
                led.value = duty  # 0.0 = apagado, 1.0 = máximo brillo
            sleep(1)  # Esperar 1 segundo en cada nivel

# Crear y ejecutar el hilo
t = Thread(target=ciclo_pwm)
t.start()

# Programa principal
try:
    while True:
        sleep(1)  # Loop principal de baja carga
except KeyboardInterrupt:
    print("\nPrograma terminado")
    evento.set()  # Señalizar al hilo que debe terminar
    t.join()      # Esperar a que el hilo termine
    # Apagar todos los LEDs
    for led in leds:
        led.close()

