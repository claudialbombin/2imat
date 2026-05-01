import random
import time
from threading import Thread
from multiprocessing import Process

# Función que realiza n sumas de números aleatorios entre 0 y 1 y luego duerme 20 segundos
def suma_aleatoria(n):
    total = 0.0
    for _ in range(n):
        total += random.random()
    print(f"Suma terminada para n={n}. Durmiendo 20 segundos...")
    time.sleep(20)
    print(f"Proceso/Hilo con n={n} finalizado.")

if __name__ == "__main__":
    # Cambia esta variable a "procesos" o "hilos" para probar
    modo = "hilos"  # Cambia a "procesos" para probar con multiprocessing

    valores = [10_000_000, 100_000_000]

    if modo == "hilos":
        # Crear y lanzar dos hilos
        hilos = []
        for n in valores:
            t = Thread(target=suma_aleatoria, args=(n,))
            hilos.append(t)
            t.start()
        for t in hilos:
            t.join()
    elif modo == "procesos":
        # Crear y lanzar dos procesos
        procesos = []
        for n in valores:
            p = Process(target=suma_aleatoria, args=(n,))
            procesos.append(p)
            p.start()
        for p in procesos:
            p.join()
    else:
        print("Modo no válido. Usa 'hilos' o 'procesos'.")

# -------------------------------
# Observaciones de la terminal (captura adjunta):
# - Si ejecuto la versión con hilos y uso `ps u | grep python3`, veo un solo proceso Python,
#   ya que los hilos comparten el mismo espacio de proceso.
# - Si ejecuto la versión con procesos, veo varios procesos Python (uno por cada Process lanzado),
#   cada uno con su propio identificador de proceso (PID).
# -------------------------------