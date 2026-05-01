#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# ARCHIVO: src_model_modifications.py
# DESCRIPCIÓN: Código EXACTO que debe insertarse en la función compare_execution
#              del archivo src/model.py del proyecto original
# USO: Reemplazar SOLO la sección marcada con ##CODE FOR STUDENTS en src/model.py
# AUTOR: Claudia Maria Lopez Bombin Y Gonzalo Velasco Lucas
# FECHA: Noviembre 2025
# =============================================================================

import numpy as np
import time
from multiprocessing import Pool

# =============================================================================
# FUNCIÓN AUXILIAR: matrix_multiply
# =============================================================================
def matrix_multiply(size: int) -> float:
    """
    Realiza multiplicación de matrices cuadradas del tamaño especificado
    y devuelve el tiempo de ejecución.
    
    Esta función es utilizada internamente por compare_execution().
    
    Args:
        size (int): Tamaño de la matriz cuadrada (size x size)
        
    Returns:
        float: Tiempo en segundos que tomó la multiplicación
    """
    # Generar dos matrices aleatorias del tamaño especificado
    A = np.random.rand(size, size)
    B = np.random.rand(size, size)
    
    # Medir el tiempo exacto de la multiplicación
    start_time = time.time()
    result = np.dot(A, B)  # Multiplicación de matrices optimizada con NumPy
    end_time = time.time()
    
    return end_time - start_time

# =============================================================================
# CÓDIGO EXACTO PARA INSERTAR EN src/model.py
# =============================================================================
"""
EN EL ARCHIVO src/model.py, REEMPLAZAR ESTA SECCIÓN:

    matrix_sizes = [310, 210, 400, 160]
    ##CODE FOR STUDENTS
    # END CODE FOR STUDENTS

CON ESTE CÓDIGO:
"""

# === INICIO DEL CÓDIGO A INSERTAR ===
    # EJECUCIÓN SECUENCIAL
    start_sequential = time.time()
    for size in matrix_sizes:
        matrix_multiply(size)
    sequential_time = time.time() - start_sequential

    # EJECUCIÓN PARALELA  
    start_parallel = time.time()
    with Pool(processes=2) as pool:
        pool.map(matrix_multiply, matrix_sizes)
    parallel_time = time.time() - start_parallel
# === FIN DEL CÓDIGO A INSERTAR ===

"""
NOTA: También se debe agregar la función auxiliar matrix_multiply
en el mismo archivo src/model.py, fuera de la función compare_execution.
"""