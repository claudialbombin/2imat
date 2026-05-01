#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import threading

# ================= CONFIGURACIÓN DE PINES =================
TRIG = 25
ECHO = 24
BUZZER = 27

# Botones disponibles
BOTON_GRABAR = 7
BOTON_REPRODUCIR = 16
BOTON_PARAR = 17      # Botón adicional para parar reproducción
BOTON_BORRAR = 19     # Botón adicional para borrar secuencia

# LEDs
LED_GRABANDO = 20
LED_REPRODUCIENDO = 21

# ================= NOTAS MUSICALES =================
NOTAS = {
    'Do3': 130.81, 'Do#3': 138.59, 'Re3': 146.83, 'Re#3': 155.56,
    'Mi3': 164.81, 'Fa3': 174.61, 'Fa#3': 185.00, 'Sol3': 196.00,
    'Sol#3': 207.65, 'La3': 220.00, 'La#3': 233.08, 'Si3': 246.96,
    'Do4': 261.63, 'Do#4': 277.18, 'Re4': 293.66, 'Re#4': 311.13,
    'Mi4': 329.63, 'Fa4': 349.23, 'Fa#4': 369.99, 'Sol4': 392.00,
    'Sol#4': 415.30, 'La4': 440.00, 'La#4': 466.16, 'Si4': 493.88,
    'Do5': 523.25
}

# Escala por defecto (Do mayor)
ESCALA = ['Do3', 'Re3', 'Mi3', 'Fa3', 'Sol3', 'La3', 'Si3',
          'Do4', 'Re4', 'Mi4', 'Fa4', 'Sol4', 'La4', 'Si4', 'Do5']

# ================= PARÁMETROS =================
DISTANCIA_MIN = 5
DISTANCIA_MAX = 40
DURACION_NOTA = 0.3
MODO_PIANO = True

# ================= VARIABLES GLOBALES =================
pwm_buzzer = None
grabando = False
reproduciendo = False
secuencia_grabada = []
ultima_nota = None
lock = threading.Lock()

# Variables para debounce de botones
ultimo_tiempo_boton = {BOTON_GRABAR: 0, BOTON_REPRODUCIR: 0, 
                        BOTON_PARAR: 0, BOTON_BORRAR: 0}
DEBOUNCE_TIME = 0.3  # 300ms

# ================= LIMPIAR GPIO =================
def limpiar_gpio():
    """Limpia la configuración GPIO anterior"""
    try:
        GPIO.cleanup()
        time.sleep(0.3)
    except:
        pass

# ================= SETUP GPIO =================
def setup():
    """Configura todos los pines GPIO"""
    global pwm_buzzer
    
    # Limpiar configuración anterior
    limpiar_gpio()
    
    # Deshabilitar warnings
    GPIO.setwarnings(False)
    
    # Configurar modo
    GPIO.setmode(GPIO.BCM)
    
    # Configurar sensor ultrasonidos
    GPIO.setup(TRIG, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(ECHO, GPIO.IN)
    
    # Configurar altavoz
    GPIO.setup(BUZZER, GPIO.OUT, initial=GPIO.LOW)
    pwm_buzzer = GPIO.PWM(BUZZER, 440)
    pwm_buzzer.start(0)
    
    # Configurar botones con pull-up
    GPIO.setup(BOTON_GRABAR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BOTON_REPRODUCIR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BOTON_PARAR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BOTON_BORRAR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # Configurar LEDs
    GPIO.setup(LED_GRABANDO, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(LED_REPRODUCIENDO, GPIO.OUT, initial=GPIO.LOW)
    
    time.sleep(0.1)
    
    print("🎹 PIANO-THEREMIN CON GRABACIÓN 🎵")
    print("="*55)
    print(f"Rango: {DISTANCIA_MIN}cm - {DISTANCIA_MAX}cm")
    print(f"Escala: {ESCALA[0]} → {ESCALA[-1]}")
    print("\n🎮 CONTROLES:")
    print(f"   - GPIO{BOTON_GRABAR}: Iniciar/Detener grabación")
    print(f"   - GPIO{BOTON_REPRODUCIR}: Reproducir secuencia")
    print(f"   - GPIO{BOTON_PARAR}: Parar reproducción")
    print(f"   - GPIO{BOTON_BORRAR}: Borrar secuencia")
    print(f"   - LED GPIO{LED_GRABANDO}: Encendido durante grabación")
    print(f"   - LED GPIO{LED_REPRODUCIENDO}: Encendido durante reproducción")
    print("\n🎵 Modo: " + ("PIANO" if MODO_PIANO else "THEREMIN"))
    print("\n👉 Mueve la mano para tocar. ¡Graba tus melodías!\n")
    print("="*55)

# ================= MEDIR DISTANCIA =================
def medir_distancia():
    """Mide la distancia con HC-SR04"""
    try:
        GPIO.output(TRIG, False)
        time.sleep(0.05)
        
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        
        inicio_eco = time.time()
        fin_eco = time.time()
        
        timeout = time.time() + 0.02
        
        while GPIO.input(ECHO) == 0:
            inicio_eco = time.time()
            if time.time() > timeout:
                return -1
        
        while GPIO.input(ECHO) == 1:
            fin_eco = time.time()
            if time.time() > timeout:
                return -1
        
        duracion = fin_eco - inicio_eco
        distancia = (duracion * 34300) / 2
        
        if distancia < 0 or distancia > 500:
            return -1
            
        return distancia
        
    except:
        return -1

# ================= CONVERTIR DISTANCIA A NOTA =================
def distancia_a_nota(distancia):
    """Convierte distancia a nota musical"""
    if distancia > DISTANCIA_MAX:
        distancia = DISTANCIA_MAX
    if distancia < DISTANCIA_MIN:
        distancia = DISTANCIA_MIN
    
    rango = DISTANCIA_MAX - DISTANCIA_MIN
    offset = distancia - DISTANCIA_MIN
    
    indice = int((offset / rango) * len(ESCALA))
    
    if indice >= len(ESCALA):
        indice = len(ESCALA) - 1
    if indice < 0:
        indice = 0
    
    return ESCALA[indice], indice

# ================= TOCAR NOTA =================
def tocar_nota(nota, duracion=None):
    """Toca una nota musical"""
    try:
        frecuencia = NOTAS[nota]
        pwm_buzzer.ChangeFrequency(frecuencia)
        pwm_buzzer.ChangeDutyCycle(10) #volumen
        
        if duracion:
            time.sleep(duracion)
            pwm_buzzer.ChangeDutyCycle(0)
    except:
        pass

def silencio():
    """Apaga el sonido"""
    try:
        pwm_buzzer.ChangeDutyCycle(0)
    except:
        pass

# ================= FUNCIONES DE BOTONES (POLLING) =================
def leer_boton(boton, ultimo_tiempo):
    """Lee el estado de un botón con debounce"""
    tiempo_actual = time.time()
    
    # Verificar si el botón está presionado (LOW porque usamos pull-up)
    if GPIO.input(boton) == GPIO.LOW:
        if tiempo_actual - ultimo_tiempo > DEBOUNCE_TIME:
            return True, tiempo_actual
    return False, ultimo_tiempo

def verificar_botones():
    """Verifica el estado de todos los botones"""
    global grabando, reproduciendo, secuencia_grabada, ultimo_tiempo_boton
    
    # Botón GRABAR
    presionado, nuevo_tiempo = leer_boton(BOTON_GRABAR, ultimo_tiempo_boton[BOTON_GRABAR])
    if presionado:
        ultimo_tiempo_boton[BOTON_GRABAR] = nuevo_tiempo
        with lock:
            if not reproduciendo:
                grabando = not grabando
                
                if grabando:
                    secuencia_grabada = []
                    GPIO.output(LED_GRABANDO, GPIO.HIGH)
                    print("\n🔴 ¡GRABACIÓN INICIADA! 🔴")
                    print("   Presiona el mismo botón para detener\n")
                else:
                    GPIO.output(LED_GRABANDO, GPIO.LOW)
                    num_notas = len(secuencia_grabada)
                    print(f"\n✅ GRABACIÓN DETENIDA. {num_notas} notas guardadas.\n")
            else:
                print("\n⏸️ No se puede grabar mientras se reproduce\n")
    
    # Botón REPRODUCIR
    presionado, nuevo_tiempo = leer_boton(BOTON_REPRODUCIR, ultimo_tiempo_boton[BOTON_REPRODUCIR])
    if presionado:
        ultimo_tiempo_boton[BOTON_REPRODUCIR] = nuevo_tiempo
        with lock:
            if not grabando and not reproduciendo:
                if len(secuencia_grabada) > 0:
                    hilo_reproducir = threading.Thread(target=reproducir_secuencia, daemon=True)
                    hilo_reproducir.start()
                else:
                    print("\n⚠️ No hay ninguna secuencia grabada\n")
            elif grabando:
                print("\n⏸️ Detén la grabación primero\n")
            elif reproduciendo:
                print("\n⏸️ Ya se está reproduciendo\n")
    
    # Botón PARAR
    presionado, nuevo_tiempo = leer_boton(BOTON_PARAR, ultimo_tiempo_boton[BOTON_PARAR])
    if presionado:
        ultimo_tiempo_boton[BOTON_PARAR] = nuevo_tiempo
        with lock:
            if reproduciendo:
                reproduciendo = False
                GPIO.output(LED_REPRODUCIENDO, GPIO.LOW)
                silencio()
                print("\n⏹️ Reproducción detenida\n")
            else:
                print("\n⚠️ No hay reproducción activa\n")
    
    # Botón BORRAR
    presionado, nuevo_tiempo = leer_boton(BOTON_BORRAR, ultimo_tiempo_boton[BOTON_BORRAR])
    if presionado:
        ultimo_tiempo_boton[BOTON_BORRAR] = nuevo_tiempo
        with lock:
            if not grabando and not reproduciendo:
                if len(secuencia_grabada) > 0:
                    secuencia_grabada = []
                    print("\n🗑️ Secuencia borrada\n")
                else:
                    print("\n📭 No hay secuencia para borrar\n")
            else:
                print("\n⏸️ Detén grabación/reproducción primero\n")

def reproducir_secuencia():
    """Reproduce la secuencia grabada"""
    global reproduciendo
    
    with lock:
        reproduciendo = True
        GPIO.output(LED_REPRODUCIENDO, GPIO.HIGH)
    
    print("\n▶️ REPRODUCIENDO SECUENCIA... ▶️")
    print(f"   {len(secuencia_grabada)} notas\n")
    
    for i, (nota, duracion) in enumerate(secuencia_grabada, 1):
        if not reproduciendo:  # Permitir parar
            break
        
        print(f"   Nota {i:2d}: {nota}")
        
        try:
            pwm_buzzer.ChangeFrequency(NOTAS[nota])
            pwm_buzzer.ChangeDutyCycle(50)
            time.sleep(duracion)
            pwm_buzzer.ChangeDutyCycle(0)
            time.sleep(0.05)
        except:
            pass
    
    print("\n✅ REPRODUCCIÓN FINALIZADA ✅\n")
    
    with lock:
        reproduciendo = False
        GPIO.output(LED_REPRODUCIENDO, GPIO.LOW)
        silencio()

# ================= MODO PRINCIPAL =================
def modo_piano():
    """Modo piano con control de botones por polling"""
    global grabando, ultima_nota, secuencia_grabada
    
    print("🎹 MODO PIANO ACTIVADO")
    print("   Usa los botones físicos para controlar\n")
    
    while True:
        # Verificar botones constantemente
        verificar_botones()
        
        # Si está reproduciendo, solo verificamos botones
        if reproduciendo:
            time.sleep(0.05)
            continue
        
        # Medir distancia y tocar
        distancia = medir_distancia()
        
        if distancia > 0:
            nota, indice = distancia_a_nota(distancia)
            
            if nota != ultima_nota:
                # Mostrar visualmente
                barra = "█" * int((indice / (len(ESCALA) - 1)) * 20)
                barra += "░" * (20 - len(barra))
                
                estado = "🎤[GRAB]" if grabando else "🎵[LIBRE]"
                print(f"{estado} Dist: {distancia:5.1f}cm | Nota: {nota:>5} | {barra}")
                
                # Tocar nota
                tocar_nota(nota, DURACION_NOTA)
                
                # Grabar si está activo
                if grabando:
                    secuencia_grabada.append((nota, DURACION_NOTA))
                
                ultima_nota = nota
            else:
                time.sleep(0.05)
        else:
            time.sleep(0.1)

# ================= MENÚ PRINCIPAL =================
def menu():
    """Menú interactivo"""
    print("\n" + "="*50)
    print("🎹 PIANO-THEREMIN CON GRABACIÓN 🎵")
    print("="*50)
    print("1. Modo Piano")
    print("2. Ver secuencia grabada")
    print("3. Configurar escala")
    print("4. Salir")
    
    opcion = input("\nSelecciona una opción (1-4): ")
    return opcion

def ver_secuencia():
    """Muestra la secuencia grabada"""
    if len(secuencia_grabada) == 0:
        print("\n📭 No hay ninguna secuencia grabada\n")
    else:
        print(f"\n📜 SECUENCIA GRABADA ({len(secuencia_grabada)} notas):")
        print("-" * 40)
        for i, (nota, duracion) in enumerate(secuencia_grabada, 1):
            print(f"  {i:2d}. {nota:>5} - {duracion:.2f}s")
        print("-" * 40 + "\n")

def configurar_escala():
    """Configura una escala personalizada"""
    global ESCALA
    
    print("\n🎼 ESCALAS DISPONIBLES:")
    print("1. Do Mayor (Do4,Re4,Mi4,Fa4,Sol4,La4,Si4,Do5)")
    print("2. Pentatónica (Do4,Re4,Mi4,Sol4,La4,Do5)")
    print("3. Blues (Do4,Re#4,Fa4,Sol4,Sol#4,Si4,Do5)")
    print("4. Mantener actual")
    
    opcion = input("\nElige una opción (1-4): ")
    
    if opcion == '1':
        ESCALA = ['Do4', 'Re4', 'Mi4', 'Fa4', 'Sol4', 'La4', 'Si4', 'Do5']
        print("✅ Escala Do Mayor seleccionada")
    elif opcion == '2':
        ESCALA = ['Do4', 'Re4', 'Mi4', 'Sol4', 'La4', 'Do5']
        print("✅ Escala Pentatónica seleccionada")
    elif opcion == '3':
        ESCALA = ['Do4', 'Re#4', 'Fa4', 'Sol4', 'Sol#4', 'Si4', 'Do5']
        print("✅ Escala de Blues seleccionada")
    else:
        print("✅ Escala actual mantenida")
    
    print(f"   Notas: {' → '.join(ESCALA)}\n")

# ================= BUCLE PRINCIPAL =================
def loop():
    """Bucle principal"""
    try:
        while True:
            opcion = menu()
            
            if opcion == '1':
                modo_piano()
                
            elif opcion == '2':
                ver_secuencia()
                
            elif opcion == '3':
                configurar_escala()
                
            elif opcion == '4':
                print("\n👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción no válida")
                
    except KeyboardInterrupt:
        print("\n\n👋 Programa terminado")
    finally:
        silencio()
        if pwm_buzzer:
            pwm_buzzer.stop()
        GPIO.cleanup()
        print("✅ Sistema apagado correctamente")

# ================= PUNTO DE ENTRADA =================
if __name__ == "__main__":
    setup()
    loop()