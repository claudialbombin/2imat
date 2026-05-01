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