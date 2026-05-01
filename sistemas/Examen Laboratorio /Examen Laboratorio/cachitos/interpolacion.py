def interpolar(valor, puntos_x, puntos_y):
    """Interpola linealmente"""
    if valor <= puntos_x[0]:
        return puntos_y[0]
    if valor >= puntos_x[-1]:
        return puntos_y[-1]
    
    for i in range(len(puntos_x)-1):
        if puntos_x[i] <= valor <= puntos_x[i+1]:
            x1, x2 = puntos_x[i], puntos_x[i+1]
            y1, y2 = puntos_y[i], puntos_y[i+1]
            return y1 + (y2-y1)/(x2-x1)*(valor-x1)
    
    return puntos_y[-1]

# Uso:
voltajes = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
luces = [0, 200, 400, 600, 800, 1000]
lux = interpolar(1.8, voltajes, luces)