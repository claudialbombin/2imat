import random
import time
from typing import List
import multiprocessing

def generar_lista_aleatoria(tam: int) -> List[float]:
    """Genera una lista de tamaño tam de números aleatorios entre 0 y 100"""
    lista = []
    for _ in range(tam):
        lista.append(random.uniform(0, 100))
    return lista

def sumar_lista(lista: List[float]) -> float:
    """Realiza la suma elemento a elemento sin usar la función sum()"""
    suma = 0.0
    for numero in lista:
        suma += numero
    return suma

def proceso_trabajo(tamano):
    """Función que ejecuta cada proceso"""
    lista = generar_lista_aleatoria(tamano)
    resultado = sumar_lista(lista)
    print(f"Finalizada la suma de {tamano} valores dando como resultado {resultado}")
    return resultado

if __name__ == "__main__":
    tamaños = [20000000, 40000000, 50000000, 60000000]

    # Versión monoprocesador
    print("Version monoprocesador")
    t0 = time.time()
    for tam in tamaños:
        lista = generar_lista_aleatoria(tam)
        resultado = sumar_lista(lista)
        print(f"Finalizada la suma de {tam} valores dando como resultado {resultado}")
    t1 = time.time()
    tiempo_mono = t1 - t0

    # Versión multiprocesador
    print("\nVersion multiprocesador")
    t0 = time.time()
    
    procesos = []
    for tam in tamaños:
        proceso = multiprocessing.Process(target=proceso_trabajo, args=(tam,))
        procesos.append(proceso)
        proceso.start()
    
    for proceso in procesos:
        proceso.join()
    
    t1 = time.time()
    tiempo_multi = t1 - t0

    print(f"\nEl trabajo total ha tardado {tiempo_mono} segundos (versión monoprocesador)")
    print(f"El trabajo total ha tardado {tiempo_multi} segundos (versión multiprocesador)")

    # SpeedUp
    if tiempo_multi > 0:
        speedup = tiempo_mono / tiempo_multi
        print(f"SpeedUp = {speedup}")
    else:
        print("No se pudo calcular el SpeedUp (tiempo multiprocesador = 0)")

# COMENTARIOS Y RESPUESTAS:
"""
¿Cuál era el speedUp que esperaba obtener?
El speedUp teórico esperado sería cercano a 4, ya que tenemos 4 procesos ejecutándose en paralelo
y cada uno realiza una tarea independiente similar.

¿El speedUp obtenido es mayor o menor? ¿A qué crees que se debe?
El speedUp obtenido es generalmente menor al teórico. Esto se debe principalmente a:
1. Overhead de creación y gestión de procesos
2. Contención en el acceso a memoria RAM
3. Operaciones de E/S compartidas
4. Serialización de datos entre procesos
5. Tiempos de sincronización y scheduling del sistema operativo

El speedUp rara vez alcanza el valor teórico máximo debido a estos factores de overhead.
"""