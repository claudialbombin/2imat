#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: PWM para control de intensidad
Concepto: Usar PWMLED para variar brillo (sin parpadeo apreciable)
Ejemplo típico: LEDs que se atenúan gradualmente
"""

import time
from gpiozero import PWMLED, Button
from gpiozero import MCP3008

def main():
    # --- CONFIGURACIÓN PWM ---
    # PWMLED permite valor entre 0.0 y 1.0 (0% a 100% duty cycle)
    # Frecuencia >60Hz para que no se aprecie parpadeo
    led_pwm = PWMLED(20, frequency=100)  # 100 Hz
    
    # Botón para cambiar intensidad
    boton = Button(16)
    
    # Opcional: potenciómetro para control analógico
    pot = MCP3008(channel=7)
    
    PERIODO_SCAN = 0.05
    
    # Variables para control manual
    boton_anterior = boton.is_pressed
    intensidad = 0.0
    incremento = 0.2  # 20% por pulsación
    
    print("Programa de control PWM")
    print("Opciones:")
    print("  1. Pulsa GPIO16 para incrementar intensidad 20%")
    print("  2. Gira potenciómetro para control analógico")
    print("  3. Edita el código para elegir modo")
    
    # Elegir modo: 1=manual, 2=pot
    MODO = 2  # Cambiar según queramos probar
    
    try:
        while True:
            inicio_ciclo = time.time()
            
            if MODO == 1:
                # --- MODO MANUAL (por pulsador) ---
                boton_actual = boton.is_pressed
                
                if boton_anterior and not boton_actual:
                    intensidad = intensidad + incremento
                    if intensidad > 1.0:
                        intensidad = 0.0  # Reiniciar
                    
                    led_pwm.value = intensidad
                    print(f"Intensidad: {intensidad*100:.0f}%")
                
                boton_anterior = boton_actual
                
            elif MODO == 2:
                # --- MODO ANALÓGICO (por potenciómetro) ---
                intensidad = pot.value  # 0.0 a 1.0
                led_pwm.value = intensidad
                
                # Mostrar cada segundo
                if int(time.time()) > int(time.time() - 0.05):
                    print(f"Intensidad: {intensidad*100:.1f}%")
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        led_pwm.off()

if __name__ == "__main__":
    main()