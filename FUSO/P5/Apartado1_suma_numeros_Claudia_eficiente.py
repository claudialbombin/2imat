import random
import time
import multiprocessing

def generar_lista_eficiente(tamano: int) -> list:
    """Genera una lista usando list comprehension"""
    return [random.uniform(0, 100) for _ in range(tamano)]

def sumar_lista_eficiente(lista: list) -> float:
    """Suma usando la función sum() nativa"""
    return sum(lista)

def proceso_trabajo_eficiente(tamano):
    """Función que ejecuta cada proceso en versión eficiente"""
    lista = generar_lista_eficiente(tamano)
    resultado = sumar_lista_eficiente(lista)
    print(f"Finalizada la suma de {tamano} valores dando como resultado {resultado}")
    return resultado

if __name__ == "__main__":
    tamaños = [20000000, 40000000, 50000000, 60000000]

    # Versión monoprocesador eficiente
    print("Version monoprocesador (eficiente)")
    t0 = time.time()
    for tam in tamaños:
        lista = generar_lista_eficiente(tam)
        resultado = sumar_lista_eficiente(lista)
        print(f"Finalizada la suma de {tam} valores dando como resultado {resultado}")
    t1 = time.time()
    tiempo_mono_ef = t1 - t0

    # Versión multiprocesador eficiente
    print("\nVersion multiprocesador (eficiente)")
    t0 = time.time()
    
    procesos = []
    for tam in tamaños:
        proceso = multiprocessing.Process(target=proceso_trabajo_eficiente, args=(tam,))
        procesos.append(proceso)
        proceso.start()
    
    for proceso in procesos:
        proceso.join()
    
    t1 = time.time()
    tiempo_multi_ef = t1 - t0

    print(f"\nEl trabajo total ha tardado {tiempo_mono_ef} segundos (versión monoprocesador eficiente)")
    print(f"El trabajo total ha tardado {tiempo_multi_ef} segundos (versión multiprocesador eficiente)")

    # SpeedUp
    if tiempo_multi_ef > 0:
        speedup_ef = tiempo_mono_ef / tiempo_multi_ef
        print(f"SpeedUp = {speedup_ef}")

# COMENTARIOS Y RESPUESTAS:
"""
¿Es más rápida o menos rápida esta versión? (tanto para la versión mono como multiprocesador)

Esta versión es significativamente más rápida que la anterior debido a:
1. List comprehension: Más eficiente que append en un bucle for
2. Función sum() nativa: Optimizada en C y más rápida que suma manual en Python
3. Menor overhead de interpretación de bytecode

Tanto la versión monoprocesador como multiprocesador se benefician de estas optimizaciones,
pero la mejora es más notable en la versión monoprocesador ya que elimina ineficiencias
en el código Python puro.

El speedUp en la versión multiprocesador eficiente puede ser mayor debido a que el tiempo
de computación pura se reduce, haciendo que el overhead de los procesos sea una proporción
menor del tiempo total.
"""