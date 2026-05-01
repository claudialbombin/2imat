#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: RPi.GPIO - Librería de bajo nivel
Concepto: Usar la librería RPi.GPIO directamente
Ejemplo típico: Cuando necesitas control más fino o gpiozero no funciona
"""

import time
import RPi.GPIO as GPIO

def main():
    # --- CONFIGURACIÓN INICIAL (OBLIGATORIA) ---
    # GPIO.BCM: usar numeración del chip (GPIOxx)
    # GPIO.BOARD: usar numeración física del conector
    GPIO.setmode(GPIO.BCM)
    
    # --- CONFIGURAR PINES ---
    
    # Configurar LEDs como salidas (GPIO20 al 27)
    leds = [20, 21, 22, 23, 24, 25, 26, 27]
    for pin in leds:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)  # Inicialmente apagados
    
    # Configurar botones como entradas con pull-up
    boton1 = 16
    boton2 = 19
    GPIO.setup(boton1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(boton2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    PERIODO_SCAN = 0.05
    
    # Variables para detección de flanco
    boton1_anterior = GPIO.input(boton1)
    boton2_anterior = GPIO.input(boton2)
    
    print("Programa con RPi.GPIO")
    print("GPIO16: enciende LEDs pares")
    print("GPIO19: enciende LEDs impares")
    
    try:
        while True:
            inicio_ciclo = time.time()
            
            # --- LEER ENTRADAS ---
            # En RPi.GPIO: 
            # - Con pull-up: 0 = pulsado, 1 = no pulsado
            boton1_actual = GPIO.input(boton1)
            boton2_actual = GPIO.input(boton2)
            
            # --- PROCESAR BOTÓN 1 (GPIO16) ---
            if boton1_anterior == 1 and boton1_actual == 0:  # Flanco bajada
                print("Botón 16 pulsado - LEDs pares")
                # Encender LEDs pares (20,22,24,26)
                for pin in [20, 22, 24, 26]:
                    GPIO.output(pin, GPIO.HIGH)
                # Apagar LEDs impares (21,23,25,27)
                for pin in [21, 23, 25, 27]:
                    GPIO.output(pin, GPIO.LOW)
            
            # --- PROCESAR BOTÓN 2 (GPIO19) ---
            if boton2_anterior == 1 and boton2_actual == 0:  # Flanco bajada
                print("Botón 19 pulsado - LEDs impares")
                # Apagar LEDs pares
                for pin in [20, 22, 24, 26]:
                    GPIO.output(pin, GPIO.LOW)
                # Encender LEDs impares
                for pin in [21, 23, 25, 27]:
                    GPIO.output(pin, GPIO.HIGH)
            
            boton1_anterior = boton1_actual
            boton2_anterior = boton2_actual
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        # --- LIMPIEZA (MUY IMPORTANTE) ---
        # Vuelve a configurar todos los pines como entradas sin pull-ups
        GPIO.cleanup()

if __name__ == "__main__":
    main()