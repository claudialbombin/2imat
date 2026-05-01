import time
from multiprocessing import Process, Manager

# Función que aproxima pi usando la serie propuesta en el enunciado
def aproximar_pi(n):
    suma = 0.0
    # Sumamos los términos de la serie desde 1 hasta n
    for i in range(1, n + 1):
        suma += 1 / (i * i)
    # Calculamos la raíz cuadrada de 6 * suma para aproximar pi
    return (6 * suma) ** 0.5

# Función para procesos: calcula pi y mide el tiempo, guarda el resultado y el tiempo en una lista compartida
def proceso_pi(n, resultados, idx):
    inicio = time.time()  # Guardamos el tiempo de inicio
    resultado = aproximar_pi(n)  # Calculamos la aproximación de pi
    fin = time.time()  # Guardamos el tiempo de fin
    tiempo = fin - inicio
    # Mostramos el resultado y el tiempo empleado
    print(f"Con un valor de {n}, el resultado es {resultado}, con un tiempo de {tiempo:.4f} segundos")
    resultados[idx] = tiempo  # Guardamos el tiempo en la posición correspondiente

def calcular_speedup(tiempo_secuencial, tiempo_paralelo):
    if tiempo_paralelo > 0:
        return tiempo_secuencial / tiempo_paralelo
    else:
        return float('inf')

if __name__ == "__main__":
    # Lista de valores de n para los que se calculará la aproximación de pi
    valores = [1_000_000, 2_000_000, 4_000_000, 8_000_000]

    # Pedimos al usuario el modo de ejecución
    print("Elige modo de ejecución:")
    print("1. Secuencial (un solo procesador)")
    print("2. Paralelo (multiproceso)")
    modo = input("Introduce 1 o 2: ")

    tiempo_total_secuencial = None
    tiempo_total_paralelo = None

    if modo == "1":
        # Modo secuencial: ejecuta la función para cada valor de n uno tras otro
        tiempos = []
        for n in valores:
            inicio = time.time()  # Tiempo de inicio para este valor
            resultado = aproximar_pi(n)  # Aproximación de pi
            fin = time.time()  # Tiempo de fin para este valor
            tiempos.append(fin - inicio)  # Guardamos el tiempo empleado
            print(f"Con un valor de {n}, el resultado es {resultado}, con un tiempo de {fin - inicio:.4f} segundos")
        tiempo_total_secuencial = sum(tiempos)
        # Mostramos el tiempo total empleado en modo secuencial
        print(f"Tiempo total secuencial: {tiempo_total_secuencial:.4f} segundos")
    elif modo == "2":
        # Modo paralelo: crea un proceso para cada valor de n
        manager = Manager()
        resultados = manager.list([0]*len(valores))  # Lista compartida para guardar los tiempos de cada proceso
        procesos = []
        tiempos_inicio = time.time()  # Tiempo de inicio global
        for idx, n in enumerate(valores):
            # Creamos un proceso para calcular pi con el valor n
            p = Process(target=proceso_pi, args=(n, resultados, idx))
            procesos.append(p)
            p.start()  # Iniciamos el proceso
        for p in procesos:
            p.join()  # Esperamos a que todos los procesos terminen
        tiempos_fin = time.time()  # Tiempo de fin global
        tiempo_total_paralelo = tiempos_fin - tiempos_inicio
        # Mostramos el tiempo total empleado en modo paralelo
        print(f"Tiempo total paralelo: {tiempo_total_paralelo:.4f} segundos")
    else:
        # Si la opción no es válida, se informa al usuario y se termina el programa
        print("Opción no válida. El programa finaliza.")
        exit()

    # Si se han ejecutado ambos modos, calcula el speedup
    if tiempo_total_secuencial is not None and tiempo_total_paralelo is not None:
        speedup = calcular_speedup(tiempo_total_secuencial, tiempo_total_paralelo)
        print(f"SpeedUp obtenido: {speedup:.2f}")
    else:
        # Si solo se ejecuta un modo, pregunta si se quiere ejecutar el otro para comparar
        print("\n¿Quieres comparar el SpeedUp ejecutando el otro modo? (s/n)")
        respuesta = input().lower()
        if respuesta == "s":
            if modo == "1":
                # Ejecutar modo paralelo
                manager = Manager()
                resultados = manager.list([0]*len(valores))
                procesos = []
                tiempos_inicio = time.time()
                for idx, n in enumerate(valores):
                    p = Process(target=proceso_pi, args=(n, resultados, idx))
                    procesos.append(p)
                    p.start()
                for p in procesos:
                    p.join()
                tiempos_fin = time.time()
                tiempo_total_paralelo = tiempos_fin - tiempos_inicio
                print(f"Tiempo total paralelo: {tiempo_total_paralelo:.4f} segundos")
                speedup = calcular_speedup(tiempo_total_secuencial, tiempo_total_paralelo)
                print(f"SpeedUp obtenido: {speedup:.2f}")
            elif modo == "2":
                # Ejecutar modo secuencial
                tiempos = []
                for n in valores:
                    inicio = time.time()
                    resultado = aproximar_pi(n)
                    fin = time.time()
                    tiempos.append(fin - inicio)
                    print(f"Con un valor de {n}, el resultado es {resultado}, con un tiempo de {fin - inicio:.4f} segundos")
                tiempo_total_secuencial = sum(tiempos)
                print(f"Tiempo total secuencial: {tiempo_total_secuencial:.4f} segundos")
                speedup = calcular_speedup(tiempo_total_secuencial, tiempo_total_paralelo)
                print(f"SpeedUp obtenido: {speedup:.2f}")