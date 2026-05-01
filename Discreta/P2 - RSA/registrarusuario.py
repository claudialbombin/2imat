"""
registrarusuario.py

Programa para registrar nuevos usuarios en el sistema de chat cifrado

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP06B
Integrantes:
	- Claudia Maria Lopez Bombin
	- Lucia Lozano Isac

Descripción:
Este programa permite crear nuevos usuarios para el sistema de chat cifrado RSA.
Genera un par de claves RSA (pública y privada) y las almacena en archivos de texto
en la carpeta 'Usuarios', junto con la configuración de padding.

Formato de archivos generados:
- pub.<nombre>.txt: Contiene n (módulo), e (exponente público) y dígitos de padding
- priv.<nombre>.txt: Contiene d (exponente privado)

Ejemplo de uso:
    python registrarusuario.py
"""

import os
import sys
from rsa import generar_claves

def usuario_existe(nombre: str) -> bool:
    """
    Verifica si un usuario ya está registrado.
    
    Args:
        nombre (str): Nombre del usuario a verificar
        
    Returns:
        bool: True si el usuario ya existe, False en caso contrario
    """
    archivo_publico = f"Usuarios/pub.{nombre}.txt"
    archivo_privado = f"Usuarios/priv.{nombre}.txt"
    
    return os.path.exists(archivo_publico) and os.path.exists(archivo_privado)

def listar_usuarios_existentes():
    """
    Lista todos los usuarios ya registrados.
    """
    usuarios = []
    if os.path.exists("Usuarios"):
        for archivo in os.listdir("Usuarios"):
            if archivo.startswith("pub.") and archivo.endswith(".txt"):
                nombre = archivo[4:-4]  # Extraer nombre entre 'pub.' y '.txt'
                usuarios.append(nombre)
    return sorted(usuarios)

def main():
    """
    Función principal del programa de registro de usuarios.
    
    Flujo de ejecución:
    1. Solicita datos de configuración al usuario
    2. Verifica que el usuario no exista
    3. Genera par de claves RSA usando rsa.generar_claves()
    4. Crea la carpeta 'Usuarios' si no existe
    5. Guarda la clave pública en pub.<nombre>.txt
    6. Guarda la clave privada en priv.<nombre>.txt
    7. Confirma el registro exitoso
    
    Manejo de errores:
    - Valida que los inputs sean números enteros
    - Verifica que el usuario no exista previamente
    - Captura errores en generación de claves
    - Maneja errores de escritura de archivos
    """
    print("=== REGISTRO DE NUEVO USUARIO ===")
    
    # SOLICITUD DE DATOS DE CONFIGURACIÓN
    # Nombre del usuario: identificador único para el sistema
    while True:
        nombre = input("Introduce el nombre del usuario: ").strip()
        if not nombre:
            print("Error: El nombre no puede estar vacío.")
            continue
            
        # Verificar si el usuario ya existe
        if usuario_existe(nombre):
            print(f"Error: El usuario '{nombre}' ya está registrado.")
            
            # Mostrar usuarios existentes solo en caso de duplicado
            usuarios_existentes = listar_usuarios_existentes()
            if usuarios_existentes:
                print("Usuarios ya registrados:")
                for usuario in usuarios_existentes:
                    print(f"  - {usuario}")
                print("Por favor, elige un nombre diferente.")
            continue
            
        break  # Nombre válido y único
    
    try:
        # Rango para generación de primos RSA
        # min_primo: Límite inferior para buscar números primos
        min_primo = int(input("Valor mínimo para los primos: "))
        # max_primo: Límite superior (exclusivo) para buscar números primos  
        max_primo = int(input("Valor máximo para los primos: "))
        
        # Validación básica del rango
        if min_primo >= max_primo:
            print("Error: El valor mínimo debe ser menor que el máximo.")
            return
        if min_primo < 1:
            print("Error: El valor mínimo debe ser al menos 1.")
            return
            
        # digitos_padding: Número de dígitos aleatorios añadidos para seguridad
        digitos_padding = int(input("Número de cifras de padding: "))
        if digitos_padding < 0:
            print("Error: El padding no puede ser negativo.")
            return
            
    except ValueError:
        print("Error: Los valores deben ser números enteros.")
        return
    
    # GENERACIÓN DE CLAVES RSA
    print("\nGenerando claves RSA...")
    try:
        # generar_claves() retorna una tupla (n, e, d)
        # n = p * q (producto de dos primos)
        # e = exponente público (coprimo con φ(n))
        # d = exponente privado (inverso modular de e módulo φ(n))
        n, e, d = generar_claves(min_primo, max_primo)
        
        print("Claves generadas correctamente:")
        print(f"n = {n}")      # Módulo público
        print(f"e = {e}")      # Exponente público
        print(f"d = {d}")      # Exponente privado (secreto)
        
    except Exception as ex:
        print(f"Error generando claves: {ex}")
        return
    
    # CREACIÓN DE CARPETA DE USUARIOS
    # La carpeta 'Usuarios' almacena todas las claves públicas y privadas
    if not os.path.exists("Usuarios"):
        os.makedirs("Usuarios")
        print("Carpeta 'Usuarios' creada.")
    
    # GUARDADO DE CLAVE PÚBLICA
    # Formato: tres líneas con n, e y digitos_padding
    try:
        with open(f"Usuarios/pub.{nombre}.txt", "w") as f:
            f.write(f"{n}\n")              # Línea 1: módulo n
            f.write(f"{e}\n")              # Línea 2: exponente público e
            f.write(f"{digitos_padding}\n") # Línea 3: dígitos de padding
        print(f"Clave pública guardada en: Usuarios/pub.{nombre}.txt")
    except Exception as ex:
        print(f"Error guardando clave pública: {ex}")
        return
    
    # GUARDADO DE CLAVE PRIVADA  
    # Formato: una línea con el exponente privado d
    # ADVERTENCIA: En un sistema real esto estaría cifrado
    try:
        with open(f"Usuarios/priv.{nombre}.txt", "w") as f:
            f.write(f"{d}\n")  # Línea única: exponente privado d
        print(f"Clave privada guardada en: Usuarios/priv.{nombre}.txt")
    except Exception as ex:
        print(f"Error guardando clave privada: {ex}")
        return
    
    # CONFIRMACIÓN FINAL
    print("Usuario registrado exitosamente!")
    print(f"\nResumen:")
    print(f"- Nombre: {nombre}")
    print(f"- Rango de primos: [{min_primo}, {max_primo})")
    print(f"- Dígitos de padding: {digitos_padding}")
    print(f"- Archivos creados en carpeta 'Usuarios'")

if __name__ == "__main__":
    main()


# Final del archivo registrarusuario.py