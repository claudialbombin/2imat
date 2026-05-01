#contador_saturacion.py
contador = 0
MAXIMO = 3

# Incrementar con saturación
contador = min(contador + 1, MAXIMO)

# Decrementar con saturación (mínimo 0)
contador = max(contador - 1, 0)

# Incremento circular (0-1-2-3-0-1-2-3...)
contador = (contador + 1) % (MAXIMO + 1)


#contorl_tiempo.py
tiempo_inicio = time.time()
TIEMPO_LIMITE = 10  # segundos

# Dentro del bucle:
tiempo_actual = time.time()
tiempo_transcurrido = tiempo_actual - tiempo_inicio

if tiempo_transcurrido > TIEMPO_LIMITE:
    print("Tiempo agotado")
    # Acción correspondiente
    tiempo_inicio = time.time()  # Reiniciar

# Mostrar tiempo restante
tiempo_restante = TIEMPO_LIMITE - tiempo_transcurrido
print(f"Quedan: {tiempo_restante:.1f}s")

# divisor tension

# Calcular Vout del divisor
def vout_divisor(r1, r2, vin=3.3):
    """R1 arriba, R2 abajo"""
    return vin * r2 / (r1 + r2)

# Calcular resistencia desconocida (sensor abajo)
def r_desde_vout(vout, r_fija, vin=3.3):
    """Sensor en posición inferior"""
    if vout >= vin:
        return float('inf')
    return (vout * r_fija) / (vin - vout)

# Calcular resistencia desconocida (sensor arriba)
def r_desde_vout_arriba(vout, r_fija, vin=3.3):
    """Sensor en posición superior"""
    if vout <= 0:
        return float('inf')
    return (vin * r_fija / vout) - r_fija
    
    
flanco varios botones
botones = [Button(7), Button(16), Button(17), Button(19)]
estados_anteriores = [b.is_pressed for b in botones]

# Dentro del bucle:
estados_actuales = [b.is_pressed for b in botones]

for i in range(len(botones)):
    if estados_anteriores[i] and not estados_actuales[i]:
        print(f"Botón {i} pulsado")
        # Acción específica para cada botón

estados_anteriores = estados_actuales.copy()


#Flancos
# Detección de flanco de bajada (pulsación)
boton_anterior = boton.is_pressed
# Dentro del bucle:
boton_actual = boton.is_pressed
if boton_anterior and not boton_actual:
    # Acción al pulsar (UNA VEZ)
    pass
boton_anterior = boton_actual

# Detección de flanco de subida (soltar)
if not boton_anterior and boton_actual:
    # Acción al soltar
    pass

# Detectar AMBOS flancos
if boton_anterior != boton_actual:
    if not boton_actual:  # Bajada (pulsado)
        # Se pulsó
    else:  # Subida (soltado)
        # Se soltó
        
#generador parpadeo
class Parpadeo:
    def __init__(self, frecuencia_hz):
        self.medio_periodo = 0.5 / frecuencia_hz
        self.ultimo_cambio = 0
        self.estado = False
    
    def actualizar(self, tiempo_actual):
        if tiempo_actual - self.ultimo_cambio >= self.medio_periodo:
            self.estado = not self.estado
            self.ultimo_cambio = tiempo_actual
            return True
        return False

# Uso:
parpadeo = Parpadeo(2)  # 2Hz
while True:
    if parpadeo.actualizar(time.time()):
        led.value = 1 if parpadeo.estado else 0
        
        
#interpolacion
def interpolar(valor, puntos_x, puntos_y):
    """Interpola linealmente"""
    if valor <= puntos_x[0]:
        return puntos_y[0]
    if valor >= puntos_x[-1]:
        return puntos_y[-1]
    
    for i in range(len(puntos_x)-1):
        if puntos_x[i] <= valor <= puntos_x[i+1]:
            x1, x2 = puntos_x[i], puntos_x[i+1]
            y1, y2 = puntos_y[i], puntos_y[i+1]
            return y1 + (y2-y1)/(x2-x1)*(valor-x1)
    
    return puntos_y[-1]

# Uso:
voltajes = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
luces = [0, 200, 400, 600, 800, 1000]
lux = interpolar(1.8, voltajes, luces)

#maquinas estados
# Definir estados como constantes
APAGADO = 0
PARPADEO_1HZ = 1
PARPADEO_2HZ = 2

estado = APAGADO

# Transición - divides entre n estados
estado = (estado + 1) % 3  # 0->1->2->0->...

# O con if-else
if estado == APAGADO:
    estado = PARPADEO_1HZ
elif estado == PARPADEO_1HZ:
    estado = PARPADEO_2HZ
else:
    estado = APAGADO
    
#numeros aleatorios
import random

# Entre 1 y 15 (ambos incluidos)
numero = random.randint(1, 15)

# Entre 10 y 15
numero = random.randint(10, 15)

# Entre 0 y 3
digito = random.randint(0, 3)


#numero bit
# Número a lista de bits (LSB primero)
bits = [(numero >> bit) & 1 for bit in range(8)]  # 8 bits

# Mostrar en LEDs (lista leds tiene 8 elementos)
for i, led in enumerate(leds):
    if bits[i]:
        led.on()
    else:
        led.off()

# Para 4 bits específicos
bits = [(numero >> bit) & 1 for bit in range(4)]
for i, led in enumerate(leds_referencia):  # GPIO20-23
    if bits[i]:
        led.on()
    else:
        led.off()

# Invertir orden (si GPIO20 es MSB)
bits = [(numero >> bit) & 1 for bit in range(4)]
bits.reverse()  # Ahora bits[0] es MSB

# Toggle de un bit específico
numero ^= (1 << 2)  # Toggle del bit 2


#parpadeo 
# Para 1Hz: medio_periodo = 0.5
# Para 2Hz: medio_periodo = 0.25
# Para 5Hz: medio_periodo = 0.1

medio_periodo = 0.5  # Ajustar según frecuencia
tiempo_ultimo_cambio = time.time()
estado_led = False

# Dentro del bucle:
tiempo_actual = time.time()
if tiempo_actual - tiempo_ultimo_cambio >= medio_periodo:
    estado_led = not estado_led
    tiempo_ultimo_cambio = tiempo_actual
    if estado_led:
        led.on()
    else:
        led.off()


        # Versión con frecuencia variable
frecuencia = 1  # Hz
medio_periodo = 0.5 / frecuencia  # medio período en segundos


# potenciometro
UMBRAL_ON = 1.0   # Por debajo = activado
UMBRAL_OFF = 2.0  # Por encima = desactivado
estado_pulsador = False

# Dentro del bucle:
voltios = pot.voltage

if not estado_pulsador and voltios < UMBRAL_ON:
    estado_pulsador = True
    print("Pulsador activado")
elif estado_pulsador and voltios > UMBRAL_OFF:
    estado_pulsador = False
    print("Pulsador desactivado")
    
    
# pwm
from gpiozero import PWMLED

led_pwm = PWMLED(20, frequency=100)  # 100 Hz (sin parpadeo)

# Valores 0.0 a 1.0
led_pwm.value = 0.5  # 50% intensidad
led_pwm.value = 0.75  # 75%
led_pwm.value = 0.0  # apagado
led_pwm.value = 1.0  # máximo


#scan
PERIODO_SCAN = 0.05  # 50 ms (típico en exámenes)

while True:
    inicio_ciclo = time.time()
    
    # TODO: tu código aquí
    
    tiempo_ejecucion = time.time() - inicio_ciclo
    if tiempo_ejecucion < PERIODO_SCAN:
        time.sleep(PERIODO_SCAN - tiempo_ejecucion)
        
#sensor analogico
from gpiozero import MCP3008

sensor = MCP3008(channel=7)  # CH7 = potenciómetro
# CH0-CH6 para sensores externos

# Formas de leer:
valor_normalizado = sensor.value      # 0.0 a 1.0
voltios = sensor.voltage               # 0 a 3.3V
porcentaje = sensor.value * 100        # 0 a 100%

# Umbral simple
if voltios < 1.0:
    # condición
elif voltios > 2.0:
    # otra condición

    # Convertir voltios a lux (sensor lineal)
lux = (voltios / 3.0) * 1500  # 0V=0lx, 3V=1500lx


#timer apagado
import threading

def apagar():
    led.off()
    print("LED apagado por timer")

# Crear y lanzar timer
timer = threading.Timer(3.0, apagar)  # 3 segundos
timer.daemon = True
timer.start()

# Cancelar timer si es necesario
if timer.is_alive():
    timer.cancel()
    
    
# try except
def main():
    # Inicializar hardware
    led = LED(20)
    boton = Button(16)
    
    try:
        while True:
            # Código principal
            pass
            
    except KeyboardInterrupt:
        print("\nPrograma terminado por usuario")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Limpieza siempre se ejecuta
        led.off()
        print("GPIO limpio")

if __name__ == "__main__":
    main()