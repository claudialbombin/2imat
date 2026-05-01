from multiprocessing import Process, Queue
import time

# Función que suma los números de un rango y pone el resultado en una cola
def suma_parcial(inicio, fin, queue):
    total = 0
    for i in range(inicio, fin + 1):
        total += i
    queue.put(total)

# Función que reparte la suma entre dos procesos y muestra el resultado final
def suma_grande_con_proceso():
    queue1 = Queue()
    queue2 = Queue()
    mitad = 35000000

    # Creamos dos procesos, cada uno suma la mitad del rango
    p1 = Process(target=suma_parcial, args=(1, mitad, queue1))
    p2 = Process(target=suma_parcial, args=(mitad + 1, 70000000, queue2))

    p1.start()
    p2.start()
    p1.join()
    p2.join()

    # Recogemos los resultados de las colas
    suma_total = queue1.get() + queue2.get()
    print(f"La suma de 1 a 70.000.000 es: {suma_total}")

def main():
    # Creamos el proceso secundario que usará otro proceso para repartir la tarea
    p = Process(target=suma_grande_con_proceso)
    p.start()
    # Esperamos 3 segundos a que termine
    p.join(timeout=3)
    # Si sigue vivo después de 3 segundos, lo terminamos
    if p.is_alive():
        print("El proceso no ha terminado en 3 segundos. Terminando proceso...")
        p.terminate()
        p.join()
    else:
        print("El proceso terminó correctamente.")

    # Al repartir la suma entre dos procesos, la tarea puede realizarse más rápido
    # y es más probable que la suma termine y se muestre antes de los 3 segundos,
    # ya que cada proceso puede ejecutarse en un núcleo distinto y no comparten el GIL.
    # Sin embargo, en la mayoría de ordenadores, sumar hasta 70.000.000 sigue siendo
    # demasiado lento para completarse en menos de 3 segundos, por lo que normalmente
    # la suma no se muestra.

if __name__ == "__main__":
    main()