"""
imatlab.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP06B
Integrantes:
	- Claudia Maria Lopez Bombin
	- Lucia Lozano Isac

Descripción:
Sistema interactivo IMAT-LAB de resolución de ecuaciones en aritmética modular.

Interfaz de acceso interactivo o por lotes a la librería modular.py. Si este script se ejecuta sin parámetros,
lanzará la interfaz de usuario para el modo interactivo.
"""

import sys
from typing import TextIO
import modular


def run_commands(fin: TextIO, fout: TextIO):
    """ 
    Recibe un manejador fin de un fichero de texto ya abierto para lectura y otro de un fichero de salida
    ya abierto para escritura y ejecuta línea por línea los comandos proporcionados por fin, escribiendo los resultados en fout.
    """
    for line in fin:
        line = line.strip()
        if not line:
            continue
        try:
            resultado = execute_command(line)
            fout.write(resultado + "\n")
        except modular.IncompatibleEquationError:
            fout.write("NE\n")
        except ZeroDivisionError:
            fout.write("NE\n")
        except Exception:
            fout.write("NOP\n")


def execute_command(comando: str) -> str:
    """
    Interpreta un comando en formato string y devuelve el resultado como string.
    """
    comandos = {
        # Funcion 1
        "primo": modular.es_primo,
        # Funcion 2
        "primos": modular.lista_primos,
        # Funcion 3
        "factorizar": modular.factorizar,
        # Funcion 4.1
        "mcd": modular.mcd,
        # Funcion 4.2
        "bezout": modular.bezout,
        # Funcion 5.1
        "mcdn": modular.mcd_n,
        # Funcion 5.2
        "bezoutn": modular.bezout_n,
        # Funcion 6
        "coprimos": modular.coprimos,
        # Funcion 7
        "pow": modular.potencia_mod_p,
        # Funcion 8
        "inv": modular.inversa_mod_p,
        # Funcion 9
        "euler": modular.euler,
        # Funcion 10
        "legendre": modular.legendre,
        # Funcion 11
        "resolverSistema": modular.resolver_sistema_congruencias,
        # Funcion 13
        "raiz": modular.raiz_mod_p,
        # Funcion 14
        "ecCuadratica": modular.ecuacion_cuadratica,
    }

    if "(" not in comando or not comando.endswith(")"):
        return "NOP"

    nombre, args = comando.split("(", 1)
    nombre = nombre.strip()
    args = args[:-1]  # quitamos el paréntesis final

    if nombre not in comandos:
        return "NOP"

    argumentos = parse_args(args, nombre)

    # Casos especiales:
    # 1. Si es mcd y tiene 1 argumento, usar mcd_n
    if nombre == "mcd":
        if len(argumentos) == 1:
            funcion = modular.mcd_n
            argumentos = [argumentos]  # mcd_n espera una lista
        elif len(argumentos) > 2:
            funcion = modular.mcd_n
            argumentos = [argumentos]  # mcd_n espera una lista
        else:
            funcion = modular.mcd  # caso normal de 2 argumentos
    else:
        funcion = comandos[nombre]
    # 2. Raiz - devolver ambas raíces
    if nombre == "raiz" and len(argumentos) == 2:
        try:
            n, p = argumentos
            raiz1 = modular.raiz_mod_p(n, p)
            raiz2 = (-raiz1) % p  # La otra raíz es el negativo módulo p

            if raiz1 == raiz2:
                return str(raiz1)  # Raíz doble
            else:
                # Ordenar para consistencia
                raices_ordenadas = sorted([raiz1, raiz2])
                return f"{raices_ordenadas[0]}, {raices_ordenadas[1]}"
        except modular.IncompatibleEquationError:
            raise
        except Exception:
            return "NOP"

    try:
        resultado = funcion(*argumentos)
        output = format_output(nombre, resultado)
        return output
    except modular.IncompatibleEquationError:
        raise  # Re-lanzar para que run_commands lo capture como "NE"
    except ZeroDivisionError:
        raise  # Re-lanzar para que run_commands lo capture como "NE"
    except Exception:
        return "NOP"


def parse_args(args: str, comando: str = ""):
    """
    Convierte los argumentos de texto en enteros o listas de enteros.
    """

    if not args:
        return []

    # Limpiar espacios
    args = args.strip()

    # Caso especial: argumento único "0"
    if args == "0":
        return [0]

    # PRIMERO intentar parsear como número simple
    try:
        # Si no hay comas ni corchetes, es un número simple
        if "," not in args and "[" not in args and "]" not in args:
            resultado = [int(args)]
            return resultado
    except ValueError:
        pass

    if "[" in args:  # caso con listas
        partes = args.split("],")
        listas = []
        for p in partes:
            p = p.strip(" []")
            if not p:
                listas.append([])
                continue
            numeros = [int(x.strip())
                       for x in p.replace(";", ",").split(",") if x.strip()]
            listas.append(numeros)

        if comando in ["resolverSistema", "resolverSistema12"]:
            if listas and all(len(lst) == 3 for lst in listas):
                alist = [lst[0] for lst in listas]
                blist = [lst[1] for lst in listas]
                plist = [lst[2] for lst in listas]
                return [alist, blist, plist]

        return listas

    # **CORRECCIÓN: Manejar múltiples argumentos separados por comas**
    # Caso general: múltiples argumentos simples separados por comas
    if "," in args and "[" not in args and "]" not in args:
        try:
            return [int(x.strip()) for x in args.split(",") if x.strip()]
        except ValueError:
            return []

    # Si llegamos aquí, intentamos parsear como único número
    try:
        return [int(args)]
    except ValueError:
        return []


def format_output(nombre: str, resultado) -> str:
    """
    Da formato al resultado según el comando ejecutado.
    """
    if nombre == "primo":
        return "Sí" if resultado else "No"
    if nombre == "primos":
        return ", ".join(map(str, resultado)) if resultado else "NE"
    if nombre == "factorizar":
        if resultado == {}:
            return "0"
        return ", ".join(f"{p}: {e}" for p, e in resultado.items())
    if nombre == "coprimos":
        return "Sí" if resultado else "No"
    if nombre == "resolverSistema":
        r, m = resultado
        return f"{r} (mod {m})"
    # CORRECCIÓN PARA ecuacion_cuadratica
    if nombre == "ecCuadratica":
        x1, x2 = resultado
        if x1 == x2:
            return str(x1)  # Raíz doble: solo un número
        else:
            return f"{x1}, {x2}"  # Dos raíces distintas
    return str(resultado)


def interactive_mode():
    """
    Modo interactivo: permite escribir comandos en la terminal.
    """
    print("IMAT-LAB (modo interactivo). Escribe un comando, seguido de el/los numeros a usar entre parentesis (ej. primo (3)), o pulsa Enter para salir.")
    while True:
        linea = input("> ").strip()
        if not linea:
            break
        try:
            resultado = execute_command(linea)
            # Imprimir resultado
            print(resultado)
        except Exception:
            print("NOP")


if __name__ == "__main__":
    # Modo batch si se pasan dos ficheros como argumentos
    if len(sys.argv) == 3:
        with open(sys.argv[1], "r", encoding="utf-8") as fin, \
                open(sys.argv[2], "w", encoding="utf-8") as fout:
            run_commands(fin, fout)
    else:
        # Modo interactivo si no hay argumentos
        interactive_mode()

# Fin del archivo imatlab.py
