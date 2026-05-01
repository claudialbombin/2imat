#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: Callbacks con gpiozero
Concepto: Ejecutar funciones automáticamente cuando ocurre un evento
Ejemplo típico: Responder a pulsaciones sin estar en el bucle principal
"""

from gpiozero import Button, LED
from signal import pause

def main():
    # --- CONFIGURACIÓN ---
    led_rojo = LED(20)
    led_verde = LED(21)
    led_azul = LED(22)
    
    boton1 = Button(16)
    boton2 = Button(17)
    boton3 = Button(19)
    
    # --- DEFINIR CALLBACKS (funciones que se llaman automáticamente) ---
    
    def pulsar_boton1():
        """Se llama cuando se pulsa boton1"""
        led_rojo.toggle()
        print("Botón 1 pulsado - LED rojo toggle")
    
    def soltar_boton1():
        """Se llama cuando se suelta boton1"""
        print("Botón 1 soltado")
    
    def pulsar_boton2():
        """Se llama cuando se pulsa boton2"""
        led_verde.on()
        print("Botón 2 pulsado - LED verde ON")
    
    def soltar_boton2():
        """Se llama cuando se suelta boton2"""
        led_verde.off()
        print("Botón 2 soltado - LED verde OFF")
    
    def pulsar_boton3():
        """Se llama cuando se pulsa boton3"""
        led_azul.toggle()
        print("Botón 3 pulsado - LED azul toggle")
    
    # --- ASIGNAR CALLBACKS ---
    # when_pressed: se llama en el flanco de bajada (cuando se pulsa)
    # when_released: se llama en el flanco de subida (cuando se suelta)
    
    boton1.when_pressed = pulsar_boton1
    boton1.when_released = soltar_boton1
    
    boton2.when_pressed = pulsar_boton2
    boton2.when_released = soltar_boton2
    
    boton3.when_pressed = pulsar_boton3
    # No asignamos when_released para boton3
    
    # --- CALLBACKS CON PARÁMETROS (usando lambda) ---
    # A veces necesitamos pasar parámetros a los callbacks
    
    def encender_led(led):
        """Callback que recibe qué LED encender"""
        led.on()
        print(f"LED {led.pin} encendido")
    
    def apagar_led(led):
        """Callback que recibe qué LED apagar"""
        led.off()
        print(f"LED {led.pin} apagado")
    
    # Para pasar parámetros, usamos lambda
    # Creamos otro botón virtual para este ejemplo
    # boton_extra = Button(7)
    # boton_extra.when_pressed = lambda: encender_led(led_rojo)
    # boton_extra.when_released = lambda: apagar_led(led_rojo)
    
    print("Programa con callbacks")
    print("Los callbacks se ejecutan automáticamente")
    print("Pulsa botones para ver el comportamiento")
    print("GPIO16: toggle rojo (pulsar/soltar)")
    print("GPIO17: ON al pulsar, OFF al soltar")
    print("GPIO19: toggle azul (solo al pulsar)")
    
    # --- BUCLE PRINCIPAL ---
    # Con callbacks, podemos tener un bucle vacío o usar pause()
    # pause() mantiene el programa en ejecución hasta Ctrl+C
    
    try:
        # El programa se queda esperando eventos
        pause()
        
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        led_rojo.off()
        led_verde.off()
        led_azul.off()

if __name__ == "__main__":
    main()