import matplotlib.pyplot as plt
import numpy as np
import time

# ==============================
# EJERCICIO 4: Función para Newton
# ==============================

def newton_interpolant_from_points(x, y):
    """
    Construye el interpolador en forma de Newton a partir de nodos x y valores y=f(x).
    Devuelve:
      - coeffs: [a0, a1, ..., an] donde ak = f[x0,...,xk]
      - dd: tabla de diferencias divididas
    """
    n = len(x)
    if n != len(y):
        raise ValueError("x e y deben tener la misma longitud")
    
    # Tabla de diferencias divididas
    dd = [[0.0] * n for _ in range(n)]
    
    # Primera columna: f[xi] = yi
    for i in range(n):
        dd[i][0] = float(y[i])
    
    # Calcular diferencias divididas de orden superior
    for j in range(1, n):
        for i in range(n - j):
            denom = x[i + j] - x[i]
            if abs(denom) < 1e-15:  # Evitar división por cero
                raise ValueError(f"Nodos repetidos o muy cercanos: x[{i}]={x[i]}, x[{i+j}]={x[i+j]}")
            dd[i][j] = (dd[i + 1][j - 1] - dd[i][j - 1]) / denom
    
    # Coeficientes: primera fila de cada columna
    coeffs = [dd[0][k] for k in range(n)]
    return coeffs, dd

def newton_interpolant_from_function(f, x_nodes):
    """
    Ejercicio 4: dada una función f y nodos x_nodes, construye el interpolador de Newton.
    """
    y = [f(xi) for xi in x_nodes]
    coeffs, dd = newton_interpolant_from_points(x_nodes, y)
    return coeffs, dd, x_nodes, y

def newton_eval(x_nodes, coeffs, x):
    """
    Evalúa P(x) en el punto x usando la forma de Newton (Horner adaptado).
    """
    n = len(coeffs)
    if n == 0:
        return 0.0
    
    p = coeffs[-1]  # Último coeficiente
    for k in range(n - 2, -1, -1):
        p = p * (x - x_nodes[k]) + coeffs[k]
    return p

# ==============================
# EJERCICIO 5: Gráfica de comparación
# ==============================

def plot_interpolation_comparison(f, coeffs, x_nodes, x_range=(-5, 5), num_points=1000, title=""):
    """
    Representa la función original y el polinomio interpolador.
    """
    a, b = x_range
    x_fine = np.linspace(a, b, num_points)
    
    # Evaluar función original
    y_fine = f(x_fine)
    
    # Evaluar polinomio interpolador
    y_interp = np.array([newton_eval(x_nodes, coeffs, xi) for xi in x_fine])
    
    # Calcular error
    error = np.abs(y_fine - y_interp)
    max_error = np.max(error)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Subgráfica 1: Comparación
    axes[0].plot(x_fine, y_fine, 'b-', label='Función original', linewidth=2)
    axes[0].plot(x_fine, y_interp, 'r--', label='Polinomio interpolador', linewidth=2)
    axes[0].scatter(x_nodes, f(x_nodes), color='green', s=50, zorder=5, label='Nodos de interpolación')
    axes[0].set_xlabel('x')
    axes[0].set_ylabel('y')
    axes[0].set_title(f'{title}\nComparación: función vs interpolador')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Subgráfica 2: Error
    axes[1].plot(x_fine, error, 'g-', label='Error absoluto', linewidth=2)
    axes[1].set_xlabel('x')
    axes[1].set_ylabel('Error')
    axes[1].set_title(f'Error de interpolación (máx: {max_error:.2e})')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return max_error

# ==============================
# EJERCICIO 6: Función de Runge
# ==============================

def runge_function(x):
    """f(x) = 1/(1 + x^2) - Función de Runge"""
    return 1 / (1 + x**2)

def equidistant_nodes(a, b, n):
    """Genera n+1 nodos equidistantes en [a, b]"""
    return np.linspace(a, b, n + 1)

def interpolate_runge_function(degrees, x_range=(-5, 5)):
    """
    Interpola la función de Runge con polinomios de los grados especificados.
    """
    a, b = x_range
    errors = []
    
    for degree in degrees:
        print(f"\n=== Grado {degree} ===")
        
        # Generar nodos equidistantes
        x_nodes = equidistant_nodes(a, b, degree)
        print(f"Nodos: {x_nodes}")
        
        # Calcular interpolador
        coeffs, dd, _, _ = newton_interpolant_from_function(runge_function, x_nodes)
        
        # Evaluar y graficar
        max_error = plot_interpolation_comparison(
            runge_function, coeffs, x_nodes, x_range, 
            title=f'Función de Runge - Polinomio grado {degree}'
        )
        
        errors.append(max_error)
    
    return errors

# ==============================
# EJERCICIO 7: Análisis del efecto Runge
# ==============================

def analyze_runge_phenomenon():
    """
    Analiza el fenómeno de Runge para diferentes grados.
    """
    degrees = [4, 8, 12, 16]
    
    print("=" * 60)
    print("EJERCICIO 6: Fenómeno de Runge")
    print("=" * 60)
    print("Función: f(x) = 1/(1 + x^2)")
    print("Intervalo: [-5, 5]")
    print("Nodos: equidistantes")
    print("=" * 60)
    
    errors = interpolate_runge_function(degrees)
    
    # Análisis de los resultados
    print("\n" + "=" * 60)
    print("EJERCICIO 7: Análisis de resultados")
    print("=" * 60)
    
    print("\nRESUMEN DE ERRORES MÁXIMOS:")
    for degree, error in zip(degrees, errors):
        print(f"  Grado {degree}: error máximo = {error:.2e}")
    
    print("\nOBSERVACIONES:")
    print("1. Se observa el fenómeno de Runge: a medida que aumenta el grado,")
    print("   aparecen oscilaciones grandes cerca de los extremos del intervalo.")
    print("2. El error máximo NO disminuye monotónicamente con el grado.")
    print("3. Las oscilaciones son más pronunciadas en los extremos [-5, 5].")
    
    print("\nEXPLICACIÓN TEÓRICA (Error de interpolación):")
    print("El error de interpolación está dado por:")
    print("  f(x) - P_n(x) = f^(n+1)(ξ)/(n+1)! * Π_{i=0}^n (x - x_i)")
    print("Para la función de Runge en [-5, 5]:")
    print("1. Las derivadas de orden alto crecen rápidamente con n.")
    print("2. El término Π_{i=0}^n (x - x_i) es grande en los extremos para nodos equidistantes.")
    print("3. La combinación hace que el error explote cerca de los extremos.")
    
    print("\nSOLUCIONES POSIBLES:")
    print("1. Usar nodos de Chebyshev (más densos en los extremos).")
    print("2. Usar interpolación por trozos (splines).")
    print("3. Reducir el grado del polinomio o ajustar el intervalo.")
    
    return degrees, errors

# ==============================
# PRUEBAS Y EJECUCIÓN
# ==============================

if __name__ == "__main__":
    # Prueba básica del Ejercicio 4
    print("=" * 60)
    print("PRUEBA DEL EJERCICIO 4: Interpolador de Newton")
    print("=" * 60)
    
    # Función de prueba
    def test_f(x):
        return np.sin(x)
    
    x_test = [-1, -0.5, 0, 0.5, 1]
    coeffs, dd, x_nodes, y_nodes = newton_interpolant_from_function(test_f, x_test)
    
    print(f"Nodos: {x_nodes}")
    print(f"Valores: {y_nodes}")
    print(f"Coeficientes (diferencias divididas):")
    for i, c in enumerate(coeffs):
        print(f"  a[{i}] = {c:.6f}")
    
    # Evaluar en un punto
    x_eval = 0.3
    p_val = newton_eval(x_nodes, coeffs, x_eval)
    f_val = test_f(x_eval)
    error = abs(p_val - f_val)
    print(f"\nEvaluación en x = {x_eval}:")
    print(f"  P({x_eval}) = {p_val:.8f}")
    print(f"  f({x_eval}) = {f_val:.8f}")
    print(f"  Error = {error:.2e}")
    
    # Ejercicio 5: Gráfica de prueba
    print("\n" + "=" * 60)
    print("EJERCICIO 5: Gráfica de comparación (prueba con sin(x))")
    print("=" * 60)
    
    plot_interpolation_comparison(
        test_f, coeffs, x_nodes, x_range=(-1.5, 1.5),
        title='Prueba: sin(x) - Polinomio grado 4'
    )
    
    # Ejercicios 6 y 7: Fenómeno de Runge
    analyze_runge_phenomenon()
    
    print("\n" + "=" * 60)
    print("RESPUESTAS A LAS PREGUNTAS DEL EJERCICIO 7:")
    print("=" * 60)
    print("\n7a) En general, NO es cierto que lim_{n→∞} P_n(x) = f(x).")
    print("   El ejemplo de Runge muestra que aumentar n puede empeorar la aproximación.")
    print("   La convergencia uniforme no está garantizada para cualquier función y distribución de nodos.")
    
    print("\n7b) La posición de los puntos SÍ es importante:")
    print("   - Nodos equidistantes: pueden causar el fenómeno de Runge.")
    print("   - Nodos de Chebyshev: minimizan el máximo del término Π(x - x_i).")
    print("   - Nodos ajustados a la función: mejoran la convergencia.")
    print("   Ejemplo: Para f(x)=|x|, los nodos de Chebyshev dan mejor convergencia que los equidistantes.")