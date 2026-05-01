from multiprocessing import Process
import time

# Función que suma los números del 1 al 70.000.000 e imprime el resultado
def suma_grande():
    total = 0
    for i in range(1, 70000001):
        total += i
    print(f"La suma de 1 a 70.000.000 es: {total}")

def main():
    # Creamos el proceso secundario
    p = Process(target=suma_grande)
    p.start()
    # Esperamos 3 segundos a que termine
    p.join(timeout=3)
    # Si sigue vivo después de 3 segundos, lo terminamos
    if p.is_alive():
        print("El proceso no ha terminado en 3 segundos. Terminando proceso...")
        p.terminate()
        p.join()
    else:
        print("El proceso terminó correctamente.")

    # La suma terminará e imprimirá el resultado solo si el proceso secundario
    # consigue completar la suma antes de que pasen los 3 segundos.
    # Normalmente, sumar hasta 70.000.000 tarda más de 3 segundos,
    # por lo que el proceso suele ser terminado antes de finalizar la suma.

if __name__ == "__main__":
    main()