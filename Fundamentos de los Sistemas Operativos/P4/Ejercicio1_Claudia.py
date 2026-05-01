from threading import Thread
import time

# Variable global para indicar si el proceso ha terminado
terminado = False

# Función que ejecuta el temporizador en un hilo separado
def thread_task(segundos):
    global terminado
    restante = segundos
    # Mientras queden segundos y no se haya terminado, muestra el mensaje cada 5 segundos
    while restante > 0 and not terminado:
        print(f'El usuario dispone de {restante} segundos para introducir un nombre y un apellido.')
        time.sleep(5)  # Espera 5 segundos antes de mostrar el siguiente mensaje
        restante -= 5
    # Si el tiempo se agota y no se ha terminado, muestra mensaje de tiempo agotado
    if not terminado:
        print("No se ha introducido ningun nombre")
        terminado = True  # Marca como terminado para que el hilo principal lo sepa

if __name__ == "__main__":
    temporizador = 20  # Tiempo total disponible para introducir los datos

    # Creamos y lanzamos el hilo del temporizador
    hilo_temp = Thread(target=thread_task, args=(temporizador,))
    hilo_temp.start()

    # Guardamos el tiempo de inicio antes de pedir los datos
    inicio = time.time()
    nombre = input("Nombre: ")      # Pedimos el nombre al usuario
    apellido = input("Apellido: ")  # Pedimos el apellido al usuario
    fin = time.time()               # Guardamos el tiempo al terminar

    # Comprobamos si el usuario ha tardado demasiado o si el temporizador ya terminó
    if fin - inicio > temporizador or terminado:
        print("Ha introducido el nombre demasiado tarde")
        terminado = True  # Aseguramos que el hilo del temporizador termine si no lo ha hecho
    else:
        terminado = True  # Indicamos que se ha terminado correctamente
        print(f"Bienvenido/a {nombre} {apellido}")

    # Esperamos a que el hilo del temporizador termine antes de finalizar el programa
    hilo_temp.join()
