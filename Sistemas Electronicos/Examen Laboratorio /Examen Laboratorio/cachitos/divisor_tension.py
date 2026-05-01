# Calcular Vout del divisor
def vout_divisor(r1, r2, vin=3.3):
    """R1 arriba, R2 abajo"""
    return vin * r2 / (r1 + r2)

# Calcular resistencia desconocida (sensor abajo)
def r_desde_vout(vout, r_fija, vin=3.3):
    """Sensor en posición inferior"""
    if vout >= vin:
        return float('inf')
    return (vout * r_fija) / (vin - vout)

# Calcular resistencia desconocida (sensor arriba)
def r_desde_vout_arriba(vout, r_fija, vin=3.3):
    """Sensor en posición superior"""
    if vout <= 0:
        return float('inf')
    return (vin * r_fija / vout) - r_fija