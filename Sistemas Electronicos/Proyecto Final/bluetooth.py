#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PIANO THEREMIN CON APRENDIZAJE INTERACTIVO VÍA BLUETOOTH
========================================================
Este programa convierte la Raspberry Pi en un instrumento musical interactivo
que se comunica por Bluetooth con tu móvil para ayudarte a aprender música.

FUNCIONALIDADES:
- El móvil envía una nota que debes tocar
- El sistema detecta qué nota estás tocando con la mano
- Evalúa si acertaste y envía feedback al móvil
- Lleva estadísticas de aciertos/fallos
- Modo libre para practicar sin presión

CONEXIONES BLUETOOTH:
- BT05 TXD -> GPIO22 (RXD de Raspberry)
- BT05 RXD -> GPIO23 (TXD de Raspberry)
- Alimentar BT05 a 3.3V (NO a 5V)
"""

import RPi.GPIO as GPIO
import time
import threading
import serial
import json
import random

# ================= CONFIGURACIÓN DE PINES =================
# Pines del sensor ultrasonidos
TRIG = 25      # Pin para enviar pulso ultrasónico
ECHO = 24      # Pin para recibir el eco

# Pin del altavoz
BUZZER = 27    # Pin PWM para generar sonido

# Pines de los botones físicos (como respaldo)
BOTON_GRABAR = 7      # No usado en modo aprendizaje, pero disponible
BOTON_REPRODUCIR = 16  # Cambiar entre modo libre/aprendizaje
BOTON_PARAR = 17      # Salir al menú principal
BOTON_BORRAR = 19     # Reiniciar estadísticas

# Pines de los LEDs indicadores
LED_GRABANDO = 20      # LED que indica modo aprendizaje activo
LED_REPRODUCIENDO = 21 # LED que indica esperando tu turno

# Pines para Bluetooth (conexión serie)
BT_TX = 22    # GPIO22 conectado al TXD del BT05 (Raspberry recibe datos)
BT_RX = 23    # GPIO23 conectado al RXD del BT05 (Raspberry envía datos)

# ================= NOTAS MUSICALES (Frecuencias en Hz) =================
# Diccionario que mapea cada nota a su frecuencia para generar el sonido
NOTAS = {
    'Do3': 130.81, 'Do#3': 138.59, 'Re3': 146.83, 'Re#3': 155.56,
    'Mi3': 164.81, 'Fa3': 174.61, 'Fa#3': 185.00, 'Sol3': 196.00,
    'Sol#3': 207.65, 'La3': 220.00, 'La#3': 233.08, 'Si3': 246.96,
    'Do4': 261.63, 'Do#4': 277.18, 'Re4': 293.66, 'Re#4': 311.13,
    'Mi4': 329.63, 'Fa4': 349.23, 'Fa#4': 369.99, 'Sol4': 392.00,
    'Sol#4': 415.30, 'La4': 440.00, 'La#4': 466.16, 'Si4': 493.88,
    'Do5': 523.25
}

# Escala principal para el modo aprendizaje (notas que el sistema puede pedir)
# Usamos una octava completa de Do mayor para empezar
ESCALA_APRENDIZAJE = ['Do4', 'Re4', 'Mi4', 'Fa4', 'Sol4', 'La4', 'Si4', 'Do5']

# ================= PARÁMETROS DEL SISTEMA =================
DISTANCIA_MIN = 5      # Distancia mínima en cm (mano más cerca = nota más grave)
DISTANCIA_MAX = 40     # Distancia máxima en cm (mano más lejos = nota más aguda)
DURACION_NOTA = 0.5    # Duración del pitido al tocar una nota (segundos)
DURACION_FEEDBACK = 1.0 # Duración del feedback sonoro de acierto/fallo

# ================= VARIABLES GLOBALES =================
pwm_buzzer = None           # Objeto PWM para controlar el altavoz
bluetooth = None            # Objeto para comunicación serie Bluetooth
modo_aprendizaje = False    # True = modo aprendizaje, False = modo libre
nota_a_tocar = None         # Nota que el sistema pide al usuario
puntuacion = 0              # Aciertos totales
intentos = 0                # Intentos totales
ultima_nota_tocada = None   # Última nota que detectó el sensor
esperando_respuesta = False # Flag para saber si estamos esperando que toque

# Lock para sincronizar hilos (evita conflictos)
lock = threading.Lock()

# ================= CONFIGURACIÓN DE BLUETOOTH =================

def emitir_telemetria(nota, distancia):
    """
    Emite un JSON compacto con el estado actual del instrumento.
    El dashboard Streamlit lo lee en tiempo real.
    """
    global modo_aprendizaje, nota_a_tocar, puntuacion, intentos, ESCALA_APRENDIZAJE
 
    modo_str = "APRENDIZAJE" if modo_aprendizaje else "LIBRE"
 
    payload = {
        "nota":       nota,
        "distancia":  round(distancia, 1),
        "modo":       modo_str,
        "escala":     ESCALA_APRENDIZAJE,
        "objetivo":   nota_a_tocar if modo_aprendizaje else None,
        "aciertos":   puntuacion,
        "intentos":   intentos,
    }
    enviar_por_bluetooth(payload)
 
def configurar_bluetooth():
    """
    Configura la comunicación serie con el módulo BT05
    El BT05 actúa como puente serie Bluetooth (SPP - Serial Port Profile)
    Velocidad por defecto: 9600 baudios
    """
    global bluetooth
    
    try:
        # Inicializar puerto serie en los pines GPIO22 (RX) y GPIO23 (TX)
        # Usamos UART por software (serial)
        bluetooth = serial.Serial(
            port='/dev/ttyS0',    # Puerto serie de Raspberry (UART)
            baudrate=9600,         # Misma velocidad que el BT05 por defecto
            timeout=1              # Timeout de 1 segundo para lectura
        )
        
        # Configurar pines como UART (esto lo maneja automático serial)
        print("✅ Módulo Bluetooth configurado correctamente")
        print("   Conecta desde tu móvil al dispositivo 'BT05'")
        print("   Usa una app de terminal Bluetooth (ej: 'Serial Bluetooth Terminal')")
        return True
        
    except Exception as e:
        print(f"⚠️ Error configurando Bluetooth: {e}")
        print("   El sistema funcionará sin Bluetooth")
        return False

def enviar_por_bluetooth(mensaje):
    """
    Envía un mensaje JSON por Bluetooth al móvil
    Args:
        mensaje: Diccionario con los datos a enviar
    """
    global bluetooth
    
    if bluetooth and bluetooth.is_open:
        try:
            # Convertir diccionario a JSON y añadir salto de línea
            datos_json = json.dumps(mensaje) + '\n'
            bluetooth.write(datos_json.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error enviando: {e}")
            return False
    return False

def recibir_por_bluetooth():
    """
    Recibe comandos del móvil vía Bluetooth
    Los comandos posibles:
    - {"comando": "iniciar"} -> Inicia modo aprendizaje
    - {"comando": "libre"} -> Cambia a modo libre
    - {"comando": "nota", "nota": "Do4"} -> Pide una nota específica
    - {"comando": "estadisticas"} -> Pide estadísticas
    - {"comando": "reset"} -> Reinicia estadísticas
    - {"comando": "siguiente"} -> Siguiente nota aleatoria
    """
    if bluetooth and bluetooth.is_open:
        try:
            if bluetooth.in_waiting > 0:
                linea = bluetooth.readline().decode('utf-8').strip()
                if linea:
                    return json.loads(linea)
        except json.JSONDecodeError:
            print(f"Mensaje no JSON: {linea}")
        except Exception as e:
            print(f"Error recibiendo: {e}")
    return None

# ================= CONFIGURACIÓN GPIO =================

def limpiar_gpio():
    """Limpia la configuración anterior de los pines GPIO"""
    try:
        GPIO.cleanup()
        time.sleep(0.3)
    except:
        pass

def setup():
    """Configura todos los pines GPIO y periféricos"""
    global pwm_buzzer
    
    # Limpiar configuración anterior
    limpiar_gpio()
    
    # Deshabilitar warnings molestos
    GPIO.setwarnings(False)
    
    # Configurar modo de numeración BCM (Broadcom)
    GPIO.setmode(GPIO.BCM)
    
    # Configurar pines del sensor ultrasonidos
    GPIO.setup(TRIG, GPIO.OUT, initial=GPIO.LOW)  # TRIG inicialmente en bajo
    GPIO.setup(ECHO, GPIO.IN)                     # ECHO como entrada
    
    # Configurar pin del altavoz como salida PWM
    GPIO.setup(BUZZER, GPIO.OUT, initial=GPIO.LOW)
    pwm_buzzer = GPIO.PWM(BUZZER, 440)  # Frecuencia inicial 440Hz (La4)
    pwm_buzzer.start(0)                 # Duty cycle 0% (silencio)
    
    # Configurar botones (como respaldo, aunque usamos Bluetooth)
    GPIO.setup(BOTON_GRABAR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BOTON_REPRODUCIR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BOTON_PARAR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BOTON_BORRAR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Configurar LEDs
    GPIO.setup(LED_GRABANDO, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(LED_REPRODUCIENDO, GPIO.OUT, initial=GPIO.LOW)
    
    # Configurar Bluetooth
    configurar_bluetooth()
    
    # Pequeña pausa para estabilizar
    time.sleep(0.5)
    
    # Mostrar información de inicio
    print("\n" + "="*60)
    print("🎹 PIANO THEREMIN - MODO APRENDIZAJE INTERACTIVO 🎵")
    print("="*60)
    print("\n📱 CONEXIÓN BLUETOOTH:")
    print("   1. Enciende el módulo BT05")
    print("   2. Desde tu móvil, busca dispositivo 'BT05' o 'HC-05'")
    print("   3. Conecta (código por defecto: 1234 o 0000)")
    print("   4. Abre una app de terminal Bluetooth")
    print("   5. Envía comandos JSON")
    print("\n🎮 CONTROLES POR BLUETOOTH:")
    print("   {\"comando\": \"iniciar\"}     - Inicia modo aprendizaje")
    print("   {\"comando\": \"libre\"}       - Modo libre (toca lo que quieras)")
    print("   {\"comando\": \"nota\", \"nota\": \"Do4\"} - Pide nota específica")
    print("   {\"comando\": \"siguiente\"}   - Siguiente nota aleatoria")
    print("   {\"comando\": \"estadisticas\"} - Muestra puntuación")
    print("   {\"comando\": \"reset\"}       - Reinicia estadísticas")
    print("\n🎵 CÓMO TOCAR:")
    print("   - Mano CERCA (5cm)  → Nota GRAVE (Do4)")
    print("   - Mano LEJOS (40cm) → Nota AGUDA (Do5)")
    print("   - Mueve la mano suavemente para cambiar notas")
    print("\n" + "="*60 + "\n")

# ================= MEDICIÓN DE DISTANCIA =================

def medir_distancia():
    """
    Mide la distancia usando el sensor ultrasónico HC-SR04
    Principio: Envía un pulso ultrasónico y mide el tiempo que tarda en volver
    Retorna: Distancia en centímetros (float) o -1 si hay error
    """
    try:
        # Asegurar que el pin TRIG está en bajo para empezar limpio
        GPIO.output(TRIG, False)
        time.sleep(0.05)  # Pausa de 50ms para estabilizar
        
        # Enviar pulso de 10 microsegundos por el pin TRIG
        GPIO.output(TRIG, True)
        time.sleep(0.00001)  # 10 microsegundos
        GPIO.output(TRIG, False)
        
        # Medir tiempo de inicio del eco
        inicio_eco = time.time()
        fin_eco = time.time()
        
        # Timeout de 20ms para evitar que el programa se cuelgue
        timeout = time.time() + 0.02
        
        # Esperar a que el pin ECHO se ponga en alto (inicio del eco)
        while GPIO.input(ECHO) == 0:
            inicio_eco = time.time()
            if time.time() > timeout:
                return -1
        
        # Esperar a que el pin ECHO se ponga en bajo (fin del eco)
        while GPIO.input(ECHO) == 1:
            fin_eco = time.time()
            if time.time() > timeout:
                return -1
        
        # Calcular duración del pulso de eco
        duracion = fin_eco - inicio_eco
        
        # Calcular distancia: velocidad del sonido = 34300 cm/s
        # Fórmula: distancia = (tiempo * velocidad) / 2 (porque va y vuelve)
        distancia = (duracion * 34300) / 2
        
        # Validar que la distancia esté en rango razonable
        if distancia < 0 or distancia > 500:
            return -1
            
        return distancia
        
    except Exception:
        return -1

def distancia_a_nota(distancia):
    """
    Convierte una distancia en centímetros a una nota musical
    Mapeo lineal: distancia pequeña (cerca) = nota grave
                   distancia grande (lejos) = nota aguda
    
    Args:
        distancia: Distancia en cm (entre DISTANCIA_MIN y DISTANCIA_MAX)
    
    Returns:
        Tupla (nombre_nota, índice_en_escala)
    """
    # Limitar distancia al rango configurado
    if distancia > DISTANCIA_MAX:
        distancia = DISTANCIA_MAX
    if distancia < DISTANCIA_MIN:
        distancia = DISTANCIA_MIN
    
    # Calcular el rango total de distancias
    rango = DISTANCIA_MAX - DISTANCIA_MIN
    
    # Calcular qué porcentaje del rango representa la distancia actual
    offset = distancia - DISTANCIA_MIN
    
    # Calcular índice de nota (0 = nota más grave, len-1 = nota más aguda)
    # Mapeo inverso: menor distancia = menor índice (nota grave)
    indice = int((offset / rango) * len(ESCALA_APRENDIZAJE))
    
    # Asegurar que el índice está dentro del rango válido
    if indice >= len(ESCALA_APRENDIZAJE):
        indice = len(ESCALA_APRENDIZAJE) - 1
    if indice < 0:
        indice = 0
    
    return ESCALA_APRENDIZAJE[indice], indice

# ================= GENERACIÓN DE SONIDO =================

def tocar_nota(nota, duracion=None):
    """
    Genera el sonido de una nota musical mediante PWM
    
    Args:
        nota: Nombre de la nota (ej: 'Do4')
        duracion: Duración en segundos (None = sonido continuo)
    """
    try:
        # Obtener frecuencia de la nota desde el diccionario
        frecuencia = NOTAS[nota]
        
        # Configurar el PWM con la frecuencia deseada
        pwm_buzzer.ChangeFrequency(frecuencia)
        
        # Activar sonido con volumen medio (50% duty cycle)
        pwm_buzzer.ChangeDutyCycle(50)
        
        # Si se especificó duración, apagar después del tiempo
        if duracion:
            time.sleep(duracion)
            pwm_buzzer.ChangeDutyCycle(0)
            
    except Exception as e:
        print(f"Error reproduciendo nota {nota}: {e}")

def silencio():
    """Apaga inmediatamente cualquier sonido que esté sonando"""
    try:
        pwm_buzzer.ChangeDutyCycle(0)
    except:
        pass

def feedback_acierto():
    """
    Feedback positivo cuando el usuario acierta una nota
    Suena un acorde alegre (Do mayor ascendente)
    """
    print("🎉 ¡CORRECTO! 🎉")
    
    # Enviar mensaje por Bluetooth
    enviar_por_bluetooth({"estado": "acierto", "mensaje": "¡Correcto!"})
    
    # LED parpadea rápido indicando éxito
    for _ in range(3):
        GPIO.output(LED_REPRODUCIENDO, True)
        time.sleep(0.1)
        GPIO.output(LED_REPRODUCIENDO, False)
        time.sleep(0.1)
    
    # Tocar un acorde de celebración: Do-Mi-Sol ascendente
    tocar_nota('Do4', 0.3)
    tocar_nota('Mi4', 0.3)
    tocar_nota('Sol4', 0.5)
    silencio()

def feedback_fallo(nota_esperada, nota_tocada):
    """
    Feedback negativo cuando el usuario falla
    
    Args:
        nota_esperada: Nota que debía tocar
        nota_tocada: Nota que realmente tocó
    """
    print(f"❌ FALLO - Esperaba: {nota_esperada}, tocaste: {nota_tocada} ❌")
    
    # Enviar mensaje por Bluetooth con la corrección
    enviar_por_bluetooth({
        "estado": "fallo",
        "esperada": nota_esperada,
        "tocada": nota_tocada,
        "mensaje": f"Esperaba {nota_esperada}, tocaste {nota_tocada}"
    })
    
    # LED rojo parpadeo lento indicando error
    for _ in range(2):
        GPIO.output(LED_GRABANDO, True)
        time.sleep(0.3)
        GPIO.output(LED_GRABANDO, False)
        time.sleep(0.2)
    
    # Tocar un sonido de error (descendente grave)
    tocar_nota('Do4', 0.2)
    tocar_nota('Si3', 0.2)
    tocar_nota('Sol3', 0.3)
    silencio()
    
    # Tocar la nota correcta para que el usuario la escuche
    print(f"🎵 La nota correcta es: {nota_esperada}")
    time.sleep(0.5)
    tocar_nota(nota_esperada, 0.8)

# ================= LÓGICA DEL MODO APRENDIZAJE =================

def nueva_nota_desafio():
    """
    Genera una nueva nota aleatoria para el desafío
    También puede recibir nota específica desde Bluetooth
    """
    global nota_a_tocar, esperando_respuesta, intentos
    
    with lock:
        # Elegir nota aleatoria de la escala
        nota_a_tocar = random.choice(ESCALA_APRENDIZAJE)
        esperando_respuesta = True
        
        # Enviar la nota por Bluetooth al móvil
        enviar_por_bluetooth({
            "comando": "desafio",
            "nota": nota_a_tocar,
            "intento": intentos + 1
        })
        
        # Anunciar la nota por el altavoz (para que el usuario la escuche)
        print(f"\n🎯 ¡TU TURNO! Toca la nota: {nota_a_tocar}")
        tocar_nota(nota_a_tocar, 0.5)
        
        # LED parpadea indicando que esperamos tu respuesta
        GPIO.output(LED_REPRODUCIENDO, True)

def verificar_respuesta(nota_tocada):
    """
    Verifica si la nota que tocó el usuario es correcta
    
    Args:
        nota_tocada: Nota detectada por el sensor
    """
    global puntuacion, intentos, esperando_respuesta, nota_a_tocar
    
    with lock:
        if not esperando_respuesta:
            return
        
        intentos += 1
        esperando_respuesta = False
        GPIO.output(LED_REPRODUCIENDO, False)
        
        # Comparar nota tocada con nota esperada
        if nota_tocada == nota_a_tocar:
            puntuacion += 1
            feedback_acierto()
        else:
            feedback_fallo(nota_a_tocar, nota_tocada)
        
        # Enviar estadísticas actualizadas
        porcentaje = (puntuacion / intentos) * 100 if intentos > 0 else 0
        enviar_por_bluetooth({
            "estadisticas": {
                "aciertos": puntuacion,
                "intentos": intentos,
                "porcentaje": f"{porcentaje:.1f}"
            }
        })
        
        # Pequeña pausa antes de la siguiente nota
        time.sleep(1)
        
        # Generar siguiente nota
        nueva_nota_desafio()

def procesar_comando_bluetooth():
    """
    Procesa comandos recibidos desde el móvil vía Bluetooth
    """
    global modo_aprendizaje, nota_a_tocar, puntuacion, intentos
    
    comando = recibir_por_bluetooth()
    
    if comando:
        cmd = comando.get('comando')
        
        if cmd == 'iniciar':
            # Iniciar modo aprendizaje
            with lock:
                modo_aprendizaje = True
                puntuacion = 0
                intentos = 0
                GPIO.output(LED_GRABANDO, True)
                print("\n📚 MODO APRENDIZAJE ACTIVADO")
                nueva_nota_desafio()
            enviar_por_bluetooth({"estado": "aprendizaje_iniciado"})
            
        elif cmd == 'libre':
            # Cambiar a modo libre
            with lock:
                modo_aprendizaje = False
                esperando_respuesta = False
                GPIO.output(LED_GRABANDO, False)
                GPIO.output(LED_REPRODUCIENDO, False)
                print("\n🎵 MODO LIBRE ACTIVADO - Toca lo que quieras")
            enviar_por_bluetooth({"estado": "modo_libre"})
            
        elif cmd == 'nota':
            # Solicitar nota específica
            nota_especifica = comando.get('nota')
            if nota_especifica in NOTAS:
                with lock:
                    if modo_aprendizaje:
                        nota_a_tocar = nota_especifica
                        esperando_respuesta = True
                        GPIO.output(LED_REPRODUCIENDO, True)
                        print(f"\n🎯 Nota específica: {nota_a_tocar}")
                        tocar_nota(nota_a_tocar, 0.5)
                        enviar_por_bluetooth({"estado": "nota_especifica", "nota": nota_especifica})
            else:
                enviar_por_bluetooth({"error": f"Nota {nota_especifica} no válida"})
                
        elif cmd == 'siguiente':
            # Saltar a siguiente nota (cuenta como fallo si no respondió)
            with lock:
                if esperando_respuesta:
                    intentos += 1
                    esperando_respuesta = False
                    GPIO.output(LED_REPRODUCIENDO, False)
                    feedback_fallo(nota_a_tocar, "sin respuesta")
                    nueva_nota_desafio()
                    
        elif cmd == 'estadisticas':
            # Enviar estadísticas actuales
            porcentaje = (puntuacion / intentos) * 100 if intentos > 0 else 0
            enviar_por_bluetooth({
                "estadisticas": {
                    "aciertos": puntuacion,
                    "intentos": intentos,
                    "porcentaje": f"{porcentaje:.1f}"
                }
            })
            
        elif cmd == 'reset':
            # Reiniciar estadísticas
            with lock:
                puntuacion = 0
                intentos = 0
                if modo_aprendizaje:
                    esperando_respuesta = False
                    GPIO.output(LED_REPRODUCIENDO, False)
                    nueva_nota_desafio()
            enviar_por_bluetooth({"estado": "estadisticas_reseteadas"})

# ================= BUCLE PRINCIPAL =================

def bucle_principal():
    """
    Bucle principal del programa
    - Lee constantemente la distancia del sensor
    - Detecta qué nota está tocando el usuario
    - En modo aprendizaje: verifica si la nota es correcta
    - En modo libre: simplemente reproduce la nota
    - Procesa comandos Bluetooth
    """
    global ultima_nota_tocada
    
    print("🎹 Sistema listo. Esperando comandos...\n")
    
    while True:
        # Procesar comandos Bluetooth (no bloqueante)
        procesar_comando_bluetooth()
        
        # Verificar botones físicos (opcional, como respaldo)
        # Botón REPRODUCIR (GPIO16) cambia entre modo libre/aprendizaje
        if GPIO.input(BOTON_REPRODUCIR) == GPIO.LOW:
            time.sleep(0.3)  # Debounce
            with lock:
                modo_aprendizaje = not modo_aprendizaje
                if modo_aprendizaje:
                    puntuacion = 0
                    intentos = 0
                    GPIO.output(LED_GRABANDO, True)
                    print("\n📚 MODO APRENDIZAJE (por botón)")
                    nueva_nota_desafio()
                else:
                    esperando_respuesta = False
                    GPIO.output(LED_GRABANDO, False)
                    GPIO.output(LED_REPRODUCIENDO, False)
                    print("\n🎵 MODO LIBRE (por botón)")
        
        # Botón PARAR (GPIO17) sale al menú
        if GPIO.input(BOTON_PARAR) == GPIO.LOW:
            time.sleep(0.3)
            print("\n⏸️ Saliendo del modo actual...")
            break
        
        # Medir distancia actual
        distancia = medir_distancia()
        
        if distancia > 0:
            # Convertir distancia a nota musical
            nota_actual, indice = distancia_a_nota(distancia)
            
            # Mostrar información en consola (feedback visual)
            barra = "█" * int((indice / (len(ESCALA_APRENDIZAJE) - 1)) * 20)
            barra += "░" * (20 - len(barra))
            
            estado = "📚[APREND]" if modo_aprendizaje else "🎵[LIBRE]"
            if modo_aprendizaje and esperando_respuesta:
                estado += f" 🎯OBJ: {nota_a_tocar}"
            
            print(f"{estado} Dist: {distancia:5.1f}cm | Nota: {nota_actual:>5} | {barra}", end='\r')
            
            # Detectar cambio de nota (evita repetir la misma nota constantemente)
            if nota_actual != ultima_nota_tocada:
                # Tocar la nota (en modo libre o modo aprendizaje, siempre suena)
                tocar_nota(nota_actual, DURACION_NOTA)
                
                # Si estamos en modo aprendizaje y esperando respuesta, verificar
                if modo_aprendizaje and esperando_respuesta:
                    verificar_respuesta(nota_actual)
                
                ultima_nota_tocada = nota_actual
                emitir_telemetria(nota_actual, distancia)
            else:
                # Pequeña pausa para no saturar el procesador
                time.sleep(0.03)
        else:
            # Error en medición, esperar y reintentar
            time.sleep(0.1)

def menu_principal():
    """
    Menú principal del programa
    """
    try:
        while True:
            print("\n" + "="*50)
            print("🎹 PIANO THEREMIN - APRENDIZAJE INTERACTIVO 🎵")
            print("="*50)
            print("1. Iniciar modo aprendizaje")
            print("2. Modo libre (tocar sin presión)")
            print("3. Configurar escala")
            print("4. Ver estadísticas")
            print("5. Salir")
            
            opcion = input("\nSelecciona una opción (1-5): ")
            
            if opcion == '1':
                global modo_aprendizaje, puntuacion, intentos, nota_a_tocar, esperando_respuesta
                modo_aprendizaje = True
                puntuacion = 0
                intentos = 0
                GPIO.output(LED_GRABANDO, True)
                print("\n📚 MODO APRENDIZAJE ACTIVADO")
                nueva_nota_desafio()
                bucle_principal()
                
            elif opcion == '2':
                modo_aprendizaje = False
                GPIO.output(LED_GRABANDO, False)
                GPIO.output(LED_REPRODUCIENDO, False)
                print("\n🎵 MODO LIBRE - Toca lo que quieras")
                bucle_principal()
                
            elif opcion == '3':
                configurar_escala()
                
            elif opcion == '4':
                if intentos > 0:
                    porcentaje = (puntuacion / intentos) * 100
                    print(f"\n📊 ESTADÍSTICAS:")
                    print(f"   Aciertos: {puntuacion}")
                    print(f"   Intentos: {intentos}")
                    print(f"   Porcentaje: {porcentaje:.1f}%")
                else:
                    print("\n📊 Aún no hay estadísticas. Empieza a practicar!")
                    
            elif opcion == '5':
                print("\n👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción no válida")
                
    except KeyboardInterrupt:
        print("\n\n👋 Programa terminado por usuario")
    finally:
        silencio()
        if pwm_buzzer:
            pwm_buzzer.stop()
        if bluetooth and bluetooth.is_open:
            bluetooth.close()
        GPIO.cleanup()
        print("✅ Sistema apagado correctamente")

def configurar_escala():
    """Permite cambiar la escala musical"""
    global ESCALA_APRENDIZAJE
    
    print("\n🎼 SELECCIONA UNA ESCALA:")
    print("1. Do Mayor (Do4,Re4,Mi4,Fa4,Sol4,La4,Si4,Do5)")
    print("2. Pentatónica (Do4,Re4,Mi4,Sol4,La4,Do5)")
    print("3. Blues (Do4,Re#4,Fa4,Sol4,Sol#4,Si4,Do5)")
    print("4. Cromática (todas las notas - más difícil)")
    
    opcion = input("\nOpción (1-4): ")
    
    if opcion == '1':
        ESCALA_APRENDIZAJE = ['Do4', 'Re4', 'Mi4', 'Fa4', 'Sol4', 'La4', 'Si4', 'Do5']
    elif opcion == '2':
        ESCALA_APRENDIZAJE = ['Do4', 'Re4', 'Mi4', 'Sol4', 'La4', 'Do5']
    elif opcion == '3':
        ESCALA_APRENDIZAJE = ['Do4', 'Re#4', 'Fa4', 'Sol4', 'Sol#4', 'Si4', 'Do5']
    elif opcion == '4':
        ESCALA_APRENDIZAJE = ['Do4', 'Do#4', 'Re4', 'Re#4', 'Mi4', 'Fa4', 
                              'Fa#4', 'Sol4', 'Sol#4', 'La4', 'La#4', 'Si4', 'Do5']
    else:
        print("Opción no válida, manteniendo escala actual")
    
    print(f"✅ Escala actualizada: {' → '.join(ESCALA_APRENDIZAJE)}")

# ================= PUNTO DE ENTRADA =================
if __name__ == "__main__":
    setup()
    menu_principal()