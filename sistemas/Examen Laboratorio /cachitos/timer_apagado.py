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