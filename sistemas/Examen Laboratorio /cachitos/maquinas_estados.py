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