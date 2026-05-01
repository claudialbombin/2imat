from gpiozero import LEDBoard
from time import sleep
from threading import Thread

# Crear un objeto LEDBoard para controlar todos los LEDs del GPIO20 al GPIO27
leds = LEDBoard(20, 21, 22, 23, 24, 25, 26, 27, pwm=False)

def secuencia_desplazamiento():
    """
    Secuencia que desplaza un LED encendido de izquierda a derecha,
    duplicando la velocidad en cada ciclo completo hasta llegar a 1ms
    """
    delay = 1.0  # Tiempo inicial entre desplazamientos: 1 segundo
    
    # Fase 1: Velocidad creciente hasta llegar a 1ms
    while delay >= 0.001:  # Continuar mientras el delay sea mayor o igual a 1ms
        for i in range(8):  # Recorrer los 8 LEDs
            leds.off()      # Apagar todos los LEDs
            leds[i].on()    # Encender solo el LED actual
            sleep(delay)    # Esperar el tiempo correspondiente
        delay /= 2.0        # Duplicar la velocidad para el siguiente ciclo

    # Fase 2: Velocidad constante (1ms entre cambios)
    while True:
        for i in range(8):
            leds.off()
            leds[i].on()
            sleep(0.001)  # 1ms constante

# Crear y ejecutar el hilo
t = Thread(target=secuencia_desplazamiento)
t.daemon = True
t.start()

# Mantener el programa principal activo
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    print("\nPrograma terminado")
    leds.off()

"""
PREGUNTA: ¿Qué está pasando? (efecto extraño observado en los diodos)
RESPUESTA: Cuando el tiempo entre desplazamientos se reduce por debajo del tiempo de
           persistencia retiniana (aproximadamente 16-20ms), el ojo humano no puede
           seguir los cambios individuales. En lugar de ver un LED moviéndose, se
           perciben varios LEDs encendidos simultáneamente o un efecto de "barrido"
           continuo. Esto se debe a que la frecuencia de cambio supera la capacidad
           de resolución temporal del sistema visual humano, creando una ilusión
           óptica conocida como efecto phi o persistencia de la visión.
"""