PERIODO_SCAN = 0.05  # 50 ms (típico en exámenes)

while True:
    inicio_ciclo = time.time()
    
    # TODO: tu código aquí
    
    tiempo_ejecucion = time.time() - inicio_ciclo
    if tiempo_ejecucion < PERIODO_SCAN:
        time.sleep(PERIODO_SCAN - tiempo_ejecucion)