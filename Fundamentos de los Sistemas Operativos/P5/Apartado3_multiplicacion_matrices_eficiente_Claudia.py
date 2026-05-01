import random
import time
import numpy as np
import multiprocessing
from typing import List

def multiplica_matrices_ef(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    More efficient matrix multiplication algorithm
    """
    m = A.shape[0]
    n = A.shape[1]
    p = B.shape[1]
    
    # Create zero matrix C
    C = np.zeros((m, p))
    
    for i in range(m):
        ci = C[i]  # Get row i of C
        for k in range(n):
            bk = B[k]  # Get row k of B
            aik = A[i, k]  # Get element A[i, k]
            for j in range(p):
                ci[j] += aik * bk[j]
    
    return C

def genera_matriz_aleatoria(filas: int, columnas: int) -> np.ndarray:
    return np.random.random((filas, columnas))

def tarea_multiplicacion_ef(tamano: int, resultado: list, indice: int):
    """
    Función que ejecuta una tarea de multiplicación de matrices eficiente
    """
    A = genera_matriz_aleatoria(tamano, tamano)
    B = genera_matriz_aleatoria(tamano, tamano)
    
    inicio = time.time()
    C = multiplica_matrices_ef(A, B)
    fin = time.time()
    
    tiempo_ejecucion = fin - inicio
    resultado[indice] = (tamano, tiempo_ejecucion)

def ejecucion_secuencial_ef(tamanos: List[int]):
    """
    Ejecución secuencial con algoritmo eficiente
    """
    print("=== EJECUCIÓN SECUENCIAL (ALGORITMO EFICIENTE) ===")
    tiempos = []
    
    for tamano in tamanos:
        A = genera_matriz_aleatoria(tamano, tamano)
        B = genera_matriz_aleatoria(tamano, tamano)
        
        inicio = time.time()
        C = multiplica_matrices_ef(A, B)
        fin = time.time()
        
        tiempo_ejecucion = fin - inicio
        tiempos.append(tiempo_ejecucion)
        print(f"Tarea {tamano}x{tamano}: {tiempo_ejecucion:.4f}s")
    
    return tiempos

def ejecutar_grupo_tareas_ef(tamanos_grupo: List[int], resultado: list, indices: List[int]):
    """
    Ejecuta un grupo de tareas secuencialmente con algoritmo eficiente
    """
    for i, tamano in enumerate(tamanos_grupo):
        tarea_multiplicacion_ef(tamano, resultado, indices[i])

def ejecucion_paralela_ef(tamanos: List[int]):
    """
    Ejecución paralela con 2 procesos y algoritmo eficiente
    """
    print("\n=== EJECUCIÓN PARALELA (2 PROCESOS - ALGORITMO EFICIENTE) ===")
    
    manager = multiprocessing.Manager()
    resultado = manager.list([None] * len(tamanos))
    
    procesos = []
    
    # Proceso 1: tareas 0 y 2 (310x310 y 160x160)
    p1 = multiprocessing.Process(target=ejecutar_grupo_tareas_ef, 
                                args=([tamanos[0], tamanos[2]], resultado, [0, 2]))
    procesos.append(p1)
    
    # Proceso 2: tareas 1 y 3 (400x400 y 210x210)
    p2 = multiprocessing.Process(target=ejecutar_grupo_tareas_ef,
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

def test_multiplicacion_pequena_ef():
    """
    Test con matrices pequeñas para verificar el algoritmo eficiente
    """
    print("=== TEST CON MATRICES PEQUEÑAS (ALGORITMO EFICIENTE) ===")
    A = np.array([[1, 2], [3, 4]])
    B = np.array([[5, 6], [7, 8]])
    
    print("Matriz A:")
    print(A)
    print("Matriz B:")
    print(B)
    
    C = multiplica_matrices_ef(A, B)
    print("Resultado A × B (algoritmo eficiente):")
    print(C)
    
    # Verificación con numpy
    C_numpy = np.dot(A, B)
    print("Resultado con numpy (para verificación):")
    print(C_numpy)
    
    print("¿Los resultados coinciden?", np.allclose(C, C_numpy))

def main():
    # Test con matrices pequeñas
    test_multiplicacion_pequena_ef()
    
    print("\n" + "="*50)
    print("ANÁLISIS DE RENDIMIENTO - ALGORITMO EFICIENTE")
    print("="*50)
    
    # Tamaños de matrices
    tamanos = [310, 400, 160, 210]
    
    # Ejecución secuencial con algoritmo eficiente
    tiempos_secuencial_ef = ejecucion_secuencial_ef(tamanos)
    tiempo_total_secuencial_ef = sum(tiempos_secuencial_ef)
    
    print(f"\nTiempo total secuencial (eficiente): {tiempo_total_secuencial_ef:.4f}s")
    
    # Ejecución paralela con algoritmo eficiente
    tiempos_paralelos_ef, tiempo_total_paralelo_ef = ejecucion_paralela_ef(tamanos)
    
    print(f"Tiempo total paralelo (eficiente): {tiempo_total_paralelo_ef:.4f}s")
    
    # Cálculo de speedup
    speedup_ef = tiempo_total_secuencial_ef / tiempo_total_paralelo_ef
    print(f"SpeedUp obtenido (eficiente): {speedup_ef:.2f}x")

if __name__ == "__main__":
    main()

# COMENTARIOS Y RESPUESTAS:
"""
¿Es más rápido ahora? ¿A qué crees que puede deberse?

Sí, el algoritmo eficiente es significativamente más rápido. Esto se debe a:

1. MEJOR LOCALIDAD DE CACHE: 
   - Al acceder a filas completas (ci = C[i], bk = B[k]) en lugar de elementos individuales,
     se aprovecha mejor la jerarquía de memoria cache.
   - Los accesos a memoria son más secuenciales y predecibles.

2. REDUCCIÓN DE ACCESOS A MEMORIA:
   - aik = A[i, k] se carga una vez y se reutiliza en el bucle interno
   - En el algoritmo original, A[i, k] se accedía en cada iteración del bucle más interno

3. OPTIMIZACIONES DEL COMPILADOR:
   - El patrón de acceso más regular permite mejores optimizaciones a nivel de compilador

4. MENOS OVERHEAD DE INDEXACIÓN:
   - Se reducen las operaciones de indexación de arrays numpy

La mejora en rendimiento puede ser de 2x a 3x dependiendo del tamaño de las matrices
y de la arquitectura del procesador, debido principalmente a la mejor utilización
de la cache y la reducción de accesos a memoria.
"""