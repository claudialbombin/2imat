import matplotlib.pyplot as plt
import numpy as np

# Ejercicio 4
class SplineCubicoNatural:
    def __init__(self, x_nodos, y_nodos, M):
        self.x_nodos = x_nodos
        self.y_nodos = y_nodos
        self.M = M

    def __call__(self, x_eval):
        return evaluar_spline_cubico(self.x_nodos, self.y_nodos, self.M, x_eval)

def construir_momentos_naturales(x_nodos: list, y_nodos: list):
    n = len(x_nodos) - 1
    if n < 1:
        raise ValueError("Se necesitan al menos 2 nodos.")
    if len(y_nodos) != n + 1:
        raise ValueError("y_nodos debe tener la misma longitud que x_nodos.")

    i = 0
    while i < n:
        if not (x_nodos[i] < x_nodos[i + 1]):
            raise ValueError("x_nodos debe ser estrictamente creciente (sin repetidos).")
        i += 1

    if n == 1:
        return [0.0, 0.0]

    h = [x_nodos[k + 1] - x_nodos[k] for k in range(n)]

    m = n - 1
    a = [0.0] * m
    b = [2.0] * m
    c = [0.0] * m
    d = [0.0] * m

    j = 1
    while j <= n - 1:
        hj = h[j - 1]
        hj1 = h[j]

        denom = hj + hj1
        lam = hj1 / denom
        mu = hj / denom

        pendiente_der = (y_nodos[j + 1] - y_nodos[j]) / hj1
        pendiente_izq = (y_nodos[j] - y_nodos[j - 1]) / hj

        dj = (6.0 / denom) * (pendiente_der - pendiente_izq)

        idx = j - 1
        a[idx] = mu
        c[idx] = lam
        d[idx] = dj
        j += 1

    c_prime = [0.0] * m
    d_prime = [0.0] * m

    c_prime[0] = c[0] / b[0]
    d_prime[0] = d[0] / b[0]

    i = 1
    while i < m:
        den = b[i] - a[i] * c_prime[i - 1]
        if i < m - 1:
            c_prime[i] = c[i] / den
        d_prime[i] = (d[i] - a[i] * d_prime[i - 1]) / den
        i += 1

    M_interior = [0.0] * m
    M_interior[m - 1] = d_prime[m - 1]

    i = m - 2
    while i >= 0:
        M_interior[i] = d_prime[i] - c_prime[i] * M_interior[i + 1]
        i -= 1

    M = [0.0] + M_interior + [0.0]
    return M

def evaluar_spline_cubico(x_nodos: list, y_nodos: list, M, x_eval):
    n = len(x_nodos) - 1
    if len(y_nodos) != n + 1 or len(M) != n + 1:
        raise ValueError("Dimensiones incompatibles entre x_nodos, y_nodos y M.")

    x0 = x_nodos[0]
    xn = x_nodos[n]

    # Solo numpy: detecta escalar también para np.float64, etc.
    es_escalar = np.isscalar(x_eval)
    if es_escalar:
        x_list = [float(x_eval)]
    else:
        x_list = [float(v) for v in x_eval]

    # Convertimos una vez para usar searchsorted (equivalente a bisect_right)
    x_arr = np.asarray(x_nodos, dtype=float)

    buckets = {}
    idx = 0
    while idx < len(x_list):
        x = x_list[idx]
        if x < x0 or x > xn:
            raise ValueError("Hay puntos de evaluación fuera del intervalo [x0, xn].")

        if x == xn:
            j = n - 1
        else:
            j = int(np.searchsorted(x_arr, x, side="right") - 1)
            if j < 0:
                j = 0
            if j > n - 1:
                j = n - 1

        if j in buckets:
            buckets[j].append(idx)
        else:
            buckets[j] = [idx]
        idx += 1

    out = [0.0] * len(x_list)

    for j, posiciones in buckets.items():
        xj = x_nodos[j]
        xj1 = x_nodos[j + 1]
        hj1 = xj1 - xj

        yj = y_nodos[j]
        yj1 = y_nodos[j + 1]
        Mj = M[j]
        Mj1 = M[j + 1]

        A = (Mj1 - Mj) / (6.0 * hj1)
        B = Mj / 2.0
        C = (yj1 - yj) / hj1 - (2.0 * Mj + Mj1) * hj1 / 6.0
        D = yj

        k = 0
        while k < len(posiciones):
            p = posiciones[k]
            t = x_list[p] - xj
            out[p] = A * (t ** 3) + B * (t ** 2) + C * t + D
            k += 1

    if es_escalar:
        return out[0]
    return out

def spline_cubico_natural(f, x_nodos: list):
    n = len(x_nodos) - 1
    if n < 1:
        raise ValueError("Se necesitan al menos 2 nodos.")

    y_nodos = [float(f(x)) for x in x_nodos]
    M = construir_momentos_naturales(x_nodos, y_nodos)

    S = SplineCubicoNatural(x_nodos, y_nodos, M)
    return S, y_nodos

# Ejercicio 5
def dibujar_spline_y_funcion(f, a, b, n, puntos_grafica=1000):
    """
    Dibuja el spline cúbico y la función original
    
    Args:
        f: función original
        a, b: límites del intervalo [a, b]
        n: número de subintervalos (n+1 nodos)
        puntos_grafica: número de puntos para graficar
    """
    #print('entro dibujar')
    # Calcular el spline
    x_nodos = np.linspace(a, b, n+1)
    spline, y_nodos = spline_cubico_natural(f, x_nodos)
    
    # Crear puntos para graficar (más densos para curvas suaves)
    x_grafica = np.linspace(a, b, puntos_grafica)
    y_funcion = f(x_grafica)
    y_spline = spline(x_grafica)
    
    # Configurar la figura
    plt.figure(figsize=(10, 6))
    
    # Graficar la función original
    plt.plot(x_grafica, y_funcion, 'b-', label='Función original', linewidth=2, alpha=0.7)
    
    # Graficar el spline
    plt.plot(x_grafica, y_spline, 'r--', label='Spline cúbico', linewidth=2)
    
    # Marcar los nodos
    plt.plot(x_nodos, y_nodos, 'go', markersize=8, label=f'Nodos (n+1={n+1})')
    
    # Configurar el gráfico
    plt.grid(True, alpha=0.3)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title(f'Comparación: Función original vs Spline cúbico con {n+1} nodos')
    plt.legend()
    
    # Mostrar el error máximo aproximado
    error_max = np.max(np.abs(y_funcion - y_spline))
    plt.text(0.02, 0.98, f'Error máximo: {error_max:.2e}', 
             transform=plt.gca().transAxes, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.show()
    #print('salgo dibujar')

def ejercicio6():
    """
    Función principal con ejemplos de uso
    """
    #print('entro main')
    f = lambda x: 1/(1 + x**2)
    dibujar_spline_y_funcion(f, -5, 5, 16)  # 17nodos

ejercicio6()

"""
Comparando el resultado con los de la practica anterior, observamos que el spline cúbico natural se ajusta mucho mejor a la función original, 
especialmente en los extremos del intervalo, comparado con el polinomio de interpolación de grado 16 que presentaba oscilaciones significativas 
(fenómeno de Runge). El error máximo del spline es considerablemente menor, lo que confirma que el spline cúbico natural es una mejor opción 
para la interpolación en este caso.
"""