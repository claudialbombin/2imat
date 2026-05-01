from threading import Thread, Semaphore
import time

# Variables globales
NUM_HILOS = 4
NUM_RONDAS = 10

# Semáforos para la barrera
mutex = Semaphore(1)
barrera = Semaphore(0)
contador = 0

def hilo(id_hilo: int) -> None:
    global contador
    
    for ronda in range(NUM_RONDAS):
        # Realizar la tarea (sección crítica)
        mutex.acquire()
        try:
            print(f"El hilo {id_hilo} realiza el lote en la ronda {ronda + 1}")
        finally:
            mutex.release()
        time.sleep(0.5)  # Simular trabajo
        
        # Barrera de sincronización
        mutex.acquire()
        contador += 1
        
        if contador == NUM_HILOS:
            # Último hilo en llegar
            print(f"--- Todas las tareas de la ronda {ronda + 1} completadas ---")
            contador = 0
            # Liberar a todos los hilos restantes
            for _ in range(NUM_HILOS - 1):
                barrera.release()
            mutex.release()
        else:
            mutex.release()
            # Esperar a que todos terminen
            barrera.acquire()

if __name__ == "__main__":
    # Bloque principal: crea e inicia los hilos
    hilos = []
    for i in range(NUM_HILOS):
        t = Thread(target=hilo, args=(i,))
        hilos.append(t)
    
    for t in hilos:
        t.start()
    
    for t in hilos:
        t.join()
    
    print("Todas las rondas completadas")