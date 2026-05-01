#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: Divisor de tensión con sensores resistivos
Concepto: Calcular tensión de salida y leer sensores (LDR, NTC)
Ejemplo típico: Montar divisor con LDR y calcular lux/temperatura
"""

import time
from gpiozero import MCP3008, LED

def calcular_vout(r1, r2, vin=3.3):
    """
    Calcula la tensión de salida de un divisor de tensión.
    
    Para divisor con R1 arriba (a Vcc) y R2 abajo (a GND):
    Vout = Vin * R2 / (R1 + R2)
    
    Args:
        r1: Resistencia superior (conectada a Vin)
        r2: Resistencia inferior (conectada a GND)
        vin: Tensión de alimentación (por defecto 3.3V)
    
    Returns:
        Tensión de salida en voltios
    """
    return vin * r2 / (r1 + r2)

def calcular_resistencia_desde_vout(vout, r_fija, vin=3.3, posicion='abajo'):
    """
    Calcula la resistencia desconocida a partir de Vout.
    
    Args:
        vout: Tensión medida en el divisor
        r_fija: Resistencia conocida
        vin: Tensión de alimentación
        posicion: 'abajo' si sensor está abajo, 'arriba' si está arriba
    
    Returns:
        Resistencia calculada
    """
    if posicion == 'abajo':
        # Sensor en R2: Vout = Vin * Rsensor / (Rfija + Rsensor)
        # Despejando: Rsensor = (Vout * Rfija) / (Vin - Vout)
        if vout >= vin:  # Evitar división por cero
            return float('inf')
        return (vout * r_fija) / (vin - vout)
    
    else:  # Sensor arriba
        # Sensor en R1: Vout = Vin * Rfija / (Rsensor + Rfija)
        # Despejando: Rsensor = (Vin * Rfija / Vout) - Rfija
        if vout <= 0:
            return float('inf')
        return (vin * r_fija / vout) - r_fija

def main():
    """
    Ejemplo: LDR en divisor de tensión
    Montaje: Vcc(3.3V) -> Rfija (10k) -> punto medio -> LDR -> GND
    El punto medio se conecta a canal ADC
    """
    
    # --- CONFIGURACIÓN ---
    # Resistencia fija del divisor (la que hemos elegido)
    R_FIJA = 10000  # 10k ohmios
    
    # Sensor LDR conectado a CH0
    sensor = MCP3008(channel=0)
    
    # LEDs para indicar niveles de luz
    led_poca_luz = LED(20)
    led_mucha_luz = LED(21)
    
    PERIODO_SCAN = 0.1
    
    print("Programa de divisor de tensión con LDR")
    print(f"Resistencia fija: {R_FIJA/1000:.1f}kΩ")
    print("Sensor en posición INFERIOR (entre punto medio y GND)")
    
    try:
        while True:
            inicio_ciclo = time.time()
            
            # Leer tensión del ADC
            vout = sensor.voltage
            
            # Calcular resistencia del LDR
            # Como sensor está abajo (entre punto medio y GND)
            r_ldr = calcular_resistencia_desde_vout(
                vout, 
                R_FIJA, 
                vin=3.3, 
                posicion='abajo'
            )
            
            # Calcular lux aproximado (relación inversa)
            # A más luz, menos resistencia
            if r_ldr > 0 and r_ldr < float('inf'):
                # Modelo aproximado: lux = k / R
                # Ajustar constantes según sensor
                k = 100000  # Constante de calibración
                lux = k / r_ldr
            else:
                lux = 0
            
            # Mostrar cada segundo
            if int(time.time()) > int(time.time() - 0.1):
                print(f"Vout: {vout:.2f}V | R_LDR: {r_ldr/1000:.1f}kΩ | Lux: {lux:.0f}")
            
            # Control de LEDs según nivel de luz
            if lux < 50:
                led_poca_luz.on()
                led_mucha_luz.off()
            elif lux > 200:
                led_poca_luz.off()
                led_mucha_luz.on()
            else:
                led_poca_luz.off()
                led_mucha_luz.off()
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        led_poca_luz.off()
        led_mucha_luz.off()

if __name__ == "__main__":
    main()