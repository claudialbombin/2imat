#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: threading - Hilos para concurrencia
Concepto: Ejecutar varias tareas "simultáneamente"
Ejemplo típico: Parpadeo en un hilo mientras el principal hace otra cosa
"""

import time
import threading
from gpiozero import LED, Button

def main():
    # --- CONFIGURACIÓN ---
    led_parpadeo = LED(20)
    led_estado = LED(21)
    boton = Button(16)
    
    # Variable para controlar hilos
    parpadeando = True
    frecuencia = 2  # Hz
    
    print("Programa con threading")
    print("Hilo 1: parpadeo a 2Hz (cada 0.25s medio período)")
    print("Hilo principal: espera botones")
    print("Pulsa GPIO16 para toggle LED de estado")
    
    def tarea_parpadeo():
        """Función que se ejecuta en un hilo aparte"""
        estado = False
        medio_periodo = 0.5 / frecuencia  # 0.25s para 2Hz
        
        while parpadeando:
            tiempo_inicio = time.time()
            
            # Cambiar estado
            estado = not estado
            if estado:
                led_parpadeo.on()
            else:
                led_parpadeo.off()
            
            # Esperar medio período
            tiempo_ejecucion = time.time() - tiempo_inicio
            if tiempo_ejecucion < medio_periodo:
                time.sleep(medio_periodo - tiempo_ejecucion)
        
        # Asegurar que el LED queda apagado al terminar
        led_parpadeo.off()
    
    def tarea_botones():
        """Otra forma: hilo para leer botones (aunque gpiozero ya tiene)"""
        boton_anterior = boton.is_pressed
        
        while parpadeando:
            boton_actual = boton.is_pressed
            
            if boton_anterior and not boton_actual:
                led_estado.toggle()
                print(f"Botón pulsado - LED estado: {'ON' if led_estado.is_lit else 'OFF'}")
            
            boton_anterior = boton_actual
            time.sleep(0.05)  # 50ms
    
    # --- CREAR HILOS ---
    # daemon=True: el hilo termina cuando termina el programa principal
    hilo1 = threading.Thread(target=tarea_parpadeo, daemon=True)
    hilo2 = threading.Thread(target=tarea_botones, daemon=True)
    
    # Iniciar hilos
    hilo1.start()
    hilo2.start()
    
    try:
        # El hilo principal puede hacer otras cosas
        contador = 0
        while True:
            time.sleep(1)
            contador += 1
            print(f"[Principal] Segundos: {contador}")
            
    except KeyboardInterrupt:
        print("\nPrograma terminado")
        parpadeando = False  # Señal para detener hilos
        time.sleep(0.1)  # Pequeña pausa para que los hilos terminen
    finally:
        led_parpadeo.off()
        led_estado.off()

if __name__ == "__main__":
    main()