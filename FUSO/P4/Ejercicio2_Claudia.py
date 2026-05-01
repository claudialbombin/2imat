from threading import Thread
from multiprocessing import Process
import numpy as np
import random
import time

# Parámetros de la matriz y número de cambios por hilo (para modificarlos rapidamente)
n_filas = 50
n_columnas = 50
n_cambios = 20

# Funcion define la tarea de cada hilo
def thread_task(indice, matriz):
    # Cada hilo cambia n_cambios posiciones de la matriz a su índice
    for _ in range(n_cambios):
        # Escoge aleatoriamente una posición
        fila = random.randint(0, n_filas - 1)
        columna = random.randint(0, n_columnas - 1)
        # Cambia el valor de la posición a su índice
        matriz[fila, columna] = indice
        # Espera 1 segundo
        time.sleep(1)

# Funcion define tarea de cada proceso
def process_task(indice, matriz):
    # Cada proceso cambia n_cambios posiciones de la matriz a su índice
    for _ in range(n_cambios):
        fila = random.randint(0, n_filas - 1)
        columna = random.randint(0, n_columnas - 1)
        matriz[fila, columna] = indice
        time.sleep(1)
        
if __name__ == "__main__":
    # Inicializamos matriz con NaN
    matriz = np.full((n_filas, n_columnas), np.nan)

	# Solicitamos número de hilos
    try:
        n_crear = int(input("Introduce el número de hilos o procesos que deseas crear: "))
        if n_crear < 1: # Comprobamos q sea positivo
            print("El número de hilos o de procesos debe ser mayor que 0.")
            exit()
    except ValueError: # COmprobamos que haya numero
        print("No has introducido un número válido.")
        exit()

	# Aqui comentar y descomentar dependendo si queremos hilos o procesos

	# # PRIMERA PARTE: HILOS
	# # Creamos y lanzamos hilos
    # hilos = []
    # for i in range(1, n_crear + 1):
    #     hilo = Thread(target=thread_task, args=(i, matriz))
    #     hilos.append(hilo)
    #     hilo.start()
	# # Unimos todos al final
    # for hilo in hilos:
    #     hilo.join()

	# SEGUNDA PARTE: PROCESOS
    procesos = []
    for i in range(1, n_crear + 1):
        proceso = Process(target=process_task, args=(i, matriz))
        procesos.append(proceso)
        proceso.start()

    for proceso in procesos:
        proceso.join()
        
	# Printeamos matriz modificada
    for fila in matriz:
        print([int(x) if not np.isnan(x) else np.nan for x in fila])

    # Contar ocurrencias finales de cada número de hilo en la matriz
    # Ojo que se pueden sobreescribir y entonces con el numero de cambios que realiza cada hilo
    resultado = {}
    for i in range(1, n_crear + 1):
        resultado[i] = int(np.sum(matriz == i))

    print("Resultado:", resultado)


# -------------------------------
# COMENTARIO:
# Al cambiar de hilos (threads) a procesos (Process), la matriz y las variables
# ya NO se comparten entre procesos. Cada proceso tiene su propia copia de la matriz,
# por lo que los cambios realizados por los procesos hijos NO afectan a la matriz
# del proceso principal. Por eso, la matriz final no refleja los cambios esperados.
# -------------------------------