#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: Detección por FLANCO
Concepto: La salida cambia UNA VEZ por cada pulsación
Ejemplo típico: Toggle de LEDs con cada pulsación
"""

import time
from gpiozero import Button, LEDBoard

def main():
    # --- CONFIGURACIÓN ---
    boton = Button(19)  # Pulsador en GPIO19
    
    # LEDs impares (GPIO21, GPIO23, GPIO25, GPIO27)
    leds_impares = LEDBoard(21, 23, 25, 27)
    
    PERIODO_SCAN = 0.05  # 50 ms
    
    # Variables para detección de flanco
    boton_anterior = boton.is_pressed
    leds_encendidos = False  # Estado de los LEDs
    
    print("Programa de detección por FLANCO")
    print("Cada pulsación de GPIO19 alterna los LEDs impares")
    
    try:
        while True:
            inicio_ciclo = time.time()
            
            # --- LECTURA ACTUAL ---
            boton_actual = boton.is_pressed
            
            # --- DETECCIÓN DE FLANCO DE BAJADA ---
            # En pull-up: pulsado = False, soltado = True
            # Flanco de bajada: pasa de True (soltado) a False (pulsado)
            if boton_anterior and not boton_actual:
                # ¡Se ha pulsado el botón! (solo UNA vez por pulsación)
                leds_encendidos = not leds_encendidos
                
                if leds_encendidos:
                    leds_impares.on()
                    print("LEDs encendidos")
                else:
                    leds_impares.off()
                    print("LEDs apagados")
            
            # Actualizar estado anterior para la próxima iteración
            boton_anterior = boton_actual
            
            # Mantener período de scan
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        leds_impares.off()

if __name__ == "__main__":
    main()