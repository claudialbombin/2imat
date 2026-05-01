botones = [Button(7), Button(16), Button(17), Button(19)]
estados_anteriores = [b.is_pressed for b in botones]

# Dentro del bucle:
estados_actuales = [b.is_pressed for b in botones]

for i in range(len(botones)):
    if estados_anteriores[i] and not estados_actuales[i]:
        print(f"Botón {i} pulsado")
        # Acción específica para cada botón

estados_anteriores = estados_actuales.copy()