import random
import time
import numpy as np
import threading
from typing import List

def multiplica_matrices(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Classic matrix multiplication algorithm
    """
    m = A.shape[0]
    n = A.shape[1]
    p = B.shape[1]
    
    # Create zero matrix C
    C = np.zeros((m, p))
    
    for i in range(m):
        for j in range(p):
            for k in range(n):
                C[i, j] += A[i, k] * B[k, j]
    
    return C

def genera_matriz_aleatoria(filas: int, columnas: int) -> np.ndarray:
    return np.random.random((filas, columnas))

def tarea_multiplicacion(tamano: int, resultados: list, indice: int):
    """
    Función que ejecuta una tarea de multiplicación de matrices
    """
    A = genera_matriz_aleatoria(tamano, tamano)
    B = genera_matriz_aleatoria(tamano, tamano)
    
    inicio = time.time()
    C = multiplica_matrices(A, B)
    fin = time.time()
    
    tiempo_ejecucion = fin - inicio
    resultados[indice] = (tamano, tiempo_ejecucion)

def ejecucion_secuencial(tamanos: List[int]):
    """
    Ejecución secuencial de todas las tareas
    """
    print("=== EJECUCIÓN SECUENCIAL ===")
    tiempos = []
    
    for tamano in tamanos:
        A = genera_matriz_aleatoria(tamano, tamano)
        B = genera_matriz_aleatoria(tamano, tamano)
        
        inicio = time.time()
        C = multiplica_matrices(A, B)
        fin = time.time()
        
        tiempo_ejecucion = fin - inicio
        tiempos.append(tiempo_ejecucion)
        print(f"Tarea {tamano}x{tamano}: {tiempo_ejecucion:.4f}s")
    
    return tiempos

def ejecutar_grupo_tareas_hilos(tamanos_grupo: List[int], resultados: list, indices: List[int]):
    """
    Ejecuta un grupo de tareas secuencialmente en un hilo
    """
    for i, tamano in enumerate(tamanos_grupo):
        tarea_multiplicacion(tamano, resultados, indices[i])

def ejecucion_con_hilos(tamanos: List[int]):
    """
    Ejecución con 2 hilos
    """
    print("\n=== EJECUCIÓN CON HILOS (2 HILOS) ===")
    
    resultados = [None] * len(tamanos)
    hilos = []
    
    # Hilo 1: tareas 0 y 2 (310x310 y 160x160)
    h1 = threading.Thread(target=ejecutar_grupo_tareas_hilos,
                         args=([tamanos[0], tamanos[2]], resultados, [0, 2]))
    hilos.append(h1)
    
    # Hilo 2: tareas 1 y 3 (400x400 y 210x210)
    h2 = threading.Thread(target=ejecutar_grupo_tareas_hilos,
                         args=([tamanos[1], tamanos[3]], resultados, [1, 3]))
    hilos.append(h2)
    
    inicio_total = time.time()
    
    for hilo in hilos:
        hilo.start()
    
    for hilo in hilos:
        hilo.join()
    
    fin_total = time.time()
    
    # Reorganizar resultados
    tiempos_hilos = [None] * len(tamanos)
    for item in resultados:
        if item:
            tamano, tiempo = item
            idx = tamanos.index(tamano)
            tiempos_hilos[idx] = tiempo
    
    tiempo_total_hilos = fin_total - inicio_total
    
    return tiempos_hilos, tiempo_total_hilos

def test_multiplicacion_pequena():
    """
    Test con matrices pequeñas para verificar el algoritmo
    """
    print("=== TEST CON MATRICES PEQUEÑAS ===")
    A = np.array([[1, 2], [3, 4]])
    B = np.array([[5, 6], [7, 8]])
    
    print("Matriz A:")
    print(A)
    print("Matriz B:")
    print(B)
    
    C = multiplica_matrices(A, B)
    print("Resultado A × B:")
    print(C)
    
    # Verificación con numpy
    C_numpy = np.dot(A, B)
    print("Resultado con numpy (para verificación):")
    print(C_numpy)
    
    print("¿Los resultados coinciden?", np.allclose(C, C_numpy))

def main():
    # Test con matrices pequeñas
    test_multiplicacion_pequena()
    
    print("\n" + "="*50)
    print("ANÁLISIS DE RENDIMIENTO CON HILOS")
    print("="*50)
    
    # Tamaños de matrices
    tamanos = [310, 400, 160, 210]
    
    # Ejecución secuencial
    tiempos_secuencial = ejecucion_secuencial(tamanos)
    tiempo_total_secuencial = sum(tiempos_secuencial)
    
    print(f"\nTiempo total secuencial: {tiempo_total_secuencial:.4f}s")
    
    # Ejecución con hilos
    tiempos_hilos, tiempo_total_hilos = ejecucion_con_hilos(tamanos)
    
    print(f"Tiempo total con hilos: {tiempo_total_hilos:.4f}s")
    
    # Cálculo de speedup
    speedup = tiempo_total_secuencial / tiempo_total_hilos
    print(f"SpeedUp obtenido con hilos: {speedup:.2f}x")
    
    # Mostrar tiempos individuales
    print("\n=== TIEMPOS INDIVIDUALES ===")
    for i, tamano in enumerate(tamanos):
        print(f"Tamaño {tamano}x{tamano}: Secuencial={tiempos_secuencial[i]:.4f}s, Hilos={tiempos_hilos[i]:.4f}s")

if __name__ == "__main__":
    main()

# COMENTARIOS Y RESPUESTAS:
"""
¿La tarea tarda menos o más? ¿A qué crees que se debe?

La tarea generalmente tarda MÁS con hilos que con procesos para operaciones CPU-intensivas
como la multiplicación de matrices. Esto se debe principalmente al GIL (Global Interpreter Lock)
de Python.

El GIL permite que solo un hilo ejecute código Python a la vez, por lo que aunque tengamos
múltiples hilos, solo uno puede estar ejecutándose concurrentemente. Esto convierte la
ejecución con hilos en prácticamente secuencial para tareas CPU-bound.

En contraste, los procesos tienen su propio intérprete Python y espacio de memoria, por lo
que pueden ejecutarse verdaderamente en paralelo en múltiples núcleos de CPU.

El speedUp con hilos será cercano a 1x (poco o ningún improvement), mientras que con procesos
debería ser cercano a 2x con un buen balance de carga.
"""