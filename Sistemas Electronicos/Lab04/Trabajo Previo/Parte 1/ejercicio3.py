from gpiozero import LED, Button
from time import sleep, time
from threading import Thread, Lock

# Configuración inicial
led23 = LED(23)
led24 = LED(24)
btn7 = Button(7)
frecuencia_lock = Lock()  # Para acceso seguro a la variable compartida
frecuencia_led23 = 1.0    # Frecuencia inicial: 1 Hz
contador_pulsaciones = 0  # Contador de pulsaciones del botón

def control_led24():
    """
    Controla el LED24 a 0.2 Hz con duty cycle del 25%
    Periodo: 5 segundos (0.2 Hz)
    Encendido: 25% de 5s = 1.25s
    Apagado: 75% de 5s = 3.75s
    """
    while True:
        led24.on()
        sleep(1.25)  # 25% del periodo
        led24.off()
        sleep(3.75)  # 75% del periodo

def control_led23():
    """
    Controla el LED23 con frecuencia variable (1 Hz o 0.2 Hz)
    Usa un lock para acceso seguro a la variable frecuencia_led23
    """
    while True:
        # Obtener la frecuencia actual de forma segura
        with frecuencia_lock:
            periodo = 1.0 / frecuencia_led23
        
        # Ciclo de parpadeo con duty cycle del 50%
        led23.on()
        sleep(periodo / 2)   # Mitad del periodo encendido
        led23.off()
        sleep(periodo / 2)   # Mitad del periodo apagado

def cambiar_frecuencia():
    """
    Callback para el botón GPIO7
    Alterna la frecuencia del LED23 entre 1 Hz y 0.2 Hz
    Reinicia el ciclo del LED23 desde encendido
    """
    global frecuencia_led23, contador_pulsaciones
    
    contador_pulsaciones += 1
    
    # Alternar frecuencia según paridad del contador
    with frecuencia_lock:
        if contador_pulsaciones % 2 == 1:  # Pulsaciones impares
            frecuencia_led23 = 0.2  # Cambiar a 0.2 Hz
        else:  # Pulsaciones pares
            frecuencia_led23 = 1.0  # Volver a 1 Hz
    
    led23.on()  # Reiniciar desde estado encendido (sincronización)

# Configurar el callback del botón
btn7.when_pressed = cambiar_frecuencia

# Crear y ejecutar los hilos
t1 = Thread(target=control_led24)
t2 = Thread(target=control_led23)
t1.daemon = True
t2.daemon = True
t1.start()
t2.start()

# Programa principal
try:
    while True:
        sleep(0.1)  # Loop principal casi sin carga
except KeyboardInterrupt:
    print("\nPrograma terminado")
    led23.off()
    led24.off()

"""
PREGUNTA 1: ¿Se ha fijado en que si pulsa y suelta muy rápido, el sistema no siempre responde?
RESPUESTA: Sí, esto se debe al fenómeno conocido como "rebote mecánico" (bounce) de los
           pulsadores. Cuando se presiona o suelta un botón mecánico, los contactos no
           hacen una transición limpia de 0 a 1 (o viceversa), sino que producen múltiples
           transiciones rápidas durante unos milisegundos antes de estabilizarse.

PREGUNTA 2: ¿Sería capaz de explicar la razón?
RESPUESTA: La razón es física: los contactos metálicos del pulsador rebotan al hacer
           contacto, generando múltiples pulsos eléctricos en muy poco tiempo (típicamente
           5-50ms). El sistema interpreta cada uno de estos rebotes como una pulsación
           independiente, pero a velocidades humanas parecen ser una sola pulsación.

PREGUNTA 3: ¿Se le ocurre alguna solución?
RESPUESTA: Sí, existen varias soluciones:
           1. Implementar un filtro de rebote en software (debounce) que ignore
              múltiples cambios dentro de una ventana de tiempo (ej: 50ms).
           2. Usar hardware específico (circuitos RC o integrados como el 555).
           3. En gpiozero, podemos usar el parámetro `bounce_time` al crear el Button:
              `Button(7, bounce_time=0.05)` para ignorar cambios durante 50ms después
              de una pulsación.

PREGUNTA 4: ¿Está relacionada con el hecho de que se le haya pedido llamar a sleep() solo una vez?
RESPUESTA: Indirectamente, sí. Si usáramos sleep() en el callback del botón, podríamos
           implementar fácilmente un debounce en software. Por ejemplo:
           
           def callback_debounce():
               if time() - ultima_pulsacion > 0.05:  # 50ms de debounce
                   # Procesar pulsación
                   ultima_pulsacion = time()
           
           Sin embargo, usar sleep() en callbacks bloquea todo el programa, por lo que
           no es una buena práctica. La solución con threading permite implementar
           debounce sin bloquear, pero es más compleja.
"""