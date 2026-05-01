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
    
    
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: Detección por FLANCO
Concepto: La salida cambia UNA VEZ por cada pulsación
Ejemplo típico: Toggle de LEDs con cada pulsación
"""

import time
from gpiozero import Button, LEDBoard

def main():
    # --- CONFIGURACIÓN ---
    boton = Button(19)  # Pulsador en GPIO19
    
    # LEDs impares (GPIO21, GPIO23, GPIO25, GPIO27)
    leds_impares = LEDBoard(21, 23, 25, 27)
    
    PERIODO_SCAN = 0.05  # 50 ms
    
    # Variables para detección de flanco
    boton_anterior = boton.is_pressed
    leds_encendidos = False  # Estado de los LEDs
    
    print("Programa de detección por FLANCO")
    print("Cada pulsación de GPIO19 alterna los LEDs impares")
    
    try:
        while True:
            inicio_ciclo = time.time()
            
            # --- LECTURA ACTUAL ---
            boton_actual = boton.is_pressed
            
            # --- DETECCIÓN DE FLANCO DE BAJADA ---
            # En pull-up: pulsado = False, soltado = True
            # Flanco de bajada: pasa de True (soltado) a False (pulsado)
            if boton_anterior and not boton_actual:
                # ¡Se ha pulsado el botón! (solo UNA vez por pulsación)
                leds_encendidos = not leds_encendidos
                
                if leds_encendidos:
                    leds_impares.on()
                    print("LEDs encendidos")
                else:
                    leds_impares.off()
                    print("LEDs apagados")
            
            # Actualizar estado anterior para la próxima iteración
            boton_anterior = boton_actual
            
            # Mantener período de scan
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        leds_impares.off()

if __name__ == "__main__":
    main()
    
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: Detección por NIVEL
Concepto: La salida depende del estado actual de la entrada
Ejemplo típico: Encender LEDs mientras se pulsa un botón
"""

import time
from gpiozero import Button, LED, LEDBoard

def main():
    # --- CONFIGURACIÓN ---
    # Pulsador en GPIO19 (pull-up interno)
    boton = Button(19)
    
    # LEDs pares (GPIO20, GPIO22, GPIO24, GPIO26)
    leds_pares = LEDBoard(20, 22, 24, 26)
    
    # LEDs impares (GPIO21, GPIO23, GPIO25, GPIO27)
    leds_impares = LEDBoard(21, 23, 25, 27)
    
    PERIODO_SCAN = 0.05  # 50 ms
    
    print("Programa de detección por NIVEL")
    print("Mantén pulsado GPIO19 para encender LEDs pares")
    print("Suelta para encender LEDs impares")
    
    try:
        while True:
            inicio_ciclo = time.time()
            
            # --- LECTURA POR NIVEL ---
            # El estado de las salidas depende DIRECTAMENTE
            # del valor actual de la entrada
            if boton.is_pressed:  # True cuando está pulsado
                # Mientras está pulsado: enciende pares
                leds_pares.on()
                leds_impares.off()
            else:
                # Mientras NO está pulsado: enciende impares
                leds_pares.off()
                leds_impares.on()
            
            # Mantener período de scan
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        leds_pares.off()
        leds_impares.off()

if __name__ == "__main__":
    main()
    
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
    

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: threading.Timer
Concepto: Ejecutar una función después de un tiempo (una vez)
Ejemplo típico: Apagar un LED después de X segundos
"""

import time
import threading
from gpiozero import Button, LED

def main():
    # --- CONFIGURACIÓN ---
    boton = Button(16)
    led = LED(20)
    
    # Variable para guardar el timer activo
    timer_activo = None
    
    print("Programa con threading.Timer")
    print("Pulsa GPIO16: el LED se enciende 3 segundos")
    print("Si pulsas antes de que pasen 3s, se reinicia el contador")
    
    def apagar_led():
        """Función que se ejecutará cuando termine el timer"""
        led.off()
        print("LED apagado por timer")
    
    def encender_con_temporizador():
        """Enciende LED y programa su apagado"""
        nonlocal timer_activo
        
        # Si hay un timer previo, lo cancelamos
        if timer_activo and timer_activo.is_alive():
            timer_activo.cancel()
            print("Timer anterior cancelado")
        
        # Encender LED
        led.on()
        print("LED encendido")
        
        # Crear nuevo timer para apagar en 3 segundos
        timer_activo = threading.Timer(3.0, apagar_led)
        timer_activo.daemon = True  # El hilo termina con el programa
        timer_activo.start()
    
    # Asignar callback al botón
    boton.when_pressed = encender_con_temporizador
    
    try:
        # Bucle principal vacío (los callbacks hacen todo)
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nPrograma terminado")
        # Cancelar timer si existe
        if timer_activo:
            timer_activo.cancel()
    finally:
        led.off()

if __name__ == "__main__":
    main()
    
    
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
    
    
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: Parpadeo manual (sin blink())
Concepto: Controlar frecuencia de parpadeo dentro del bucle de scan
Ejemplo típico: Exámenes donde prohíben usar blink() y hay que hacerlo manual
"""

import time
from gpiozero import LED, Button

def main():
    # --- CONFIGURACIÓN ---
    led1 = LED(20)  # LED principal
    led2 = LED(21)  # LED secundario
    boton = Button(16)
    
    PERIODO_SCAN = 0.05  # 50 ms
    
    # Variables para control de frecuencias
    # Para 1Hz: período total = 1s, medio período = 0.5s
    # Para 2Hz: período total = 0.5s, medio período = 0.25s
    # Para 5Hz: período total = 0.2s, medio período = 0.1s
    
    # Configuración inicial
    frecuencia_actual = 1  # Hz
    medio_periodo = 0.5 / frecuencia_actual  # medio período en segundos
    
    tiempo_ultimo_cambio = time.time()
    estado_led = False
    
    # Variable para cambio de frecuencia
    boton_anterior = boton.is_pressed
    
    print("Programa de parpadeo manual")
    print(f"Frecuencia inicial: {frecuencia_actual}Hz")
    print("Pulsa GPIO16 para cambiar a 2Hz, otra vez a 1Hz, etc.")
    
    try:
        while True:
            inicio_ciclo = time.time()
            tiempo_actual = time.time()
            
            # --- CAMBIO DE FRECUENCIA CON BOTÓN ---
            boton_actual = boton.is_pressed
            if boton_anterior and not boton_actual:
                # Cambiar frecuencia: 1Hz -> 2Hz -> 1Hz -> ...
                if frecuencia_actual == 1:
                    frecuencia_actual = 2
                    print("Frecuencia: 2Hz")
                else:
                    frecuencia_actual = 1
                    print("Frecuencia: 1Hz")
                
                # Actualizar medio período
                medio_periodo = 0.5 / frecuencia_actual
                
                # Reiniciar parpadeo (opcional, como en algunos exámenes)
                tiempo_ultimo_cambio = tiempo_actual
                estado_led = True
                led1.on()
            
            boton_anterior = boton_actual
            
            # --- CONTROL DE PARPADEO MANUAL ---
            # Comprobar si ha pasado el medio período
            if tiempo_actual - tiempo_ultimo_cambio >= medio_periodo:
                # Cambiar estado del LED
                estado_led = not estado_led
                tiempo_ultimo_cambio = tiempo_actual
                
                if estado_led:
                    led1.on()
                    # led2 también puede parpadear sincronizado
                    led2.on()
                else:
                    led1.off()
                    led2.off()
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        led1.off()
        led2.off()

if __name__ == "__main__":
    main()
    
    
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
    
    
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: RPi.GPIO - Librería de bajo nivel
Concepto: Usar la librería RPi.GPIO directamente
Ejemplo típico: Cuando necesitas control más fino o gpiozero no funciona
"""

import time
import RPi.GPIO as GPIO

def main():
    # --- CONFIGURACIÓN INICIAL (OBLIGATORIA) ---
    # GPIO.BCM: usar numeración del chip (GPIOxx)
    # GPIO.BOARD: usar numeración física del conector
    GPIO.setmode(GPIO.BCM)
    
    # --- CONFIGURAR PINES ---
    
    # Configurar LEDs como salidas (GPIO20 al 27)
    leds = [20, 21, 22, 23, 24, 25, 26, 27]
    for pin in leds:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)  # Inicialmente apagados
    
    # Configurar botones como entradas con pull-up
    boton1 = 16
    boton2 = 19
    GPIO.setup(boton1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(boton2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    PERIODO_SCAN = 0.05
    
    # Variables para detección de flanco
    boton1_anterior = GPIO.input(boton1)
    boton2_anterior = GPIO.input(boton2)
    
    print("Programa con RPi.GPIO")
    print("GPIO16: enciende LEDs pares")
    print("GPIO19: enciende LEDs impares")
    
    try:
        while True:
            inicio_ciclo = time.time()
            
            # --- LEER ENTRADAS ---
            # En RPi.GPIO: 
            # - Con pull-up: 0 = pulsado, 1 = no pulsado
            boton1_actual = GPIO.input(boton1)
            boton2_actual = GPIO.input(boton2)
            
            # --- PROCESAR BOTÓN 1 (GPIO16) ---
            if boton1_anterior == 1 and boton1_actual == 0:  # Flanco bajada
                print("Botón 16 pulsado - LEDs pares")
                # Encender LEDs pares (20,22,24,26)
                for pin in [20, 22, 24, 26]:
                    GPIO.output(pin, GPIO.HIGH)
                # Apagar LEDs impares (21,23,25,27)
                for pin in [21, 23, 25, 27]:
                    GPIO.output(pin, GPIO.LOW)
            
            # --- PROCESAR BOTÓN 2 (GPIO19) ---
            if boton2_anterior == 1 and boton2_actual == 0:  # Flanco bajada
                print("Botón 19 pulsado - LEDs impares")
                # Apagar LEDs pares
                for pin in [20, 22, 24, 26]:
                    GPIO.output(pin, GPIO.LOW)
                # Encender LEDs impares
                for pin in [21, 23, 25, 27]:
                    GPIO.output(pin, GPIO.HIGH)
            
            boton1_anterior = boton1_actual
            boton2_anterior = boton2_actual
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        # --- LIMPIEZA (MUY IMPORTANTE) ---
        # Vuelve a configurar todos los pines como entradas sin pull-ups
        GPIO.cleanup()

if __name__ == "__main__":
    main()
    
    
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
    
    
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROGRAMA: Control de servomotor
Concepto: Mover servo a diferentes posiciones
Ejemplo típico: Barrera que se abre/cierra con botón y temporizador
"""

import time
from gpiozero import AngularServo, Button
from gpiozero.pins.pigpio import PiGPIOFactory
import threading

def main():
    # --- CONFIGURACIÓN IMPORTANTE ---
    # Para servos necesitamos PiGPIO factory (más preciso)
    # Antes de ejecutar: en terminal escribir "sudo pigpiod"
    
    try:
        factory = PiGPIOFactory()
    except:
        print("ERROR: ¿Has ejecutado 'sudo pigpiod' en terminal?")
        print("Ejecuta: sudo pigpiod")
        return
    
    # --- CONFIGURAR SERVO ---
    # Servo en GPIO14 (el pin central del conector DIG (SERVO))
    # Ángulos típicos: -90 a 90 grados
    # Pero pueden variar según el servo
    
    servo = AngularServo(
        14,  # GPIO14
        min_angle=-90,
        max_angle=90,
        min_pulse_width=0.0005,  # 0.5ms para 0 grados (ajustar)
        max_pulse_width=0.0025,  # 2.5ms para 180 grados (ajustar)
        pin_factory=factory
    )
    
    # Botones
    boton_abrir = Button(16)
    boton_cerrar = Button(17)
    
    # Posiciones
    POS_CERRADO = -45  # Grados (barrera cerrada)
    POS_ABIERTO = 45   # Grados (barrera abierta)
    
    # Variables
    posicion_actual = POS_CERRADO
    tiempo_apertura = 0
    TIEMPO_AUTO_CIERRE = 10  # segundos
    
    # Timer para cierre automático
    timer_cierre = None
    
    print("Programa de control de servomotor")
    print(f"GPIO16: abrir barrera ({POS_ABIERTO}°)")
    print(f"GPIO17: cerrar barrera ({POS_CERRADO}°)")
    print(f"Cierre automático después de {TIEMPO_AUTO_CIERRE}s")
    
    def cerrar_automatico():
        """Cierra la barrera automáticamente"""
        nonlocal posicion_actual
        if posicion_actual == POS_ABIERTO:
            servo.angle = POS_CERRADO
            posicion_actual = POS_CERRADO
            print("Cierre automático - Barrera CERRADA")
    
    def abrir_barrera():
        """Abre la barrera y programa cierre automático"""
        nonlocal posicion_actual, timer_cierre
        
        # Cancelar timer anterior si existe
        if timer_cierre and timer_cierre.is_alive():
            timer_cierre.cancel()
        
        # Abrir barrera
        servo.angle = POS_ABIERTO
        posicion_actual = POS_ABIERTO
        tiempo_apertura = time.time()
        print("Barrera ABIERTA")
        
        # Programar cierre automático
        timer_cierre = threading.Timer(TIEMPO_AUTO_CIERRE, cerrar_automatico)
        timer_cierre.daemon = True
        timer_cierre.start()
    
    def cerrar_barrera():
        """Cierra la barrera manualmente"""
        nonlocal posicion_actual, timer_cierre
        
        # Cancelar timer si existe
        if timer_cierre and timer_cierre.is_alive():
            timer_cierre.cancel()
        
        # Cerrar barrera
        servo.angle = POS_CERRADO
        posicion_actual = POS_CERRADO
        print("Barrera CERRADA")
    
    # Asignar callbacks
    boton_abrir.when_pressed = abrir_barrera
    boton_cerrar.when_pressed = cerrar_barrera
    
    # Posición inicial
    servo.angle = POS_CERRADO
    print("Posición inicial: CERRADA")
    
    try:
        # Bucle principal
        while True:
            time.sleep(0.1)
            
            # Opcional: mostrar tiempo restante si está abierta
            if posicion_actual == POS_ABIERTO:
                tiempo_transcurrido = time.time() - tiempo_apertura
                tiempo_restante = TIEMPO_AUTO_CIERRE - tiempo_transcurrido
                if tiempo_restante > 0 and int(tiempo_restante * 10) % 10 == 0:
                    print(f"Tiempo restante: {tiempo_restante:.1f}s")
            
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        # Detener servo (deja de enviar señal)
        servo.detach()

if __name__ == "__main__":
    main()
    
    
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