#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: Conversor A/D MCP3008
Concepto: Leer canales analógicos (potenciómetro, LDR, NTC)
Ejemplo típico: Leer potenciómetro (CH7) y controlar LEDs con umbral
"""

import time
from gpiozero import MCP3008, LEDBoard

def main():
    # --- CONFIGURACIÓN DEL ADC ---
    # Channel 7 = potenciómetro de la iMAT HAT
    # Channels 0-6 = para sensores externos
    pot = MCP3008(channel=7)
    
    # Podemos crear varios canales
    # sensor_ldr = MCP3008(channel=0)
    # sensor_ntc = MCP3008(channel=1)
    
    # LEDs para visualizar
    leds = LEDBoard(20, 21, 22, 23, 24, 25, 26, 27)
    
    PERIODO_SCAN = 0.05
    
    print("Programa de lectura ADC")
    print("Gira el potenciómetro (CH7) para ver los valores")
    print("Valor 0-1: 0.0 = 0V, 1.0 = 3.3V")
    
    try:
        while True:
            inicio_ciclo = time.time()
            
            # --- FORMAS DE LEER EL ADC ---
            
            # 1. Como valor normalizado (0.0 a 1.0)
            valor = pot.value
            # 0.0 = 0V, 1.0 = 3.3V
            
            # 2. Como voltios (0 a 3.3V)
            voltios = pot.voltage
            
            # 3. Como porcentaje (0 a 100%)
            porcentaje = valor * 100
            
            # Mostrar cada 20 ciclos (aprox 1 segundo)
            if int(time.time() * 20) % 20 == 0:
                print(f"Valor: {valor:.3f} | Voltios: {voltios:.2f}V | {porcentaje:.1f}%")
            
            # --- EJEMPLO: CONTROL DE LEDS CON UMBRAL ---
            # Encender LEDs según el valor del potenciómetro
            # 0.0-0.25: pocos LEDs, 0.25-0.5: más, etc.
            num_leds_encender = int(valor * 8)  # 0 a 8 LEDs
            
            for i, led in enumerate(leds):
                if i < num_leds_encender:
                    led.on()
                else:
                    led.off()
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        leds.off()

if __name__ == "__main__":
    main()