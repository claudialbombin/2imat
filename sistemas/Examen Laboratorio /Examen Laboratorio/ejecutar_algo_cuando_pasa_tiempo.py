#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: threading.Timer
Concepto: Ejecutar una función después de un tiempo (una vez)
Ejemplo típico: Apagar un LED después de X segundos
"""

import time
import threading
from gpiozero import Button, LED

def main():
    # --- CONFIGURACIÓN ---
    boton = Button(16)
    led = LED(20)
    
    # Variable para guardar el timer activo
    timer_activo = None
    
    print("Programa con threading.Timer")
    print("Pulsa GPIO16: el LED se enciende 3 segundos")
    print("Si pulsas antes de que pasen 3s, se reinicia el contador")
    
    def apagar_led():
        """Función que se ejecutará cuando termine el timer"""
        led.off()
        print("LED apagado por timer")
    
    def encender_con_temporizador():
        """Enciende LED y programa su apagado"""
        nonlocal timer_activo
        
        # Si hay un timer previo, lo cancelamos
        if timer_activo and timer_activo.is_alive():
            timer_activo.cancel()
            print("Timer anterior cancelado")
        
        # Encender LED
        led.on()
        print("LED encendido")
        
        # Crear nuevo timer para apagar en 3 segundos
        timer_activo = threading.Timer(3.0, apagar_led)
        timer_activo.daemon = True  # El hilo termina con el programa
        timer_activo.start()
    
    # Asignar callback al botón
    boton.when_pressed = encender_con_temporizador
    
    try:
        # Bucle principal vacío (los callbacks hacen todo)
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nPrograma terminado")
        # Cancelar timer si existe
        if timer_activo:
            timer_activo.cancel()
    finally:
        led.off()

if __name__ == "__main__":
    main()