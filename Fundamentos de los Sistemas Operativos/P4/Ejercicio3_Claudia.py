from multiprocessing import Process, current_process
import os
import time

# Función que ejecuta un bucle infinito e imprime información del proceso
def bucle_infinito(nombre):
    print(f"Nombre: {nombre}, PID: {os.getpid()}, PPID: {os.getppid()}")
    while True:
        time.sleep(1)  # El proceso se queda "vivo" sin hacer nada útil

# Función para la configuración 2: cada proceso puede crear otro proceso hijo
def hijo_config2(nombre, crear_otro):
    print(f"Nombre: {nombre}, PID: {os.getpid()}, PPID: {os.getppid()}")
    if crear_otro:
        # Si se indica, crea un proceso hijo (nieto respecto al principal)
        p = Process(target=hijo_config2, args=(f"{nombre}_nieto", False), name=f"{nombre}_nieto")
        p.start()
        p.join()  # Espera a que su hijo termine (en este caso nunca termina)

if __name__ == "__main__":
    # Pedimos al usuario la configuración deseada
    try:
        opcion = int(input("Introduce 1 para configuración 1, 2 para configuración 2: "))
    except ValueError:
        print("No has introducido un número válido.")
        exit()

    # Imprime información del proceso principal
    print(f"Nombre: principal, PID: {os.getpid()}")

    if opcion == 1:
        # CONFIGURACIÓN 1: Tres procesos hijos independientes
        hijos = []
        for i in range(1, 4):
            # Creamos cada proceso hijo con un nombre específico
            p = Process(target=bucle_infinito, args=(f"proceso-hijo{i}",), name=f"proceso-hijo{i}")
            hijos.append(p)
            p.start()  # Lanzamos el proceso hijo

        # Esperamos 15 segundos antes de empezar a terminar procesos
        time.sleep(15)
        print("El principal termina proceso-hijo1")
        hijos[0].terminate()  # Terminamos el primer hijo
        hijos[0].join()       # Esperamos a que termine

        time.sleep(5)
        print("El principal termina proceso-hijo2")
        hijos[1].terminate()  # Terminamos el segundo hijo
        hijos[1].join()

        time.sleep(5)
        print("El principal termina proceso-hijo3")
        hijos[2].terminate()  # Terminamos el tercer hijo
        hijos[2].join()

        print("El principal ha terminado todos los hijos.")

    elif opcion == 2:
        # CONFIGURACIÓN 2: Proceso hijo crea nieto, que crea bisnieto
        # Solo el primer hijo es gestionado por el principal
        p1 = Process(target=hijo_config2, args=("proceso-hijo1", True), name="proceso-hijo1")
        p1.start()
        # Esperamos 15 segundos antes de terminar el primer hijo
        time.sleep(15)
        print("El principal termina proceso-hijo1")
        p1.terminate()  # Terminamos solo el primer hijo
        p1.join()
        print("El principal ha terminado proceso-hijo1.")
    else:
        print("Opción no válida. El programa finaliza.")

# -------------------------------
# RESPUESTAS:
# Configuración 1:
#   El proceso principal termina correctamente los tres procesos hijos usando terminate().
#   Los procesos hijos finalizan, pero terminate() puede no liberar recursos correctamente
#   (no es una finalización "limpia", el proceso se mata abruptamente).
#
# Configuración 2:
#   El proceso principal solo termina el primer proceso hijo (proceso-hijo1).
#   Los procesos nieto y bisnieto siguen ejecutándose en segundo plano (zombies/orfanos),
#   porque el principal no tiene referencia a ellos y no los termina explícitamente.
#   Por tanto, NO finalizan de manera correcta.
# -------------------------------