import random
import time
import numpy as np
import multiprocessing
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

def tarea_multiplicacion(tamano: int, resultado: list, indice: int):
    """
    Función que ejecuta una tarea de multiplicación de matrices
    """
    A = genera_matriz_aleatoria(tamano, tamano)
    B = genera_matriz_aleatoria(tamano, tamano)
    
    inicio = time.time()
    C = multiplica_matrices(A, B)
    fin = time.time()
    
    tiempo_ejecucion = fin - inicio
    resultado[indice] = (tamano, tiempo_ejecucion)

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

def ejecutar_grupo_tareas(tamanos_grupo: List[int], resultado: list, indices: List[int]):
    """
    Ejecuta un grupo de tareas secuencialmente
    """
    for i, tamano in enumerate(tamanos_grupo):
        tarea_multiplicacion(tamano, resultado, indices[i])

def ejecucion_paralela(tamanos: List[int]):
    """
    Ejecución paralela con 2 procesos
    """
    print("\n=== EJECUCIÓN PARALELA (2 PROCESOS) ===")
    
    manager = multiprocessing.Manager()
    resultado = manager.list([None] * len(tamanos))
    
    procesos = []
    
    # Proceso 1: tareas 0 y 2 (310x310 y 160x160)
    p1 = multiprocessing.Process(target=ejecutar_grupo_tareas, 
                                args=([tamanos[0], tamanos[2]], resultado, [0, 2]))
    procesos.append(p1)
    
    # Proceso 2: tareas 1 y 3 (400x400 y 210x210)
    p2 = multiprocessing.Process(target=ejecutar_grupo_tareas,
                                args=([tamanos[1], tamanos[3]], resultado, [1, 3]))
    procesos.append(p2)
    
    inicio_total = time.time()
    
    for proceso in procesos:
        proceso.start()
    
    for proceso in procesos:
        proceso.join()
    
    fin_total = time.time()
    
    # Reorganizar resultados
    tiempos_paralelos = [None] * len(tamanos)
    for item in resultado:
        if item:
            tamano, tiempo = item
            idx = tamanos.index(tamano)
            tiempos_paralelos[idx] = tiempo
    
    tiempo_total_paralelo = fin_total - inicio_total
    
    return tiempos_paralelos, tiempo_total_paralelo

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
    print("ANÁLISIS DE RENDIMIENTO")
    print("="*50)
    
    # Tamaños de matrices
    tamanos = [310, 400, 160, 210]
    
    # Ejecución secuencial
    tiempos_secuencial = ejecucion_secuencial(tamanos)
    tiempo_total_secuencial = sum(tiempos_secuencial)
    
    print(f"\nTiempo total secuencial: {tiempo_total_secuencial:.4f}s")
    
    # Ejecución paralela
    tiempos_paralelos, tiempo_total_paralelo = ejecucion_paralela(tamanos)
    
    print(f"Tiempo total paralelo: {tiempo_total_paralelo:.4f}s")
    
    # Cálculo de speedup
    speedup = tiempo_total_secuencial / tiempo_total_paralelo
    print(f"SpeedUp obtenido: {speedup:.2f}x")
    
    # Mostrar tiempos individuales
    print("\n=== TIEMPOS INDIVIDUALES ===")
    for i, tamano in enumerate(tamanos):
        print(f"Tamaño {tamano}x{tamano}: Secuencial={tiempos_secuencial[i]:.4f}s, Paralelo={tiempos_paralelos[i]:.4f}s")

if __name__ == "__main__":
    main()

# COMENTARIOS Y RESPUESTAS:
"""
¿Cómo has repartido las tareas entre los procesadores?

He repartido las tareas de la siguiente manera:
- Proceso 1: 310×310 y 160×160
- Proceso 2: 400×400 y 210×210

Este reparto busca balancear la carga computacional porque:
1. 400×400 es la tarea más pesada (O(n³) = 64,000,000 operaciones)
2. 310×310 es la segunda más pesada (O(n³) = 29,791,000 operaciones)
3. 210×210 es la tercera (O(n³) = 9,261,000 operaciones)
4. 160×160 es la más ligera (O(n³) = 4,096,000 operaciones)

Al separar las dos tareas más pesadas en procesos diferentes, evitamos que un solo
proceso tenga que realizar la mayor parte del trabajo, logrando un mejor balance
de carga y maximizando el speedUp potencial.
"""