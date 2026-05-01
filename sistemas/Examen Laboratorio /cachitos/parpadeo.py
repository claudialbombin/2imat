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