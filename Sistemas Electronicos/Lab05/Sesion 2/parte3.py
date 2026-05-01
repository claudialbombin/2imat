"""
Práctica 5 - Parte 3: Sistema completo de control de luz.
Lee la luz ambiental con la LDR, calcula los lux mediante interpolación
y controla la intensidad de una bombilla incandescente con PWM a través de un transistor.
La bombilla se apaga completamente a 1000 lux y brilla al máximo a 0 lux.
"""

from gpiozero import MCP3008, PWMOutputDevice
from time import sleep

# --- Configuración ---
# Pines
PIN_BOMBILLA = 14  # GPIO14 para el transistor (PWM habilitado)
CANAL_ADC = 0

# Rango de control de la bombilla
LUX_MAX_ENCENDIDO = 1000  # Por encima de este valor, bombilla apagada (0% PWM)
LUX_MIN_APAGADO = 0       # Por debajo (0 lux), bombilla al máximo (100% PWM)

# Frecuencia del PWM (Razonamiento en la sección de preguntas)
FRECUENCIA_PWM = 100  # Hz

# --- Datos de calibración (¡CAMBIAR CON LOS VALORES MEDIDOS!) ---
# Mismos datos que en el paso anterior
TENSIONES_CAL = [0.08, 0.32, 0.58, 0.91, 1.28, 1.57, 1.89, 2.21, 2.58, 2.87, 3.05]
LUXES_CAL =     [0,   28,   67,   118,  201,  312,  458,  612,  788,  941,  1023]

# --- Inicialización de Periféricos ---
sensor = MCP3008(channel=CANAL_ADC)
# PWMOutputDevice nos permite controlar el ciclo de trabajo fácilmente (0.0 a 1.0)
bombilla = PWMOutputDevice(pin=PIN_BOMBILLA, frequency=FRECUENCIA_PWM, initial_value=0)

# --- Funciones (reutilizamos interpolar_luz del paso anterior) ---
def interpolar_luz(voltios):
    """Convierte tensión a lux mediante interpolación lineal."""
    if voltios <= TENSIONES_CAL[0]:
        return LUXES_CAL[0]
    if voltios >= TENSIONES_CAL[-1]:
        return LUXES_CAL[-1]
    
    indice = 0
    for i in range(len(TENSIONES_CAL) - 1):
        if TENSIONES_CAL[i] <= voltios <= TENSIONES_CAL[i+1]:
            indice = i
            break
    
    v_i = TENSIONES_CAL[indice]
    v_i1 = TENSIONES_CAL[indice + 1]
    l_i = LUXES_CAL[indice]
    l_i1 = LUXES_CAL[indice + 1]
    
    if v_i1 - v_i == 0:
        return l_i
    lux = ((l_i1 - l_i) / (v_i1 - v_i)) * (voltios - v_i) + l_i
    return lux

def calcular_pwm_desde_lux(lux):
    """
    Calcula el ciclo de trabajo (duty cycle) para la bombilla.
    Proporcional inverso: a 0 lux -> 100% PWM, a 1000 lux -> 0% PWM.
    """
    # Limitar el valor de lux al rango de control
    if lux >= LUX_MAX_ENCENDIDO:
        return 0.0  # Apagada
    if lux <= LUX_MIN_APAGADO:
        return 1.0  # Máxima intensidad
    
    # Mapeo lineal inverso
    # Rango de lux: 0 a 1000
    # Rango de PWM: 1.0 a 0.0
    duty_cycle = 1.0 - (lux / LUX_MAX_ENCENDIDO)
    return duty_cycle

# --- Bucle Principal ---
print("Sistema de control de intensidad luminosa.")
print(f"Rango de control: {LUX_MIN_APAGADO} lux (100% PWM) a {LUX_MAX_ENCENDIDO} lux (0% PWM)\n")

try:
    while True:
        # 1. Leer la tensión del sensor
        tension = sensor.voltage
        
        # 2. Convertir a lux
        luz_actual = interpolar_luz(tension)
        
        # 3. Calcular el ciclo de trabajo PWM para la bombilla
        duty_cycle = calcular_pwm_desde_lux(luz_actual)
        
        # 4. Aplicar el PWM al transistor (y por tanto a la bombilla)
        bombilla.value = duty_cycle
        
        # 5. Mostrar información en consola
        print(f"Luz: {luz_actual:6.1f} lux | Tensión: {tension:.3f} V | PWM: {duty_cycle*100:5.1f}%", end='\r')
        
        # Esperar un poco antes de la siguiente medición (10 veces por segundo)
        sleep(0.1)

except KeyboardInterrupt:
    print("\n\nPrograma terminado.")
    bombilla.off()  # Asegurar que la bombilla se apaga al salir
