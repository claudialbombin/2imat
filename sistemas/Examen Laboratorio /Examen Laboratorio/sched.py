#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: sched - Planificador de tareas
Concepto: Ejecutar tareas periódicamente sin bloquear
Ejemplo típico: Leer sensor cada segundo mientras se atienden botones
"""

import time
import sched
import threading
from gpiozero import Button, LED, MCP3008

def main():
    # --- CONFIGURACIÓN ---
    led = LED(20)
    boton = Button(16)
    sensor = MCP3008(channel=7)  # Potenciómetro
    
    # Crear planificador
    planificador = sched.scheduler(time.time, time.sleep)
    
    # Variable para controlar ejecución
    ejecutando = True
    
    print("Programa con sched (planificador)")
    print("Tarea periódica: leer sensor cada 0.5 segundos")
    print("Pulsa GPIO16 para toggle LED (responde inmediatamente)")
    
    def tarea_periodica():
        """Función que se ejecuta periódicamente"""
        if not ejecutando:
            return
        
        # Leer sensor
        valor = sensor.value
        voltios = sensor.voltage
        
        print(f"[Tarea periódica] Sensor: {valor:.3f} ({voltios:.2f}V)")
        
        # Reprogramar la tarea para que se ejecute de nuevo en 0.5s
        if ejecutando:
            planificador.enter(0.5, 1, tarea_periodica)
    
    def pulsar_boton():
        """Callback del botón - respuesta inmediata"""
        led.toggle()
        print(f"[Botón] LED toggled - ahora {'ON' if led.is_lit else 'OFF'}")
    
    # Asignar callback al botón
    boton.when_pressed = pulsar_boton
    
    # Programar primera ejecución de la tarea periódica
    planificador.enter(0.5, 1, tarea_periodica)
    
    # --- EJECUCIÓN ---
    # Necesitamos ejecutar el planificador en un hilo aparte
    # para que no bloquee el bucle principal
    
    def run_scheduler():
        """Ejecuta el planificador en un hilo"""
        planificador.run()
    
    # Crear y lanzar hilo para el planificador
    hilo_sched = threading.Thread(target=run_scheduler, daemon=True)
    hilo_sched.start()
    
    try:
        # Bucle principal - puede hacer otras cosas
        contador = 0
        while True:
            # El bucle principal puede hacer tareas no periódicas
            time.sleep(1)
            contador += 1
            if contador % 5 == 0:
                print("[Principal] Todavía funcionando...")
            
    except KeyboardInterrupt:
        print("\nPrograma terminado")
        ejecutando = False  # Para detener tareas periódicas
    finally:
        led.off()

if __name__ == "__main__":
    main()