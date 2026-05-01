from threading import Thread, Semaphore
import time

# Variables globales y semáforos
max_visitantes = 40
capacidad_exposicion = Semaphore(max_visitantes)

# Para la sincronización de grupos
mutex = Semaphore(1)
visitantes_listos = 0
barrera_guia = Semaphore(0)
barrera_visitantes = Semaphore(0)

# Control de finalización
total_visitantes = 100
visitantes_atendidos = 0
grupos_completados = 0
todos_visitantes_creados = False

def primera_parte(idx: int):
    print(f"Soy {idx}. Estoy haciendo la primera parte")
    return

def segunda_parte():
    print(f"Estoy haciendo la segunda parte (guia) 5 secs de espera")
    time.sleep(2)  # Reducido para pruebas
    return

def visitante(idx: int):
    """Función para cada visitante"""
    global visitantes_listos, visitantes_atendidos
    
    # Esperar si hay espacio en la exposición
    capacidad_exposicion.acquire()
    
    # Primera parte - visita independiente
    primera_parte(idx)
    
    # Prepararse para la segunda parte
    mutex.acquire()
    visitantes_listos += 1
    print(f"Visitante {idx} listo para segunda parte. Total listos: {visitantes_listos}")
    
    # Si hay 10 visitantes listos, avisar al guía
    if visitantes_listos >= 10:
        barrera_guia.release()
    mutex.release()
    
    # Esperar a que el guía comience la segunda parte
    barrera_visitantes.acquire()
    
    # Segunda parte completada, salir de la exposición
    mutex.acquire()
    visitantes_atendidos += 1
    capacidad_exposicion.release()
    print(f"Visitante {idx} ha completado ambas partes. Total atendidos: {visitantes_atendidos}/100")
    mutex.release()

def guia():
    """Función para el hilo guía"""
    global visitantes_listos, visitantes_atendidos, grupos_completados
    
    while visitantes_atendidos < total_visitantes:
        # Esperar a que haya al menos 10 visitantes listos
        # Pero con timeout para verificar si ya terminamos
        barrera_guia.acquire()
        
        # Verificar que todavía hay visitantes por atender
        mutex.acquire()
        if visitantes_atendidos >= total_visitantes:
            mutex.release()
            break
            
        # Solo procesar si hay al menos 10 visitantes listos
        if visitantes_listos >= 10:
            # Realizar la segunda parte con el grupo de 10
            segunda_parte()
            
            # Liberar a 10 visitantes del grupo actual
            for _ in range(10):
                barrera_visitantes.release()
            
            visitantes_listos -= 10
            grupos_completados += 1
            print(f"Grupo {grupos_completados} de 10 visitantes liberado. Visitantes atendidos: {visitantes_atendidos + 10}/100")
            
            # Si todavía quedan visitantes listos, reactivar el guía
            if visitantes_listos >= 10:
                barrera_guia.release()
    
        mutex.release()
        #print('salí')
    
    # Liberar a cualquier visitante que pueda estar esperando
    # mutex.acquire()
    # print('voya a entar')
    # visitantes_restantes = visitantes_listos
    # for _ in range(visitantes_restantes):
    #     barrera_visitantes.release()
    # mutex.release()

if __name__ == "__main__":
    # Crear lista de hilos
    hilos_visitantes = []
    for i in range(100):
        hilo = Thread(target=visitante, args=(i,))
        hilos_visitantes.append(hilo)
    
    hilo_guia = Thread(target=guia)
    
    # Iniciar todos los hilos
    for hilo in hilos_visitantes:
        #print("Iniciando visitante", hilo)
        hilo.start()
    hilo_guia.start()
    
    # Esperar a que terminen
    for hilo in hilos_visitantes:
        #print("Esperando al visitante", hilo)
        hilo.join()
    
    hilo_guia.join()
    
    print(f"Todas las visitas completadas. Total: {visitantes_atendidos} visitantes")
    print(f"Grupos completados: {grupos_completados}")