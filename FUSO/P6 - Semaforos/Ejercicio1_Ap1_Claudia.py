# Ejercicio hilos consumidor - productor
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
    productor_thread = threading.Thread(target=productor, args=(1,))
    consumidor_thread = threading.Thread(target=consumidor, args=(1,))
    productor_thread.start()
    consumidor_thread.start()
    productor_thread.join()
    consumidor_thread.join()


# He decidido printear tambien la posición del buffer donde se produce o consume el ítem para tener una mejor visualización de lo que está ocurriendo en el buffer circular.
# Ademas, asi compruebo que no se accede a la misma posición del buffer por parte de productor y consumidor al mismo tiempo.

