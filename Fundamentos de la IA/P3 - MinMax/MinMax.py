def minimax_con_secuencia(n, es_max, camino=None):
    if camino is None:
        camino = []
    
    # Mostrar el estado actual
    estado_actual = f"{n} (Turno: {'MAX' if es_max else 'MIN'})"
    
    # Caso base: si llegamos a 0, el jugador anterior ganó
    if n == 0:
        ganador = "MIN" if es_max else "MAX"
        camino_final = camino + [f"0 → GANA {ganador}"]
        return (1 if ganador == "MAX" else -1, camino_final)
    
    if es_max:
        mejor_valor = -2
        mejor_camino = None
        
        # Opción RESTAR 1
        if n-1 >= 0:
            valor, cam = minimax_con_secuencia(n-1, False, camino + [f"{n} -1"])
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_camino = cam
        
        # Opción DIVIDIR entre 2
        if n//2 >= 0:
            valor, cam = minimax_con_secuencia(n//2, False, camino + [f"{n} ÷2"])
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_camino = cam
        
        return (mejor_valor, mejor_camino)
    
    else:  # Turno de MIN
        mejor_valor = 2
        mejor_camino = None
        
        # Opción RESTAR 1
        if n-1 >= 0:
            valor, cam = minimax_con_secuencia(n-1, True, camino + [f"{n} -1"])
            if valor < mejor_valor:
                mejor_valor = valor
                mejor_camino = cam
        
        # Opción DIVIDIR entre 2
        if n//2 >= 0:
            valor, cam = minimax_con_secuencia(n//2, True, camino + [f"{n} ÷2"])
            if valor < mejor_valor:
                mejor_valor = valor
                mejor_camino = cam
        
        return (mejor_valor, mejor_camino)

# Probar con ejemplos
print("=== SECUENCIAS DE JUEGO ÓPTIMAS ===\n")

valores_prueba = [3, 5, 6]
for n in valores_prueba:
    print(f"Para n = {n}:")
    valor, secuencia = minimax_con_secuencia(n, True)
    
    # Formatear la secuencia para mejor visualización
    print("Secuencia óptima:")
    for i in range(0, len(secuencia), 2):
        if i+1 < len(secuencia):
            print(f"  {secuencia[i]} → {secuencia[i+1]}")
        else:
            print(f"  {secuencia[i]}")
    
    ganador = "MAX" if valor == 1 else "MIN"
    print(f"Resultado: {ganador} gana con juego perfecto\n")
    print("-" * 40)