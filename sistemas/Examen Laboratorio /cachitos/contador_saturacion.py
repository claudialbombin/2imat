contador = 0
MAXIMO = 3

# Incrementar con saturación
contador = min(contador + 1, MAXIMO)

# Decrementar con saturación (mínimo 0)
contador = max(contador - 1, 0)

# Incremento circular (0-1-2-3-0-1-2-3...)
contador = (contador + 1) % (MAXIMO + 1)