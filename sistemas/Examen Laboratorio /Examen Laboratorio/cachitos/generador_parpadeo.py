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