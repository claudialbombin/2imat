from gpiozero import AngularServo, Button
from threading import Thread, Timer, Lock
from time import sleep

# Configurar el servo con los parámetros especificados:
# -45° = posición cerrada (0.5ms pulse)
# 45° = posición abierta (2.5ms pulse)
# Periodo: 20ms (50 Hz)
servo = AngularServo(14, 
                    min_angle=-45, 
                    max_angle=45,
                    min_pulse_width=0.5/1000,  # 0.5ms
                    max_pulse_width=2.5/1000,  # 2.5ms
                    frame_width=20/1000)       # 20ms periodo

# Configurar el botón del GPIO19
btn19 = Button(19)

# Variables y locks para control seguro entre hilos
estado_lock = Lock()
abierto = False  # Estado actual de la barrera
timer_cierre = None  # Referencia al timer de cierre automático

def alternar_servo():
    """
    Alterna la posición del servo entre abierto (-45°) y cerrado (45°)
    Gestiona el timer de cierre automático de 10 segundos
    """
    global abierto, timer_cierre
    
    with estado_lock:  # Sección crítica para acceso seguro
        if abierto:
            # Cerrar la barrera
            servo.angle = -45  # Posición cerrada
            print("Barrera CERRADA")
            
            # Cancelar el timer de cierre si existe
            if timer_cierre:
                timer_cierre.cancel()
                timer_cierre = None
        else:
            # Abrir la barrera
            servo.angle = 45   # Posición abierta
            print("Barrera ABIERTA")
            
            # Programar cierre automático en 10 segundos
            timer_cierre = Timer(10.0, cerrar_servo)
            timer_cierre.start()
            print("Cierre automático programado en 10 segundos")
        
        # Cambiar el estado
        abierto = not abierto

def cerrar_servo():
    """
    Cierra la barrera automáticamente después de 10 segundos
    """
    global abierto
    with estado_lock:
        if abierto:  # Solo cerrar si todavía está abierta
            servo.angle = -45
            abierto = False
            print("Barrera CERRADA automáticamente (timeout 10s)")

# Asignar la función al botón
btn19.when_pressed = alternar_servo

# Inicializar en posición cerrada
servo.angle = -45
print("Sistema iniciado. Barrera en posición CERRADA.")

# Mantener el programa vivo
try:
    while True:
        sleep(0.1)  # Loop principal de baja carga
except KeyboardInterrupt:
    print("\nPrograma terminado")
    # Cancelar el timer si está activo
    if timer_cierre:
        timer_cierre.cancel()
    # Cerrar el servo
    servo.close()

