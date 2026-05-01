import RPi.GPIO as GPIO
from rpi_hardware_pwm import HardwarePWM
from threading import Thread, Event
from time import sleep

# Variables globales
evento = Event()
FACTOR_CORRECCION = 0.933  # Factor mágico para corregir error sistemático

def control_motor():
    """
    Controla dos motores DC usando PWM por hardware de la Raspberry Pi
    Requiere configuración previa del sistema y entorno virtual
    """
    # Configurar modo de numeración de pines BCM
    GPIO.setmode(GPIO.BCM)
    
    # CONFIGURACIÓN MOTOR 1 (PWM0)
    # Pines de dirección: GPIO4 y GPIO5
    GPIO.setup(4, GPIO.OUT)
    GPIO.setup(5, GPIO.OUT)
    
    # Establecer sentido de giro (HIGH/LOW determina la dirección)
    GPIO.output(4, GPIO.HIGH)  # Sentido horario
    GPIO.output(5, GPIO.LOW)   # El otro pin debe estar en bajo
    
    # Configurar PWM por hardware en canal 0
    # Frecuencia: 20kHz * factor de corrección (para evitar pitido audible)
    motor1 = HardwarePWM(pwm_channel=0, hz=int(20000 * FACTOR_CORRECCION))
    motor1.start(50.0)  # Iniciar al 50% de duty cycle
    
    # CONFIGURACIÓN MOTOR 2 (PWM1)
    # Pines de dirección: GPIO26 y GPIO19 (verificar en esquema iMAT HAT)
    GPIO.setup(26, GPIO.OUT)
    GPIO.setup(19, GPIO.OUT)
    
    # Establecer sentido de giro
    GPIO.output(26, GPIO.HIGH)  # Sentido horario
    GPIO.output(19, GPIO.LOW)
    
    # Configurar PWM por hardware en canal 1
    motor2 = HardwarePWM(pwm_channel=1, hz=int(20000 * FACTOR_CORRECCION))
    motor2.start(50.0)  # Iniciar al 50% de duty cycle
    
    print("Motores funcionando al 50% de velocidad")
    print("Presiona Ctrl+C para detener")
    
    try:
        while not evento.is_set():
            # En este loop se podrían cambiar parámetros dinámicamente:
            # motor1.change_frequency(25000 * FACTOR_CORRECCION)
            # motor1.change_duty_cycle(60.0)  # Cambiar a 60%
            sleep(0.1)  # Loop de control
            
    finally:
        # Secuencia de limpieza
        print("\nDeteniendo motores...")
        motor1.stop()
        motor2.stop()
        GPIO.cleanup()
        print("Motores detenidos y GPIO limpiado")

# Crear y ejecutar el hilo de control
t = Thread(target=control_motor)
t.daemon = True
t.start()

# Programa principal
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    print("\nTerminando programa...")
    evento.set()  # Señalizar al hilo que debe terminar
    t.join()      # Esperar a que el hilo termine
    print("Programa terminado correctamente")
