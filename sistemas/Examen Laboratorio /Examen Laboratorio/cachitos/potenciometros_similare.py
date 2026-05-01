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