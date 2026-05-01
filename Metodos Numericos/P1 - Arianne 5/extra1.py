import numpy as np

print("EXTRA 1: Distintos formatos de punto flotante en NumPy")
exact_decimal = 0.1  # Esto en Python es float64 ya aproximado
exact_fraction = 1/10  # Mejor usar fracción para claridad

# Usaremos la representación exacta decimal de 0.1 como referencia
print(f"Valor exacto matemático 1/10 = {exact_fraction}")

for dtype in [np.float16, np.float32, np.float64, np.longdouble]:
    # Convertir 0.1 exactamente al tipo deseado
    val = dtype(exact_fraction)
    
    # El error real es la diferencia con el valor exacto matemático
    # Como no podemos tener "1/10 exacto" en Python, usamos decimal con alta precisión
    error = abs(float(val) - exact_fraction)
    
    print(f"{dtype.__name__:12} -> Valor almacenado: {val:.20f}")
    print(f"             Error absoluto: {error:.20e}")
    print(f"             Representación binaria (hex): {val.view('int16' if dtype == np.float16 else 'int32' if dtype == np.float32 else 'int64'):X}")
    print()
