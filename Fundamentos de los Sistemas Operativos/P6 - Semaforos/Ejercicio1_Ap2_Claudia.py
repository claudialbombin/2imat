# Ejercicio hilos consumidor - productor con múltiples productores y consumidores

# Copiamos y adaptamos el código del ejercicio anterior para manejar múltiples productores y consumidores.
import threading
import time
import random

BUFFER_SIZE = 10
buffer = [-1] * BUFFER_SIZE
in_index = 0
out_index = 0

# Semáforos y mutex
empty = threading.Semaphore(BUFFER_SIZE)
full = threading.Semaphore(0)
mutex = threading.Semaphore(1)

def productor(id: int):
    global buffer, in_index
    for _ in range(BUFFER_SIZE*2):
        val = random.randint(1, 10)
        empty.acquire() # Espera a que haya espacio en el buffer
        mutex.acquire() # Sección crítica
        buffer[in_index] = val
        print(f"Productor {id} produjo: {val} en la posición {in_index}")
        in_index = (in_index + 1) % BUFFER_SIZE
        mutex.release() # Fin de sección crítica
        full.release()  # Indica que hay un nuevo ítem en el buffer
        time.sleep(random.randint(0, 1)) # Simula tiempo


def consumidor(id: int):
    global buffer, out_index
    for _ in range(BUFFER_SIZE*2):
        full.acquire()  # Espera a que haya ítems en el buffer
        mutex.acquire() # Sección crítica
        val = buffer[out_index]
        buffer[out_index] = -1
        print(f"Consumidor {id} ha leido: {val} de la posición {out_index}")
        out_index = (out_index + 1) % BUFFER_SIZE
        mutex.release() # Fin de sección crítica
        empty.release() # Indica que hay espacio libre en el buffer
        time.sleep(random.randint(0, 1)) # Simula tiempo


if __name__ == "__main__":
    productor1 = threading.Thread(target=productor, args=(1,))
    consumidor1 = threading.Thread(target=consumidor, args=(1,))
    productor2 = threading.Thread(target=productor, args=(2,))
    consumidor2 = threading.Thread(target=consumidor, args=(2,))
    productor3 = threading.Thread(target=productor, args=(3,))
    consumidor3 = threading.Thread(target=consumidor, args=(3,))
    consumidor1.start()
    productor1.start()
    consumidor2.start()
    productor2.start()
    consumidor3.start()
    productor3.start()
    productor1.join()
    consumidor1.join()
    productor2.join()
    consumidor2.join()
    productor3.join()
    consumidor3.join()


# He decidido printear tambien la posición del buffer donde se produce o consume el ítem para tener una mejor visualización de lo que está ocurriendo en el buffer circular.
# Ademas, asi compruebo que no se accede a la misma posición del buffer por parte de productor y consumidor al mismo tiempo.


# Respuestas a las preguntas:

# 1. ¿Encuentras algún problema de sincronización?
# No hay condiciones de carrera ni interbloqueos con la configuración de 3 productores y 3 consumidores:
# - mutex protege in_index/out_index y evita accesos concurrentes a la zona crítica.
# - empty/full evitan sobreescrituras y consumos de posiciones vacías.

# 2. ¿Qué pasaría si en lugar de 3 productores y 3 consumidores se ejecutasen 3 productores y 4 consumidores sin cambiar el código?
# Se producirían 3 * BUFFER_SIZE*2 elementos pero los consumidores intentarían consumir 4 * BUFFER_SIZE*2 elementos.
# Los consumidores adicionales quedarían bloqueados en full.acquire() cuando no haya más items disponibles, provocando que esos hilos se queden colgados y el programa no termine (hang/deadlock por consumidores esperando indefinidamente).

