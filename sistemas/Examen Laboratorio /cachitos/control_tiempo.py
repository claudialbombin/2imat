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