#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXAMEN: Cerradura de seguridad digital
Ejercicios típicos:
- Contraseña de 2 dígitos (0-3) con pulsadores GPIO16 y GPIO17
- Cada dígito se muestra en 2 LEDs: (20,21) para dígito1, (22,23) para dígito2
- Botón validar: GPIO19
- LED estado: GPIO27 (desbloqueado), GPIO26 (bloqueado)
- Añadir tiempo límite de 10s para desbloquear
- LED bloqueo parpadea: 1Hz tras 1er fallo, 2Hz tras 2º fallo
- Añadir NTC para atenuar LEDs al 50% con temperatura alta
"""

import time
from gpiozero import LED, Button, LEDBoard, PWMLED, MCP3008

# ============================================================
# PARTE 1: Versión básica (3 puntos)
# ============================================================

def cerradura_basica():
    """
    Sistema de cierre básico:
    - Estado inicial: desbloqueado (LED27 encendido)
    - Bloquear: introducir dígitos y pulsar GPIO19
    - Dígitos: GPIO16 (dígito1), GPIO17 (dígito2)
    - Visualización: dígito1 en GPIO20-21, dígito2 en GPIO22-23
    - Al validar: se apagan todos menos GPIO26 (bloqueado)
    """
    # LEDs de estado
    led_desbloqueado = LED(27)
    led_bloqueado = LED(26)
    
    # LEDs para dígitos (usamos LEDBoard para grupos)
    digito1_leds = LEDBoard(20, 21)  # LSB, MSB
    digito2_leds = LEDBoard(22, 23)  # LSB, MSB
    
    # Pulsadores
    boton_digito1 = Button(16)
    boton_digito2 = Button(17)
    boton_validar = Button(19)
    
    # Estados del sistema
    sistema_bloqueado = False
    password_guardada = [0, 0]  # [dígito1, dígito2]
    password_intento = [0, 0]
    
    # Detección de flanco
    ant_d1 = boton_digito1.is_pressed
    ant_d2 = boton_digito2.is_pressed
    ant_val = boton_validar.is_pressed
    
    PERIODO_SCAN = 0.05
    
    def mostrar_digito(leds, valor):
        """Muestra dígito 0-3 en 2 LEDs"""
        bits = [(valor >> i) & 1 for i in range(2)]
        for i, led in enumerate(leds):
            if bits[i]:
                led.on()
            else:
                led.off()
    
    def mostrar_intento():
        mostrar_digito(digito1_leds, password_intento[0])
        mostrar_digito(digito2_leds, password_intento[1])
    
    # Estado inicial
    led_desbloqueado.on()
    led_bloqueado.off()
    mostrar_intento()
    
    print("Cerradura básica - Estado inicial: DESBLOQUEADO")
    
    try:
        while True:
            inicio_ciclo = time.time()
            
            # Botón dígito 1
            act_d1 = boton_digito1.is_pressed
            if ant_d1 and not act_d1:
                password_intento[0] = (password_intento[0] + 1) % 4
                print(f"Dígito1: {password_intento[0]}")
                mostrar_digito(digito1_leds, password_intento[0])
            ant_d1 = act_d1
            
            # Botón dígito 2
            act_d2 = boton_digito2.is_pressed
            if ant_d2 and not act_d2:
                password_intento[1] = (password_intento[1] + 1) % 4
                print(f"Dígito2: {password_intento[1]}")
                mostrar_digito(digito2_leds, password_intento[1])
            ant_d2 = act_d2
            
            # Botón validar
            act_val = boton_validar.is_pressed
            if ant_val and not act_val:
                if not sistema_bloqueado:
                    # BLOQUEAR
                    password_guardada = password_intento.copy()
                    sistema_bloqueado = True
                    
                    led_desbloqueado.off()
                    led_bloqueado.on()
                    
                    print(f"Sistema BLOQUEADO con password: {password_guardada}")
                    
                else:
                    # INTENTAR DESBLOQUEAR
                    if password_intento == password_guardada:
                        sistema_bloqueado = False
                        led_bloqueado.off()
                        led_desbloqueado.on()
                        print("¡Sistema DESBLOQUEADO!")
                    else:
                        print(f"Contraseña incorrecta: {password_intento}")
                        # Los dígitos se mantienen para reintentar
            ant_val = act_val
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        led_desbloqueado.off()
        led_bloqueado.off()
        digito1_leds.off()
        digito2_leds.off()

# ============================================================
# PARTE 2: Con tiempo límite y parpadeo por fallos (4 puntos)
# ============================================================

def cerradura_tiempo():
    """
    Añade:
    - Tiempo límite de 10s para desbloquear (desde primera pulsación)
    - LED bloqueo parpadea: 1Hz tras 1er fallo, 2Hz tras 2º fallo
    """
    led_desbloqueado = LED(27)
    led_bloqueado = LED(26)  # Este parpadeará
    
    digito1_leds = LEDBoard(20, 21)
    digito2_leds = LEDBoard(22, 23)
    
    boton_digito1 = Button(16)
    boton_digito2 = Button(17)
    boton_validar = Button(19)
    
    sistema_bloqueado = False
    password_guardada = [0, 0]
    password_intento = [0, 0]
    
    # Variables para tiempo límite
    tiempo_primera_pulsacion = 0
    tiempo_activo = False
    TIEMPO_LIMITE = 10
    
    # Variables para control de fallos
    contador_fallos = 0  # 0, 1, 2
    
    # Variables para parpadeo
    tiempo_ultimo_parpadeo = time.time()
    estado_parpadeo = True
    periodo_parpadeo = 0  # Se actualizará según fallos
    
    ant_d1 = boton_digito1.is_pressed
    ant_d2 = boton_digito2.is_pressed
    ant_val = boton_validar.is_pressed
    
    PERIODO_SCAN = 0.05
    
    def mostrar_digito(leds, valor):
        bits = [(valor >> i) & 1 for i in range(2)]
        for i, led in enumerate(leds):
            if bits[i]:
                led.on()
            else:
                led.off()
    
    def mostrar_intento():
        mostrar_digito(digito1_leds, password_intento[0])
        mostrar_digito(digito2_leds, password_intento[1])
    
    def reiniciar_intento():
        nonlocal password_intento, tiempo_primera_pulsacion, tiempo_activo
        password_intento = [0, 0]
        mostrar_intento()
        tiempo_primera_pulsacion = 0
        tiempo_activo = False
    
    # Estado inicial
    led_desbloqueado.on()
    led_bloqueado.off()
    mostrar_intento()
    
    print("Cerradura con tiempo - Estado inicial: DESBLOQUEADO")
    
    try:
        while True:
            inicio_ciclo = time.time()
            tiempo_actual = time.time()
            
            # Actualizar período según fallos
            if contador_fallos == 1:
                periodo_parpadeo = 0.5  # 1Hz
            elif contador_fallos == 2:
                periodo_parpadeo = 0.25  # 2Hz
            else:
                periodo_parpadeo = 0
            
            # Control de parpadeo del LED de bloqueo
            if sistema_bloqueado and periodo_parpadeo > 0:
                if tiempo_actual - tiempo_ultimo_parpadeo >= periodo_parpadeo:
                    estado_parpadeo = not estado_parpadeo
                    tiempo_ultimo_parpadeo = tiempo_actual
                    
                    if estado_parpadeo:
                        led_bloqueado.on()
                    else:
                        led_bloqueado.off()
            elif sistema_bloqueado:
                led_bloqueado.on()
            
            # Botón dígito 1
            act_d1 = boton_digito1.is_pressed
            if ant_d1 and not act_d1:
                if sistema_bloqueado:
                    if not tiempo_activo:
                        tiempo_primera_pulsacion = tiempo_actual
                        tiempo_activo = True
                    
                    password_intento[0] = (password_intento[0] + 1) % 4
                    mostrar_digito(digito1_leds, password_intento[0])
            ant_d1 = act_d1
            
            # Botón dígito 2
            act_d2 = boton_digito2.is_pressed
            if ant_d2 and not act_d2:
                if sistema_bloqueado:
                    if not tiempo_activo:
                        tiempo_primera_pulsacion = tiempo_actual
                        tiempo_activo = True
                    
                    password_intento[1] = (password_intento[1] + 1) % 4
                    mostrar_digito(digito2_leds, password_intento[1])
            ant_d2 = act_d2
            
            # Botón validar
            act_val = boton_validar.is_pressed
            if ant_val and not act_val:
                if not sistema_bloqueado:
                    # BLOQUEAR
                    password_guardada = password_intento.copy()
                    sistema_bloqueado = True
                    contador_fallos = 0
                    
                    led_desbloqueado.off()
                    led_bloqueado.on()
                    estado_parpadeo = True
                    
                    reiniciar_intento()
                    print(f"BLOQUEADO: {password_guardada}")
                    
                else:
                    # INTENTAR DESBLOQUEAR
                    if password_intento == password_guardada:
                        sistema_bloqueado = False
                        contador_fallos = 0
                        led_bloqueado.off()
                        led_desbloqueado.on()
                        reiniciar_intento()
                        print("¡DESBLOQUEADO!")
                    else:
                        contador_fallos = min(contador_fallos + 1, 2)
                        print(f"FALLO {contador_fallos}: {password_intento}")
            ant_val = act_val
            
            # Comprobar tiempo límite
            if sistema_bloqueado and tiempo_activo:
                tiempo_transcurrido = tiempo_actual - tiempo_primera_pulsacion
                if tiempo_transcurrido > TIEMPO_LIMITE:
                    print("Tiempo límite excedido - FALLO")
                    contador_fallos = min(contador_fallos + 1, 2)
                    reiniciar_intento()
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        led_desbloqueado.off()
        led_bloqueado.off()
        digito1_leds.off()
        digito2_leds.off()

# ============================================================
# PARTE 3: Con NTC - Atenuación por temperatura (3 puntos)
# ============================================================

def cerradura_temperatura():
    """
    Añade sensor NTC:
    - Si temperatura alta: LEDs de contraseña al 50% de intensidad
    - Usar PWMLED para control de intensidad
    """
    # LEDs de estado (normales)
    led_desbloqueado = LED(27)
    led_bloqueado = LED(26)
    
    # LEDs para dígitos (con PWM para control de intensidad)
    digito1_pwm = [PWMLED(20), PWMLED(21)]
    digito2_pwm = [PWMLED(22), PWMLED(23)]
    
    boton_digito1 = Button(16)
    boton_digito2 = Button(17)
    boton_validar = Button(19)
    
    # Sensor NTC en CH1 (divisor de tensión)
    ntc = MCP3008(channel=1)
    
    sistema_bloqueado = False
    password_guardada = [0, 0]
    password_intento = [0, 0]
    
    tiempo_primera_pulsacion = 0
    tiempo_activo = False
    TIEMPO_LIMITE = 10
    
    contador_fallos = 0
    tiempo_ultimo_parpadeo = time.time()
    estado_parpadeo = True
    periodo_parpadeo = 0
    
    # Variables para temperatura
    UMBRAL_TEMP = 2.0  # Voltios: por encima = temperatura alta
    INTENSIDAD_NORMAL = 1.0
    INTENSIDAD_REDUCIDA = 0.5
    
    ant_d1 = boton_digito1.is_pressed
    ant_d2 = boton_digito2.is_pressed
    ant_val = boton_validar.is_pressed
    
    PERIODO_SCAN = 0.05
    
    def mostrar_digito_pwm(leds, valor, intensidad):
        """Muestra dígito con PWM para control de brillo"""
        bits = [(valor >> i) & 1 for i in range(2)]
        for i, led in enumerate(leds):
            if bits[i]:
                led.value = intensidad
            else:
                led.value = 0
    
    def mostrar_intento_con_intensidad(intensidad):
        mostrar_digito_pwm(digito1_pwm, password_intento[0], intensidad)
        mostrar_digito_pwm(digito2_pwm, password_intento[1], intensidad)
    
    def reiniciar_intento():
        nonlocal password_intento, tiempo_primera_pulsacion, tiempo_activo
        password_intento = [0, 0]
        # La intensidad se aplicará en el bucle
        tiempo_primera_pulsacion = 0
        tiempo_activo = False
    
    # Estado inicial
    led_desbloqueado.on()
    led_bloqueado.off()
    
    print("Cerradura con NTC - Estado inicial: DESBLOQUEADO")
    
    try:
        while True:
            inicio_ciclo = time.time()
            tiempo_actual = time.time()
            
            # Leer temperatura
            voltios_temp = ntc.voltage
            temperatura_alta = (voltios_temp > UMBRAL_TEMP)
            
            # Determinar intensidad
            if temperatura_alta:
                intensidad = INTENSIDAD_REDUCIDA
            else:
                intensidad = INTENSIDAD_NORMAL
            
            # Actualizar LEDs de dígitos con la intensidad correspondiente
            mostrar_intento_con_intensidad(intensidad)
            
            # Mostrar cambio de temperatura
            if int(tiempo_actual * 10) % 10 == 0:
                print(f"Temp: {voltios_temp:.2f}V - Intensidad: {intensidad*100:.0f}%")
            
            # Actualizar período según fallos
            if contador_fallos == 1:
                periodo_parpadeo = 0.5
            elif contador_fallos == 2:
                periodo_parpadeo = 0.25
            else:
                periodo_parpadeo = 0
            
            # Control de parpadeo del LED de bloqueo
            if sistema_bloqueado and periodo_parpadeo > 0:
                if tiempo_actual - tiempo_ultimo_parpadeo >= periodo_parpadeo:
                    estado_parpadeo = not estado_parpadeo
                    tiempo_ultimo_parpadeo = tiempo_actual
                    
                    if estado_parpadeo:
                        led_bloqueado.on()
                    else:
                        led_bloqueado.off()
            elif sistema_bloqueado:
                led_bloqueado.on()
            
            # Botón dígito 1
            act_d1 = boton_digito1.is_pressed
            if ant_d1 and not act_d1:
                if sistema_bloqueado:
                    if not tiempo_activo:
                        tiempo_primera_pulsacion = tiempo_actual
                        tiempo_activo = True
                    
                    password_intento[0] = (password_intento[0] + 1) % 4
                    # No actualizamos aquí porque ya se actualiza cada ciclo
            ant_d1 = act_d1
            
            # Botón dígito 2
            act_d2 = boton_digito2.is_pressed
            if ant_d2 and not act_d2:
                if sistema_bloqueado:
                    if not tiempo_activo:
                        tiempo_primera_pulsacion = tiempo_actual
                        tiempo_activo = True
                    
                    password_intento[1] = (password_intento[1] + 1) % 4
            ant_d2 = act_d2
            
            # Botón validar
            act_val = boton_validar.is_pressed
            if ant_val and not act_val:
                if not sistema_bloqueado:
                    password_guardada = password_intento.copy()
                    sistema_bloqueado = True
                    contador_fallos = 0
                    
                    led_desbloqueado.off()
                    led_bloqueado.on()
                    estado_parpadeo = True
                    
                    reiniciar_intento()
                    print(f"BLOQUEADO: {password_guardada}")
                    
                else:
                    if password_intento == password_guardada:
                        sistema_bloqueado = False
                        contador_fallos = 0
                        led_bloqueado.off()
                        led_desbloqueado.on()
                        reiniciar_intento()
                        print("¡DESBLOQUEADO!")
                    else:
                        contador_fallos = min(contador_fallos + 1, 2)
                        print(f"FALLO {contador_fallos}: {password_intento}")
            ant_val = act_val
            
            # Comprobar tiempo límite
            if sistema_bloqueado and tiempo_activo:
                tiempo_transcurrido = tiempo_actual - tiempo_primera_pulsacion
                if tiempo_transcurrido > TIEMPO_LIMITE:
                    print("Tiempo límite excedido - FALLO")
                    contador_fallos = min(contador_fallos + 1, 2)
                    reiniciar_intento()
            
            # Mantener período
            tiempo_ejecucion = time.time() - inicio_ciclo
            if tiempo_ejecucion < PERIODO_SCAN:
                time.sleep(PERIODO_SCAN - tiempo_ejecucion)
                
    except KeyboardInterrupt:
        print("\nPrograma terminado")
    finally:
        led_desbloqueado.off()
        led_bloqueado.off()
        for led in digito1_pwm + digito2_pwm:
            led.off()

if __name__ == "__main__":
    # Elegir versión
    # cerradura_basica()
    # cerradura_tiempo()
    cerradura_temperatura()