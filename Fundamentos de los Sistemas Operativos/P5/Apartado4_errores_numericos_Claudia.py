import math
from typing import Tuple

def serie_ascendente(N: int) -> float:
    """
    Calcula la serie sumando de manera ascendente (de 1 a N)
    S(N) = Σ (1/i^4) desde i=1 hasta N
    """
    suma = 0.0
    for i in range(1, N + 1):
        suma += 1.0 / (i * i * i * i)
    return suma

def serie_descendente(N: int) -> float:
    """
    Calcula la serie sumando de manera descendente (de N a 1)
    S(N) = Σ (1/i^4) desde i=N hasta 1
    """
    suma = 0.0
    for i in range(N, 0, -1):
        suma += 1.0 / (i * i * i * i)
    return suma

def main():
    """
    Calcula el error acumulado para N entre 12000 y 14000
    """
    # Valor real de la serie cuando N es infinito
    valor_real = math.pi**4 / 90.0
    
    error_acumulado_asc = 0.0
    error_acumulado_desc = 0.0
    
    print("Calculando errores para N entre 12000 y 14000...")
    
    for N in range(12000, 14001):
        # Calcular con ambos métodos
        valor_asc = serie_ascendente(N)
        valor_desc = serie_descendente(N)
        
        # Acumular errores (valor absoluto)
        error_acumulado_asc += abs(valor_real - valor_asc)
        error_acumulado_desc += abs(valor_real - valor_desc)
    
    print(f"\n--- RESULTADOS ---")
    print(f"Valor real de la serie (π⁴/90): {valor_real:.15f}")
    print(f"Error acumulado ascendente: {error_acumulado_asc:.15f}")
    print(f"Error acumulado descendente: {error_acumulado_desc:.15f}")
    
    if error_acumulado_asc < error_acumulado_desc:
        print(f"\nLa suma ASCENDENTE tiene MENOS error")
    else:
        print(f"\nLa suma DESCENDENTE tiene MENOS error")

if __name__ == "__main__":
    main()

# COMENTARIOS Y RESPUESTAS:
"""
¿Qué función obtiene menos error, la que hace las sumas de manera ascendente o descendente? 
¿Por qué?

La suma DESCENDENTE generalmente obtiene MENOS error que la ascendente.

Esto se debe a la representación de punto flotante y cómo se acumulan los errores:

1. PRECISIÓN EN SUMA DE NÚMEROS DE MAGNITUD DIFERENTE:
   - En la suma ascendente, comenzamos con números grandes (1/1⁴ = 1.0) y terminamos con números muy pequeños (1/14000⁴ ≈ 2.6e-17)
   - Al sumar números de magnitudes muy diferentes, los números pequeños pueden perderse debido a la precisión limitada

2. PÉRDIDA DE DÍGITOS SIGNIFICATIVOS:
   - Cuando sumamos un número muy pequeño a uno muy grande, muchos dígitos del número pequeño se pierden en la representación
   - Ejemplo: 1.0 + 1e-17 ≈ 1.0 (el 1e-17 se pierde)

3. SUMA DESCENDENTE MÁS PRECISA:
   - Comenzamos con los números más pequeños y progresamos a los más grandes
   - Los números pequeños se suman primero, acumulando precisión antes de añadir números más grandes
   - Esto reduce la pérdida de dígitos significativos

4. ERROR DE REDONDEO ACUMULADO:
   - Cada operación de punto flotante introduce un pequeño error de redondeo
   - En la suma descendente, estos errores se acumulan de manera más favorable

La diferencia puede ser pequeña pero consistente, especialmente para series con muchos términos
donde los últimos términos son extremadamente pequeños comparados con los primeros.
"""