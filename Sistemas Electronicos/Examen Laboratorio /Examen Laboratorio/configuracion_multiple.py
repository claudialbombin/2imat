#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: List Comprehension para configuración masiva
Concepto: Crear listas de pines/botones/LEDs de forma eficiente
Ejemplo típico: Configurar todos los LEDs y botones de una vez
"""

import time
from gpiozero import Button, LED

def main():
    # --- LIST COMPREHENSION PARA PINES ---
    
    # 1. Rango simple: pines del 20 al 23 (20, 21, 22, 23)
    pines_grupo1 = [pin for pin in range(20, 24)]
    print(f"Grupo 1 (20-23): {pines_grupo1}")
    
    # 2. Rango con paso: pines pares del 20 al 26 (20, 22, 24, 26)
    pines_pares = [pin for pin in range(20, 28, 2)]
    print(f"Pines pares: {pines_pares}")
    
    # 3. Rango con paso: pines impares del 21 al 27 (21, 23, 25, 27)
    pines_impares = [pin for pin in range(21, 28, 2)]
    print(f"Pines impares: {pines_impares}")
    
    # --- CREAR MÚLTIPLES OBJETOS CON LIST COMPREHENSION ---
    
    # Crear lista de botones (GPIO7, 16, 17, 19)
    botones = [Button(pin) for pin in (7, 16, 17, 19)]
    
    # Crear lista de LEDs (GPIO20 al 27)
    leds = [LED(pin) for pin in range(20, 28)]
    
    # --- LEER MÚLTIPLES ENTRADAS A LA VEZ ---
    # Esto es muy útil en exámenes
    estados_botones = [boton.is_pressed for boton in botones]
    print(f"Estados botones: {estados_botones}")
    
    PERIODO_SCAN = 0.05
    
    print("\nPrograma de demostración de List Comprehension")
    print("Pulsa cualquier botón para ver su índice")
    print("Botón 0 = GPIO7, 1=GPIO16, 2=GPIO17, 3=GPIO19")
    
    # Variables para detección de flanco
    estados_anteriores = estados_botones.copy()
    
    try:
        while True:
            inicio_ciclo = time.time()
            
            # Leer todos los botones a la vez (MUY ÚTIL)
            estados_actuales = [boton.is_pressed for boton in botones]
            
            # Detectar flancos en todos los botones
            for i in range(len(botones)):
                if estados_anteriores[i] and not estados_actuales[i]:
                    print(f"Botón {i} pulsado (GPIO{[7,16,17,19][i]})")
                    
                    # Ejemplo: encender LED correspondiente
                    # Mapeo: botón0 -> LED20, botón1 -> LED21, etc.
                    if i < 4:  # Tenemos 4 LEDs para 4 botones
                        leds[i].toggle()
            
            estados_anteriores = estados_actuales.copy()
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        for led in leds:
            led.off()

if __name__ == "__main__":
    main()