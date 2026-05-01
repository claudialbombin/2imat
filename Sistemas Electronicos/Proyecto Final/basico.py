
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time

# ================= CONFIGURACIÓN DE PINES =================
TRIG = 25      # Pin de disparo del ultrasonidos
ECHO = 24      # Pin de eco del ultrasonidos
BUZZER = 27    # Pin del altavoz (salida PWM)

# ================= NOTAS MUSICALES (Frecuencias en Hz) =================
# Escala de Do mayor (puedes cambiarla a cualquier escala)
NOTAS = {
    # Nota     Frecuencia (Hz)
    'Do3':   130.81,
    'Do#3':  138.59,
    'Re3':   146.83,
    'Re#3':  155.56,
    'Mi3':   164.81,
    'Fa3':   174.61,
    'Fa#3':  185.00,
    'Sol3':  196.00,
    'Sol#3': 207.65,
    'La3':   220.00,
    'La#3':  233.08,
    'Si3':   246.96,
    'Do4':   261.63,   # Do central
    'Do#4':  277.18,
    'Re4':   293.66,
    'Re#4':  311.13,
    'Mi4':   329.63,
    'Fa4':   349.23,
    'Fa#4':  369.99,
    'Sol4':  392.00,
    'Sol#4': 415.30,
    'La4':   440.00,   # La estándar de afinación
    'La#4':  466.16,
    'Si4':   493.88,
    'Do5':   523.25
}

# Lista ordenada de notas para asignar por distancia
# Puedes crear tu propia escala (ej: escala pentatónica, blues, etc.)
ESCALA = [
    'Do3', 'Re3', 'Mi3', 'Fa3', 'Sol3', 'La3', 'Si3',   # Octava baja
    'Do4', 'Re4', 'Mi4', 'Fa4', 'Sol4', 'La4', 'Si4',   # Octava media
    'Do5'                                               # Nota aguda
]

# ================= PARÁMETROS DE CONTROL =================
DISTANCIA_MIN = 5      # Distancia mínima (cm) - nota más grave
DISTANCIA_MAX = 40     # Distancia máxima (cm) - nota más aguda
DURACION_NOTA = 0.3    # Duración de cada nota (segundos) - para efecto piano
MODO_PIANO = True      # True = modo piano (nota suena fijo duración), False = modo theremin (nota sostenida)

# Para modo theremin (nota continua mientras la mano está quieta)
UMBRAL_MOVIMIENTO = 3   # cm de cambio para considerar que hay movimiento
ultima_nota = None
ultima_distancia = None

# ================= SETUP GPIO =================
def setup():
    """Configura los pines GPIO y el PWM para el altavoz"""
    GPIO.setmode(GPIO.BCM)
    
    # Configurar sensor ultrasonidos
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    
    # Configurar altavoz
    GPIO.setup(BUZZER, GPIO.OUT)
    global pwm_buzzer
    pwm_buzzer = GPIO.PWM(BUZZER, 440)  # Frecuencia inicial
    pwm_buzzer.start(0)  # Empezar en silencio
    
    print("🎹 ¡PIANO-THEREMIN INICIADO! 🎵")
    print(f"Rango: {DISTANCIA_MIN}cm - {DISTANCIA_MAX}cm")
    print(f"Escala: {ESCALA[0]} → {ESCALA[-1]}")
    print("Modo: " + ("PIANO (notas con duración fija)" if MODO_PIANO else "THEREMIN (notas sostenidas)"))
    print("\nInstrucciones:")
    print("- Mueve la mano hacia adelante/atrás para cambiar de nota")
    print("- Ctrl+C para salir\n")

# ================= MEDIR DISTANCIA =================
def medir_distancia():
    """Mide la distancia con HC-SR04"""
    GPIO.output(TRIG, False)
    time.sleep(0.05)
    
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    
    inicio_eco = time.time()
    fin_eco = time.time()
    
    # Timeout para evitar bloqueos
    timeout_inicio = time.time() + 0.02
    while GPIO.input(ECHO) == 0:
        inicio_eco = time.time()
        if time.time() > timeout_inicio:
            return -1
    
    timeout_fin = time.time() + 0.02
    while GPIO.input(ECHO) == 1:
        fin_eco = time.time()
        if time.time() > timeout_fin:
            return -1
    
    duracion = fin_eco - inicio_eco
    distancia = (duracion * 34300) / 2
    
    # Limitar rango
    if distancia < 0:
        distancia = 0
    if distancia > 500:
        distancia = 500
        
    return distancia

# ================= CONVERTIR DISTANCIA A NOTA =================
def distancia_a_nota(distancia):
    """
    Convierte la distancia a una nota de la escala
    La distancia más cercana = nota más grave
    La distancia más lejana = nota más aguda
    """
    # Limitar distancia al rango configurado
    if distancia > DISTANCIA_MAX:
        distancia = DISTANCIA_MAX
    if distancia < DISTANCIA_MIN:
        distancia = DISTANCIA_MIN
    
    # Calcular qué índice de nota corresponde
    rango = DISTANCIA_MAX - DISTANCIA_MIN
    offset = distancia - DISTANCIA_MIN
    
    # Mapeo inverso: distancia pequeña = índice pequeño (nota grave)
    # Si quieres que cerca = agudo, cambia a: indice = int((offset / rango) * len(ESCALA))
    indice = int((offset / rango) * len(ESCALA))
    
    # Asegurar que está dentro del rango
    if indice >= len(ESCALA):
        indice = len(ESCALA) - 1
    if indice < 0:
        indice = 0
    
    return ESCALA[indice], indice

# ================= TOCAR NOTA =================
def tocar_nota(nota, duracion=None):
    """
    Toca una nota musical
    nota: nombre de la nota (ej: 'Do4')
    duracion: tiempo en segundos (None para sostenido)
    """
    frecuencia = NOTAS[nota]
    pwm_buzzer.ChangeFrequency(frecuencia)
    pwm_buzzer.ChangeDutyCycle(10)  # Volumen medio
    
    if duracion:
        # Modo piano: suena durante duracion y se apaga
        time.sleep(duracion)
        pwm_buzzer.ChangeDutyCycle(0)
    # Si no hay duracion, la nota sigue sonando (modo theremin)

def silencio():
    """Apaga el sonido"""
    pwm_buzzer.ChangeDutyCycle(0)

# ================= MOSTRAR INFORMACIÓN VISUAL =================
def mostrar_nota(nota, indice, distancia):
    """Muestra la nota de forma visual en la consola"""
    # Barra visual de posición
    total_barras = 20
    pos = int((indice / (len(ESCALA) - 1)) * total_barras)
    barra = "█" * pos + "░" * (total_barras - pos)
    
    print(f"Dist: {distancia:5.1f}cm | Nota: {nota:>5} ({NOTAS[nota]:6.1f}Hz) | {barra}")

# ================= MODO PIANO =================
def modo_piano():
    """Modo piano: cada distancia produce una nota con duración fija"""
    global ultima_nota
    
    while True:
        distancia = medir_distancia()
        
        if distancia > 0:
            nota, indice = distancia_a_nota(distancia)
            
            # Solo tocar si cambió la nota (evita repeticiones)
            if nota != ultima_nota:
                mostrar_nota(nota, indice, distancia)
                tocar_nota(nota, DURACION_NOTA)
                ultima_nota = nota
            else:
                # Pequeña pausa para no saturar el sensor
                time.sleep(0.05)
        else:
            print("⚠️ Error en medición")
            time.sleep(0.1)

# ================= MODO THEREMIN =================
def modo_theremin():
    """Modo theremin: la nota suena continuamente y cambia suavemente"""
    global ultima_nota, ultima_distancia
    
    nota_actual = ESCALA[0]
    tocar_nota(nota_actual, None)  # Empezar sonando
    
    while True:
        distancia = medir_distancia()
        
        if distancia > 0:
            nota, indice = distancia_a_nota(distancia)
            
            # Detectar cambio de nota
            if nota != nota_actual:
                # Pequeño fade visual (no hay fade real con PWM simple)
                mostrar_nota(nota, indice, distancia)
                tocar_nota(nota, None)  # Cambiar a nueva nota
                nota_actual = nota
            
            # Pequeña pausa para suavizar
            time.sleep(0.05)
        else:
            print("⚠️ Error en medición")
            time.sleep(0.1)

# ================= CANCIONES DE EJEMPLO =================
def cancion_ejemplo():
    """Demo: reproduce una melodía simple moviendo la mano automáticamente"""
    print("\n🎵 Reproduciendo 'Cumpleaños Feliz' 🎵")
    
    # Secuencia de notas y duraciones (nota, segundos)
    melodia = [
        ('Sol4', 0.3), ('Sol4', 0.3), ('La4', 0.6), ('Sol4', 0.6), ('Do5', 0.6), ('Si4', 1.0),
        ('Sol4', 0.3), ('Sol4', 0.3), ('La4', 0.6), ('Sol4', 0.6), ('Re5', 0.6), ('Do5', 1.0)
    ]
    
    for nota, duracion in melodia:
        print(f"Tocando: {nota}")
        tocar_nota(nota, duracion)
        time.sleep(0.1)
    
    silencio()
    print("✅ Demo finalizada\n")

# ================= MENÚ PRINCIPAL =================
def menu():
    """Menú interactivo"""
    print("\n" + "="*50)
    print("🎹 PIANO-THEREMIN CON RASPBERRY PI 🎵")
    print("="*50)
    print("1. Modo Piano (notas con duración fija)")
    print("2. Modo Theremin (notas sostenidas)")
    print("3. Demo: Reproducir canción automática")
    print("4. Configurar escala personalizada")
    print("5. Salir")
    
    opcion = input("\nSelecciona una opción (1-5): ")
    return opcion

# ================= BUCLE PRINCIPAL =================
def loop():
    """Bucle principal con selección de modo"""
    try:
        while True:
            opcion = menu()
            
            if opcion == '1':
                print("\n🎹 MODO PIANO activado")
                print("Mueve la mano para cambiar de nota (cada nota suena 0.3s)")
                modo_piano()
                
            elif opcion == '2':
                print("\n🎵 MODO THEREMIN activado")
                print("Mueve la mano suavemente - la nota cambia continuamente")
                modo_theremin()
                
            elif opcion == '3':
                cancion_ejemplo()
                
            elif opcion == '4':
                configurar_escala()
                
            elif opcion == '5':
                print("\n👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción no válida")
                
    except KeyboardInterrupt:
        print("\n\n👋 Programa terminado por usuario")
    finally:
        silencio()
        pwm_buzzer.stop()
        GPIO.cleanup()
        print("✅ Sistema apagado correctamente")

# ================= CONFIGURAR ESCALA PERSONALIZADA =================
def configurar_escala():
    """Permite al usuario crear su propia escala"""
    global ESCALA
    
    print("\n🎼 CREAR ESCALA PERSONALIZADA")
    print("Notas disponibles:", ', '.join(list(NOTAS.keys())[:12]))
    
    escala_usuario = input("Escribe las notas separadas por coma (ej: Do4,Re4,Mi4,Fa4,Sol4,La4,Si4): ")
    
    try:
        nuevas_notas = [n.strip() for n in escala_usuario.split(',')]
        # Verificar que todas las notas existen
        for nota in nuevas_notas:
            if nota not in NOTAS:
                print(f"❌ Nota '{nota}' no válida")
                return
        
        ESCALA = nuevas_notas
        print(f"✅ Escala actualizada: {' → '.join(ESCALA)}")
        
    except:
        print("❌ Error en el formato. Usa: Do4,Re4,Mi4")

# ================= PUNTO DE ENTRADA =================
if __name__ == "__main__":
    setup()
    loop()