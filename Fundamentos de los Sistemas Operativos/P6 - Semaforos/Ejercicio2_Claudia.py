from threading import Thread, Semaphore
import time

# Variables globales compartidas
costes = [0.5, 1, 0.25, 0.3, 0.5, 0.25]
contador_hilos = 0
indice_hilo_actual = -1
contador_total_variable = 0.0
hilos_procesados = 0

# Semáforos
mutex_contador = Semaphore(1)  # Protege contadores globales
zona_espera = Semaphore(3)     # Controla capacidad zona de espera (3 hilos max)
hilo_listo = Semaphore(0)      # Señala que hay hilo listo para procesar
gestor_libre = Semaphore(1)    # Controla disponibilidad del gestor
mutex_procesamiento = Semaphore(1)  # Protege el procesamiento del gestor

def hilo_trabajo(id_hilo):
	"""Función para los hilos de trabajo con coste asociado"""
	global contador_hilos, indice_hilo_actual, hilos_procesados
	
	# Esperar si la zona de espera está llena
	zona_espera.acquire()
	
	# Entrar a la zona de espera
	mutex_contador.acquire()
	contador_hilos += 1
	indice_actual = contador_hilos - 1
	mutex_contador.release()
	
	print(f"Soy el hilo {id_hilo + 1}, aviso al gestor")
	
	# Señalar al gestor que hay un hilo listo
	hilo_listo.release()
	
	# Esperar a que el gestor nos procese
	gestor_libre.acquire()
	
	# El gestor nos ha procesado, podemos terminar
	zona_espera.release()
	
	print(f"Terminado el hilo {id_hilo + 1}")

def gestor():
	"""Función para el hilo gestor"""
	global contador_total_variable, hilos_procesados
	
	while hilos_procesados < 6:
		# Esperar a que haya un hilo listo
		hilo_listo.acquire()
		
		# Procesar el hilo
		mutex_procesamiento.acquire()
		
		# Obtener el coste del siguiente hilo
		mutex_contador.acquire()
		if hilos_procesados < 6:
			coste_actual = costes[hilos_procesados]
			id_hilo_actual = hilos_procesados + 1
			hilos_procesados += 1
		else:
			mutex_contador.release()
			mutex_procesamiento.release()
			break
		
		mutex_contador.release()
		
		# Procesar el hilo
		print(f"Soy el gestor. Proceso el hilo {id_hilo_actual} y duermo {coste_actual} segundos")
		contador_total_variable += coste_actual
		time.sleep(coste_actual)
		
		# Liberar al hilo procesado
		mutex_procesamiento.release()
		gestor_libre.release()
	
	print(f"El contador final es {contador_total_variable}")

if __name__ == "__main__":
	threads = []
	
	# Crear hilo gestor
	g = Thread(target=gestor)
	threads.append(g)
	
	# Crear 6 hilos de trabajo
	for i in range(6):
		t = Thread(target=hilo_trabajo, args=(i,))
		threads.append(t)
	
	# Iniciar todos los hilos
	for t in threads:
		t.start()
	
	# Esperar a que terminen
	for t in threads:
		t.join()
	
	print("Todos los hilos han terminado")