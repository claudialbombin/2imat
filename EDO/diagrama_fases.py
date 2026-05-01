#!/usr/bin/env python3
"""
Versión simplificada para ver rápido los dos casos
"""

import numpy as np
import matplotlib.pyplot as plt

# Parámetros
m, k = 1.0, 1.0

# Crear figura con 2 subplots
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Casos a analizar
casos = [(-0.5, 'Resorte Duro (a<0)', axes[0]), 
         (0.5, 'Resorte Blando (a>0)', axes[1])]

for a, titulo, ax in casos:
    # Campo vectorial
    x = np.linspace(-2.5, 2.5, 20)
    v = np.linspace(-2.5, 2.5, 20)
    X, V = np.meshgrid(x, v)
    
    dX = V
    dV = (a * X**3 - k * X) / m
    
    # Normalizar
    norm = np.sqrt(dX**2 + dV**2)
    norm[norm == 0] = 1
    dX_norm = dX / norm
    dV_norm = dV / norm
    
    # Dibujar campo vectorial
    ax.quiver(X, V, dX_norm, dV_norm, color='gray', alpha=0.6, width=0.005)
    
    # Curvas de energía constante
    E = 0.5 * m * V**2 + 0.5 * k * X**2 - (a/4.0) * X**4
    niveles = np.linspace(0.1, 2, 15) if a < 0 else np.linspace(-0.5, 2, 15)
    ax.contour(X, V, E, levels=niveles, colors='blue', alpha=0.7, linewidths=1)
    
    # Puntos críticos
    if a > 0:
        x_silla = np.sqrt(k/a)
        ax.plot([-x_silla, 0, x_silla], [0, 0, 0], 'ro', markersize=8)
        ax.plot(0, 0, 'go', markersize=8)
    else:
        ax.plot(0, 0, 'go', markersize=8, label='Centro')
    
    ax.set_xlabel('x (posición)')
    ax.set_ylabel('v (velocidad)')
    ax.set_title(titulo)
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color='k', alpha=0.3)
    ax.axvline(0, color='k', alpha=0.3)
    ax.set_xlim([-2.5, 2.5])
    ax.set_ylim([-2.5, 2.5])

plt.tight_layout()
plt.show()
