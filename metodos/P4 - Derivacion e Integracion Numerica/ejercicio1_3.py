import numpy as np

def Euler(f, a, b, n, alpha):
    
    h = (b - a) / n
    
    # nodos
    x = np.linspace(a, b, n+1)
    
    # vector solución
    y = np.zeros(n+1)
    
    # condición inicial
    y[0] = alpha
    
    # iteración de Euler
    for i in range(n):
        y[i+1] = y[i] + h * f(x[i], y[i])
    
    return x, y