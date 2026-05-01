"""
Práctica 5 - Parte 1: Adquisición de datos de calibración.
Lee el canal 0 del MCP3008 y muestra la tensión en tiempo real.
Útil para crear la tabla de lux vs. tensión.
"""

from gpiozero import MCP3008
from time import sleep

# Inicializar el ADC en el canal 0 (conectar la salida 'vo' del circuito a CH0)
sensor_luz = MCP3008(channel=0)

print("Medidor de tensión para calibración de LDR")
print("Conecta la salida 'vo' al canal CH0.")
print("Presiona Ctrl+C para salir.\n")

try:
    while True:
        # Leer la tensión en voltios
        tension = sensor_luz.voltage
        
        # Mostrar el valor con 3 decimales
        print(f"Tensión vo: {tension:.3f} V", end='\r')
        sleep(0.2) # Leer 5 veces por segundo

except KeyboardInterrupt:
    print("\n\nMedición finalizada.")
