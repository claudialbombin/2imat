#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: Control de servomotor
Concepto: Mover servo a diferentes posiciones
Ejemplo típico: Barrera que se abre/cierra con botón y temporizador
"""

import time
from gpiozero import AngularServo, Button
from gpiozero.pins.pigpio import PiGPIOFactory
import threading

def main():
    # --- CONFIGURACIÓN IMPORTANTE ---
    # Para servos necesitamos PiGPIO factory (más preciso)
    # Antes de ejecutar: en terminal escribir "sudo pigpiod"
    
    try:
        factory = PiGPIOFactory()
    except:
        print("ERROR: ¿Has ejecutado 'sudo pigpiod' en terminal?")
        print("Ejecuta: sudo pigpiod")
        return
    
    # --- CONFIGURAR SERVO ---
    # Servo en GPIO14 (el pin central del conector DIG (SERVO))
    # Ángulos típicos: -90 a 90 grados
    # Pero pueden variar según el servo
    
    servo = AngularServo(
        14,  # GPIO14
        min_angle=-90,
        max_angle=90,
        min_pulse_width=0.0005,  # 0.5ms para 0 grados (ajustar)
        max_pulse_width=0.0025,  # 2.5ms para 180 grados (ajustar)
        pin_factory=factory
    )
    
    # Botones
    boton_abrir = Button(16)
    boton_cerrar = Button(17)
    
    # Posiciones
    POS_CERRADO = -45  # Grados (barrera cerrada)
    POS_ABIERTO = 45   # Grados (barrera abierta)
    
    # Variables
    posicion_actual = POS_CERRADO
    tiempo_apertura = 0
    TIEMPO_AUTO_CIERRE = 10  # segundos
    
    # Timer para cierre automático
    timer_cierre = None
    
    print("Programa de control de servomotor")
    print(f"GPIO16: abrir barrera ({POS_ABIERTO}°)")
    print(f"GPIO17: cerrar barrera ({POS_CERRADO}°)")
    print(f"Cierre automático después de {TIEMPO_AUTO_CIERRE}s")
    
    def cerrar_automatico():
        """Cierra la barrera automáticamente"""
        nonlocal posicion_actual
        if posicion_actual == POS_ABIERTO:
            servo.angle = POS_CERRADO
            posicion_actual = POS_CERRADO
            print("Cierre automático - Barrera CERRADA")
    
    def abrir_barrera():
        """Abre la barrera y programa cierre automático"""
        nonlocal posicion_actual, timer_cierre
        
        # Cancelar timer anterior si existe
        if timer_cierre and timer_cierre.is_alive():
            timer_cierre.cancel()
        
        # Abrir barrera
        servo.angle = POS_ABIERTO
        posicion_actual = POS_ABIERTO
        tiempo_apertura = time.time()
        print("Barrera ABIERTA")
        
        # Programar cierre automático
        timer_cierre = threading.Timer(TIEMPO_AUTO_CIERRE, cerrar_automatico)
        timer_cierre.daemon = True
        timer_cierre.start()
    
    def cerrar_barrera():
        """Cierra la barrera manualmente"""
        nonlocal posicion_actual, timer_cierre
        
        # Cancelar timer si existe
        if timer_cierre and timer_cierre.is_alive():
            timer_cierre.cancel()
        
        # Cerrar barrera
        servo.angle = POS_CERRADO
        posicion_actual = POS_CERRADO
        print("Barrera CERRADA")
    
    # Asignar callbacks
    boton_abrir.when_pressed = abrir_barrera
    boton_cerrar.when_pressed = cerrar_barrera
    
    # Posición inicial
    servo.angle = POS_CERRADO
    print("Posición inicial: CERRADA")
    
    try:
        # Bucle principal
        while True:
            time.sleep(0.1)
            
            # Opcional: mostrar tiempo restante si está abierta
            if posicion_actual == POS_ABIERTO:
                tiempo_transcurrido = time.time() - tiempo_apertura
                tiempo_restante = TIEMPO_AUTO_CIERRE - tiempo_transcurrido
                if tiempo_restante > 0 and int(tiempo_restante * 10) % 10 == 0:
                    print(f"Tiempo restante: {tiempo_restante:.1f}s")
            
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        # Detener servo (deja de enviar señal)
        servo.detach()

if __name__ == "__main__":
    main()