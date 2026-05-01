#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: Parpadeo manual (sin blink())
Concepto: Controlar frecuencia de parpadeo dentro del bucle de scan
Ejemplo típico: Exámenes donde prohíben usar blink() y hay que hacerlo manual
"""

import time
from gpiozero import LED, Button

def main():
    # --- CONFIGURACIÓN ---
    led1 = LED(20)  # LED principal
    led2 = LED(21)  # LED secundario
    boton = Button(16)
    
    PERIODO_SCAN = 0.05  # 50 ms
    
    # Variables para control de frecuencias
    # Para 1Hz: período total = 1s, medio período = 0.5s
    # Para 2Hz: período total = 0.5s, medio período = 0.25s
    # Para 5Hz: período total = 0.2s, medio período = 0.1s
    
    # Configuración inicial
    frecuencia_actual = 1  # Hz
    medio_periodo = 0.5 / frecuencia_actual  # medio período en segundos
    
    tiempo_ultimo_cambio = time.time()
    estado_led = False
    
    # Variable para cambio de frecuencia
    boton_anterior = boton.is_pressed
    
    print("Programa de parpadeo manual")
    print(f"Frecuencia inicial: {frecuencia_actual}Hz")
    print("Pulsa GPIO16 para cambiar a 2Hz, otra vez a 1Hz, etc.")
    
    try:
        while True:
            inicio_ciclo = time.time()
            tiempo_actual = time.time()
            
            # --- CAMBIO DE FRECUENCIA CON BOTÓN ---
            boton_actual = boton.is_pressed
            if boton_anterior and not boton_actual:
                # Cambiar frecuencia: 1Hz -> 2Hz -> 1Hz -> ...
                if frecuencia_actual == 1:
                    frecuencia_actual = 2
                    print("Frecuencia: 2Hz")
                else:
                    frecuencia_actual = 1
                    print("Frecuencia: 1Hz")
                
                # Actualizar medio período
                medio_periodo = 0.5 / frecuencia_actual
                
                # Reiniciar parpadeo (opcional, como en algunos exámenes)
                tiempo_ultimo_cambio = tiempo_actual
                estado_led = True
                led1.on()
            
            boton_anterior = boton_actual
            
            # --- CONTROL DE PARPADEO MANUAL ---
            # Comprobar si ha pasado el medio período
            if tiempo_actual - tiempo_ultimo_cambio >= medio_periodo:
                # Cambiar estado del LED
                estado_led = not estado_led
                tiempo_ultimo_cambio = tiempo_actual
                
                if estado_led:
                    led1.on()
                    # led2 también puede parpadear sincronizado
                    led2.on()
                else:
                    led1.off()
                    led2.off()
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        led1.off()
        led2.off()

if __name__ == "__main__":
    main()