from multiprocessing import Process
from threading import Thread
import time

# Función que suma los números de un rango y guarda el resultado en una lista compartida
def suma_parcial(inicio, fin, resultados, idx):
    total = 0
    for i in range(inicio, fin + 1):
        total += i
    resultados[idx] = total

# Función que reparte la suma entre dos hilos y muestra el resultado final
def suma_grande_con_hilo():
    resultados = [0, 0]  # Lista para guardar los resultados parciales de los dos hilos
    mitad = 35000000

    # Creamos dos hilos, cada uno suma la mitad del rango
    t1 = Thread(target=suma_parcial, args=(1, mitad, resultados, 0))
    t2 = Thread(target=suma_parcial, args=(mitad + 1, 70000000, resultados, 1))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    suma_total = resultados[0] + resultados[1]
    print(f"La suma de 1 a 70.000.000 es: {suma_total}")

def main():
    # Creamos el proceso secundario que usará un hilo adicional para repartir la tarea
    p = Process(target=suma_grande_con_hilo)
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

    # Comentario:
    # Al repartir la suma entre dos hilos dentro del proceso, la tarea se realiza más rápido
    # y es más probable que la suma termine y se muestre antes de los 3 segundos.
    # Si la suma se muestra, es porque el uso de hilos ha permitido aprovechar mejor los recursos
    # del sistema (especialmente en sistemas con varios núcleos), acelerando la operación.
    # En elcaso de mi ordenador, no es lo suficientemente rapido como para ejecutar la suma en 3 segundos.fd

if __name__ == "__main__":
    main()