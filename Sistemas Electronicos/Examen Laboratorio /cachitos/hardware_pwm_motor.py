#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: Hardware PWM para motor DC
Concepto: Controlar motor DC con PWM por hardware (alta frecuencia)
Ejemplo típico: Práctica 4 - Control de motores con L293D

INSTRUCCIONES PREVIAS:
1. Editar /boot/firmware/config.txt y añadir:
   dtoverlay=pwm-2chan,pin2=13,func2=4
2. Reiniciar Raspberry Pi
3. Crear entorno virtual (ver enunciado Práctica 4)
"""

import time
import RPi.GPIO as GPIO

# Intentar importar hardware PWM
try:
    from rpi_hardware_pwm import HardwarePWM
    HARDWARE_PWM_DISPONIBLE = True
except ImportError:
    HARDWARE_PWM_DISPONIBLE = False
    print("ADVERTENCIA: rpi_hardware_pwm no instalado")
    print("Usar entorno virtual con: pip install rpi-hardware-pwm")

def main():
    if not HARDWARE_PWM_DISPONIBLE:
        print("No se puede continuar sin rpi_hardware_pwm")
        return
    
    # --- CONFIGURACIÓN GPIO para control de sentido ---
    GPIO.setmode(GPIO.BCM)
    
    # Pines para control de sentido (L293D)
    # MOTOR 1: GPIO4 y GPIO5
    GPIO.setup(4, GPIO.OUT)
    GPIO.setup(5, GPIO.OUT)
    
    # Inicializar en un sentido
    GPIO.output(4, GPIO.HIGH)
    GPIO.output(5, GPIO.LOW)
    
    # --- CONFIGURACIÓN HARDWARE PWM ---
    # Factor de corrección para error sistemático
    FACTOR_CORRECCION = 0.933
    
    # Frecuencia para motor DC (>20kHz para evitar ruido audible)
    FRECUENCIA = 20000  # 20 kHz
    
    # Inicializar PWM por hardware
    # pwm_channel=0 para MOTOR 1 (GPIO18)
    motor_pwm = HardwarePWM(
        pwm_channel=0, 
        hz=FRECUENCIA * FACTOR_CORRECCION
    )
    
    # Arrancar con duty cycle 0% (parado)
    motor_pwm.start(0)
    
    print("Programa de control de motor DC con Hardware PWM")
    print("Control con teclado:")
    print("  w: aumentar velocidad")
    print("  s: disminuir velocidad")
    print("  r: cambiar sentido")
    print("  espacio: parar")
    print("  q: salir")
    
    # Variables de control
    duty_cycle = 0
    sentido = 1  # 1 = adelante, -1 = atrás
    
    try:
        while True:
            # Simulamos control por teclado (en examen usarían botones)
            # En un examen real, esto sería con botones GPIO
            comando = input("Comando: ").lower()
            
            if comando == 'w':
                duty_cycle = min(duty_cycle + 10, 100)
                motor_pwm.change_duty_cycle(duty_cycle)
                print(f"Velocidad: {duty_cycle}%")
                
            elif comando == 's':
                duty_cycle = max(duty_cycle - 10, 0)
                motor_pwm.change_duty_cycle(duty_cycle)
                print(f"Velocidad: {duty_cycle}%")
                
            elif comando == 'r':
                # Cambiar sentido
                sentido *= -1
                if sentido == 1:
                    GPIO.output(4, GPIO.HIGH)
                    GPIO.output(5, GPIO.LOW)
                    print("Sentido: ADELANTE")
                else:
                    GPIO.output(4, GPIO.LOW)
                    GPIO.output(5, GPIO.HIGH)
                    print("Sentido: ATRÁS")
                    
            elif comando == ' ':
                duty_cycle = 0
                motor_pwm.change_duty_cycle(0)
                print("Motor PARADO")
                
            elif comando == 'q':
                break
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        motor_pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()