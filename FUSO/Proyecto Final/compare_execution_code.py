#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# ARCHIVO: compare_execution_code.py
# DESCRIPCIÓN: Implementación de la comparación entre procesamiento
#              secuencial y paralelo para multiplicación de matrices
# USO: Este código debe integrarse en src/model.py del proyecto Flask
# AUTOR: Claudia Maria Lopez Bombin Y Gonzalo Velasco Lucas
# FECHA: Noviembre 2025
# =============================================================================

import numpy as np
import time
from multiprocessing import Pool
from typing import Tuple

def matrix_multiply(size: int) -> float:
    """
    Realiza la multiplicación de matrices cuadradas del tamaño especificado
    y devuelve el tiempo que tardó la operación.
    
    Args:
        size (int): Tamaño de las matrices cuadradas (size x size)
        
    Returns:
        float: Tiempo en segundos que tomó la multiplicación
    """
    # Generar dos matrices aleatorias del tamaño especificado
    # Usamos números aleatorios para asegurar que la multiplicación sea significativa
    A = np.random.rand(size, size)
    B = np.random.rand(size, size)
    
    # Tomar el tiempo antes de la multiplicación
    start_time = time.time()
    
    # Realizar la multiplicación de matrices
    # np.dot es la función optimizada de NumPy para multiplicación de matrices
    result = np.dot(A, B)
    
    # Tomar el tiempo después de la multiplicación
    end_time = time.time()
    
    # Calcular y devolver el tiempo transcurrido
    execution_time = end_time - start_time
    return execution_time

def compare_execution() -> Tuple[float, float]:
    """
    Compara el tiempo de ejecución entre procesamiento secuencial y paralelo
    para la multiplicación de matrices de diferentes tamaños.
    
    Returns:
        Tuple[float, float]: Tupla con:
            - sequential_time: Tiempo total en segundos para ejecución secuencial
            - parallel_time: Tiempo total en segundos para ejecución paralela
    """
    # Tiempos inicializados a 0
    sequential_time = 0
    parallel_time = 0
    
    # Tamaños de matrices a multiplicar
    # Estos tamaños representan matrices medianas/grandes para ver diferencia
    matrix_sizes = [310, 210, 400, 160]
    
    print("Iniciando comparación de ejecución...")
    print(f"Tamaños de matrices a procesar: {matrix_sizes}")
    print("-" * 50)
    
    # =========================================================================
    # EJECUCIÓN SECUENCIAL
    # =========================================================================
    print("Iniciando ejecución SECUENCIAL...")
    start_sequential = time.time()
    
    # Procesar cada tamaño de matriz uno tras otro (secuencial)
    for i, size in enumerate(matrix_sizes, 1):
        print(f"Secuencial - Matriz {i}/{len(matrix_sizes)}: {size}x{size}")
        time_taken = matrix_multiply(size)
        print(f"  Tiempo: {time_taken:.4f} segundos")
    
    sequential_time = time.time() - start_sequential
    print(f"Tiempo total SECUENCIAL: {sequential_time:.4f} segundos")
    print("-" * 50)
    
    # =========================================================================
    # EJECUCIÓN PARALELA
    # =========================================================================
    print("Iniciando ejecución PARALELA...")
    start_parallel = time.time()
    
    # Usar Pool para procesamiento paralelo con 2 procesos
    # Esto permite ejecutar múltiples multiplicaciones simultáneamente
    with Pool(processes=2) as pool:
        # map aplica la función matrix_multiply a cada elemento de matrix_sizes
        # y distribuye el trabajo entre los procesos disponibles
        print("Distribuyendo trabajo entre 2 procesos...")
        tiempos_paralelos = pool.map(matrix_multiply, matrix_sizes)
        
        # Mostrar tiempos individuales de cada proceso
        for i, (size, time_taken) in enumerate(zip(matrix_sizes, tiempos_paralelos), 1):
            print(f"Paralelo - Matriz {i}/{len(matrix_sizes)}: {size}x{size}")
            print(f"  Tiempo: {time_taken:.4f} segundos")
    
    parallel_time = time.time() - start_parallel
    print(f"Tiempo total PARALELO: {parallel_time:.4f} segundos")
    print("-" * 50)
    
    # =========================================================================
    # ANÁLISIS DE RESULTADOS
    # =========================================================================
    print("ANÁLISIS DE RESULTADOS:")
    print(f"Tiempo secuencial: {sequential_time:.4f} segundos")
    print(f"Tiempo paralelo: {parallel_time:.4f} segundos")
    
    if parallel_time > 0:
        speedup = sequential_time / parallel_time
        efficiency = (speedup / 2) * 100  # Eficiencia considerando 2 procesos
        print(f"Speedup: {speedup:.2f}x")
        print(f"Eficiencia: {efficiency:.1f}%")
        
        if speedup > 1:
            print("El procesamiento paralelo es más rápido")
        else:
            print("El procesamiento secuencial es más rápido (overhead de paralelización)")
    else:
        print("Error: Tiempo paralelo es 0")
    
    return sequential_time, parallel_time

def test_individual_matrices():
    """
    Función de prueba para verificar el tiempo de cada matriz individualmente.
    Útil para debugging y entender la carga de trabajo.
    """
    print("\n" + "="*60)
    print("PRUEBA INDIVIDUAL DE MATRICES")
    print("="*60)
    
    test_sizes = [310, 210, 400, 160]
    
    for size in test_sizes:
        print(f"\nProbando matriz {size}x{size}:")
        tiempo = matrix_multiply(size)
        print(f"Tiempo individual: {tiempo:.4f} segundos")
        
        # Estimación de operaciones (aproximada)
        operations = 2 * (size ** 3)  # n^3 multiplicaciones + n^3 sumas aproximadamente
        print(f"Operaciones estimadas: {operations:,}")
        print(f"Operaciones/segundo: {operations/tiempo:,.0f}")

if __name__ == "__main__":
    """
    Bloque principal que se ejecuta cuando el script se llama directamente.
    Útil para testing independiente del código.
    """
    print("COMPARADOR DE EJECUCIÓN SECUENCIAL VS PARALELA")
    print("=" * 60)
    
    # Ejecutar prueba individual primero
    test_individual_matrices()
    
    print("\n" + "="*60)
    print("COMPARACIÓN PRINCIPAL")
    print("="*60)
    
    # Ejecutar la comparación principal
    seq_time, par_time = compare_execution()
    
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    print(f"TIEMPO SECUENCIAL: {seq_time:.4f} segundos")
    print(f"TIEMPO PARALELO:   {par_time:.4f} segundos")
    
    if par_time > 0:
        improvement = ((seq_time - par_time) / seq_time) * 100
        print(f"MEJORA: {improvement:+.1f}%")