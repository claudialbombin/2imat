#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: Interpolación lineal para curvas de calibración
Concepto: Convertir voltios a lux usando tabla de calibración
Ejemplo típico: Práctica 5 - sensor LDR no lineal
"""

import time
from gpiozero import MCP3008, LED

def interpolar(valor, puntos_x, puntos_y):
    """
    Interpola linealmente un valor dado una tabla de puntos.
    
    Args:
        valor: El valor a interpolar (debe estar en el rango de puntos_x)
        puntos_x: Lista de valores conocidos (ej: voltajes)
        puntos_y: Lista de valores correspondientes (ej: lux)
    
    Returns:
        Valor interpolado
    """
    # Verificar límites
    if valor <= puntos_x[0]:
        return puntos_y[0]
    if valor >= puntos_x[-1]:
        return puntos_y[-1]
    
    # Buscar intervalo
    for i in range(len(puntos_x) - 1):
        if puntos_x[i] <= valor <= puntos_x[i + 1]:
            # Interpolación lineal: 
            # y = y1 + (y2-y1)/(x2-x1) * (x - x1)
            x1, x2 = puntos_x[i], puntos_x[i + 1]
            y1, y2 = puntos_y[i], puntos_y[i + 1]
            
            resultado = y1 + (y2 - y1) / (x2 - x1) * (valor - x1)
            return resultado
    
    return puntos_y[-1]  # Por si acaso

def main():
    # --- DATOS DE CALIBRACIÓN (ejemplo de Práctica 5) ---
    # Estos datos se obtienen experimentalmente con luxómetro
    # voltios_medidos = [0.5, 1.2, 1.8, 2.4, 2.9, 3.2]
    # lux_reales = [0, 150, 300, 500, 800, 1000]
    
    # Ejemplo con datos típicos
    voltios_medidos = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    lux_reales = [0, 200, 400, 600, 800, 1000]
    
    # Sensor (LDR en CH0)
    sensor = MCP3008(channel=0)
    
    # LED para indicar umbral
    led = LED(20)
    
    PERIODO_SCAN = 0.1  # 100 ms
    
    print("Programa de interpolación")
    print("Tabla de calibración:")
    for v, l in zip(voltios_medidos, lux_reales):
        print(f"  {v:.1f}V -> {l} lux")
    
    try:
        while True:
            inicio_ciclo = time.time()
            
            # Leer sensor
            voltios = sensor.voltage
            
            # Convertir a lux usando interpolación
            lux = interpolar(voltios, voltios_medidos, lux_reales)
            
            # Mostrar cada segundo
            if int(time.time()) > int(time.time() - 0.1):
                print(f"Voltios: {voltios:.2f}V -> Lux: {lux:.1f} lux")
            
            # Ejemplo: encender LED si hay poca luz
            UMBRAL_LUX = 300
            if lux < UMBRAL_LUX:
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
        led.off()

if __name__ == "__main__":
    main()