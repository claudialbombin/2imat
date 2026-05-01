#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: Detección por NIVEL
Concepto: La salida depende del estado actual de la entrada
Ejemplo típico: Encender LEDs mientras se pulsa un botón
"""

import time
from gpiozero import Button, LED, LEDBoard

def main():
    # --- CONFIGURACIÓN ---
    # Pulsador en GPIO19 (pull-up interno)
    boton = Button(19)
    
    # LEDs pares (GPIO20, GPIO22, GPIO24, GPIO26)
    leds_pares = LEDBoard(20, 22, 24, 26)
    
    # LEDs impares (GPIO21, GPIO23, GPIO25, GPIO27)
    leds_impares = LEDBoard(21, 23, 25, 27)
    
    PERIODO_SCAN = 0.05  # 50 ms
    
    print("Programa de detección por NIVEL")
    print("Mantén pulsado GPIO19 para encender LEDs pares")
    print("Suelta para encender LEDs impares")
    
    try:
        while True:
            inicio_ciclo = time.time()
            
            # --- LECTURA POR NIVEL ---
            # El estado de las salidas depende DIRECTAMENTE
            # del valor actual de la entrada
            if boton.is_pressed:  # True cuando está pulsado
                # Mientras está pulsado: enciende pares
                leds_pares.on()
                leds_impares.off()
            else:
                # Mientras NO está pulsado: enciende impares
                leds_pares.off()
                leds_impares.on()
            
            # Mantener período de scan
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        leds_pares.off()
        leds_impares.off()

if __name__ == "__main__":
    main()