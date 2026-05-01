"""
criptochat.py

Chat encriptado extremo a extremo usando RSA

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP06B
Integrantes:
    - Claudia Maria Lopez Bombin
    - Lucia Lozano Isac

Descripción:
Este programa implementa un chat cifrado que permite comunicación segura entre dos usuarios
utilizando el sistema RSA. Cada usuario cifra mensajes con la clave pública del destinatario
y descifra mensajes recibidos con su propia clave privada.

Funcionalidades:
- Cifrado de mensajes de texto usando RSA con padding
- Descifrado de mensajes cifrados
- Gestión de claves públicas y privadas desde archivos
- Interfaz interactiva para comunicación

Formato de mensajes:
- Texto plano: cadenas de caracteres normales (ej: "hola")
- Texto cifrado: listas de enteros separados por espacios (ej: "512533741 128348154")

Ejemplo de uso:
    python criptochat.py alice bob
"""

import os
import sys
import rsa 

def cargar_clave_publica(nombre: str) -> tuple:
    """
    Carga la clave pública de un usuario desde el archivo correspondiente.
    
    Args:
        nombre (str): Nombre del usuario cuya clave pública se desea cargar
    
    Returns:
        tuple: Tupla con (n, e, digitos_padding) o None si hay error
        - n (int): Módulo RSA
        - e (int): Exponente público  
        - digitos_padding (int): Número de dígitos de padding configurados
    
    Raises:
        FileNotFoundError: Si no existe el archivo de clave pública
        ValueError: Si el formato del archivo es incorrecto
    """
    try:
        ruta_archivo = f"Usuarios/pub.{nombre}.txt"
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"No se encontró el archivo de clave pública: {ruta_archivo}")
        
        with open(ruta_archivo, 'r') as f:
            lineas = f.readlines()
            
        if len(lineas) < 3:
            raise ValueError(f"Formato incorrecto en archivo de clave pública. Se esperaban 3 líneas, se encontraron {len(lineas)}")
        
        n = int(lineas[0].strip())
        e = int(lineas[1].strip())
        digitos_padding = int(lineas[2].strip())
        
        return n, e, digitos_padding
        
    except FileNotFoundError:
        raise
    except ValueError as e:
        raise ValueError(f"Error en formato del archivo de clave pública: {e}")
    except Exception as e:
        raise Exception(f"Error inesperado al cargar clave pública: {e}")

def cargar_clave_privada(nombre: str) -> tuple:
    """
    Carga la clave privada de un usuario desde el archivo correspondiente.
    
    Args:
        nombre (str): Nombre del usuario cuya clave privada se desea cargar
    
    Returns:
        tuple: Tupla con (n, d, digitos_padding) o None si hay error
        - n (int): Módulo RSA (desde clave pública)
        - d (int): Exponente privado
        - digitos_padding (int): Número de dígitos de padding configurados
    
    Raises:
        FileNotFoundError: Si no existe algún archivo necesario
        ValueError: Si el formato de algún archivo es incorrecto
    """
    try:
        # Primero cargamos la clave pública para obtener n y digitos_padding
        n, e, digitos_padding = cargar_clave_publica(nombre)
        
        # Luego cargamos la clave privada
        ruta_archivo = f"Usuarios/priv.{nombre}.txt"
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"No se encontró el archivo de clave privada: {ruta_archivo}")
        
        with open(ruta_archivo, 'r') as f:
            lineas = f.readlines()
            
        if len(lineas) < 1:
            raise ValueError("Formato incorrecto en archivo de clave privada. Se esperaba al menos 1 línea")
        
        d = int(lineas[0].strip())
        
        return n, d, digitos_padding
        
    except FileNotFoundError:
        raise
    except ValueError as e:
        raise ValueError(f"Error en formato del archivo de clave privada: {e}")
    except Exception as e:
        raise Exception(f"Error inesperado al cargar clave privada: {e}")

def mostrar_menu() -> str:
    """
    Muestra el menú principal y obtiene la opción del usuario.
    
    Returns:
        str: Opción seleccionada ('C' para cifrar, 'D' para descifrar, 'S' para salir)
    """
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("C - Cifrar mensaje para destinatario")
        print("D - Descifrar mensaje recibido")
        print("S - Salir")
        
        opcion = input("Selecciona una opción (C/D/S): ").strip().upper()
        
        if opcion in ['C', 'D', 'S']:
            return opcion
        else:
            print("Opción no válida. Por favor, selecciona C, D o S.")

def realizar_cifrado(usuario_actual: str, clave_publica_destino: tuple) -> None:
    """
    Realiza el proceso de cifrado de un mensaje para el destinatario.
    
    Args:
        usuario_actual (str): Nombre del usuario que envía el mensaje
        clave_publica_destino (tuple): Tupla con (n, e, digitos_padding) del destinatario
    
    Flujo:
        1. Solicita el mensaje en texto plano al usuario
        2. Cifra el mensaje usando la clave pública del destinatario
        3. Muestra el resultado cifrado en formato de lista de enteros
    """
    try:
        n, e, digitos_padding = clave_publica_destino
        
        print(f"\n--- CIFRADO PARA DESTINATARIO ---")
        print(f"Usando clave pública: n={n}, e={e}")
        print(f"Padding configurado: {digitos_padding} dígitos")
        
        # Solicitar mensaje
        mensaje = input("Introduce el mensaje a cifrar: ").strip()
        
        if not mensaje:
            print("Error: El mensaje no puede estar vacío.")
            return
        
        # Cifrar el mensaje
        mensaje_cifrado = rsa.cifrar_cadena_rsa(mensaje, n, e, digitos_padding)
        
        # Mostrar resultado
        print(f"\n✓ Mensaje cifrado correctamente:")
        print("Texto cifrado:", " ".join(str(x) for x in mensaje_cifrado))
        print(f"Longitud: {len(mensaje_cifrado)} bloques")
        
    except Exception as e:
        print(f"Error durante el cifrado: {e}")

def realizar_descifrado(usuario_actual: str, clave_privada_actual: tuple) -> None:
    """
    Realiza el proceso de descifrado de un mensaje recibido.
    
    Args:
        usuario_actual (str): Nombre del usuario que descifra el mensaje
        clave_privada_actual (tuple): Tupla con (n, d, digitos_padding) del usuario actual
    
    Flujo:
        1. Solicita el mensaje cifrado como lista de enteros
        2. Descifra el mensaje usando la clave privada del usuario actual
        3. Muestra el texto plano resultante
    """
    try:
        n, d, digitos_padding = clave_privada_actual
        
        print(f"\n--- DESCIFRADO PARA {usuario_actual.upper()} ---")
        print(f"Usando clave privada con módulo n={n}")
        print(f"Padding configurado: {digitos_padding} dígitos")
        
        # Solicitar mensaje cifrado
        entrada = input("Introduce el mensaje cifrado (enteros separados por espacios): ").strip()
        
        if not entrada:
            print("Error: El mensaje cifrado no puede estar vacío.")
            return
        
        # Convertir entrada a lista de enteros
        try:
            mensaje_cifrado = [int(x.strip()) for x in entrada.split()]
        except ValueError:
            print("Error: Formato incorrecto. Introduce solo enteros separados por espacios.")
            return
        
        # Descifrar el mensaje
        mensaje_descifrado = rsa.descifrar_cadena_rsa(mensaje_cifrado, n, d, digitos_padding)
        
        # Mostrar resultado
        print(f"\n✓ Mensaje descifrado correctamente:")
        print("Texto plano:", mensaje_descifrado)
        
    except Exception as e:
        print(f"Error durante el descifrado: {e}")

def main():
    """
    Función principal del programa de chat cifrado.
    
    Flujo de ejecución:
    1. Verifica los argumentos de línea de comandos
    2. Carga las claves de ambos usuarios
    3. Muestra el menú interactivo
    4. Ejecuta las operaciones seleccionadas hasta que el usuario sale
    
    Args de línea de comandos:
        usuario1: Usuario local (posee clave privada para descifrar)
        usuario2: Usuario remoto (solo se necesita clave pública para cifrar)
    
    Ejemplo:
        python criptochat.py alice bob
    """
    # Verificar argumentos
    if len(sys.argv) != 3:
        print("Uso: python criptochat.py <usuario_local> <usuario_remoto>")
        print("Ejemplo: python criptochat.py alice bob")
        sys.exit(1)
    
    usuario_local = sys.argv[1]
    usuario_remoto = sys.argv[2]
    
    print(f"=== CHAT CIFRADO RSA ===")
    print(f"Usuario local: {usuario_local} (descifra mensajes)")
    print(f"Usuario remoto: {usuario_remoto} (cifra mensajes para él)")
    print("=" * 30)
    
    try:
        # Cargar claves del usuario local (clave privada para descifrar)
        print(f"Cargando clave privada de {usuario_local}...")
        clave_privada_local = cargar_clave_privada(usuario_local)
        print("✓ Clave privada cargada correctamente")
        
        # Cargar clave pública del usuario remoto (para cifrar)
        print(f"Cargando clave pública de {usuario_remoto}...")
        clave_publica_remoto = cargar_clave_publica(usuario_remoto)
        print("✓ Clave pública cargada correctamente")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Asegúrate de que:")
        print(f"1. El usuario '{usuario_local}' esté registrado (exista carpeta Usuarios/pub.{usuario_local}.txt y priv.{usuario_local}.txt)")
        print(f"2. El usuario '{usuario_remoto}' esté registrado (exista carpeta Usuarios/pub.{usuario_remoto}.txt)")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado al cargar claves: {e}")
        sys.exit(1)
    
    # Bucle principal del programa
    while True:
        try:
            opcion = mostrar_menu()
            
            if opcion == 'C':
                realizar_cifrado(usuario_local, clave_publica_remoto)
            elif opcion == 'D':
                realizar_descifrado(usuario_local, clave_privada_local)
            elif opcion == 'S':
                print("\n¡Hasta pronto!")
                break
                
        except KeyboardInterrupt:
            print("\n\nInterrupción detectada. Saliendo...")
            break
        except Exception as e:
            print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()


# Final del archivo criptochat.py