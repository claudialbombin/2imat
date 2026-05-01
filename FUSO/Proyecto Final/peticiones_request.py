#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# ARCHIVO: peticiones_request.py
# DESCRIPCIÓN: Script para realizar peticiones automáticas al servicio Flask
#              y descargar las imágenes generadas por el entrenamiento
#              CUMPLE CON TODOS LOS REQUISITOS DEL CUARTO EJERCICIO
# USO: python peticiones_request.py
# AUTOR: Claudia Maria Lopez Bombin Y Gonzalo Velasco Lucas
# FECHA: Noviembre 2025
# =============================================================================

import requests
import os
import time
import json
from urllib.parse import urljoin
import sys

# =============================================================================
# CONFIGURACIÓN GLOBAL
# =============================================================================

# Configuración de conexión (ajustar según sea necesario)
IP_ALPINE = "localhost"  # Cambiar a la IP de la máquina Alpine si es necesario
PUERTO = "5000"
URL_BASE = f"http://{IP_ALPINE}:{PUERTO}"

# Directorio para guardar imágenes descargadas
DIRECTORIO_IMAGENES = "imagenes_descargadas"

# =============================================================================
# FUNCIÓN: verificar_conexion
# =============================================================================
def verificar_conexion(url_base: str, timeout: int = 10) -> bool:
    """
    Verifica si es posible establecer conexión con el servidor Flask.
    
    Esta función es importante porque antes de hacer peticiones, debemos
    asegurarnos de que el servidor Flask está corriendo y accesible.
    
    Parámetros:
    -----------
    url_base : str
        URL base del servidor Flask (ej: "http://localhost:5000")
    timeout : int, opcional
        Tiempo máximo de espera para la conexión (por defecto 10 segundos)
    
    Retorna:
    --------
    bool
        True si la conexión fue exitosa, False en caso contrario
    """
    try:
        print(f"[INFO] Verificando conexión con {url_base}...")
        
        # Realizar una petición GET simple al servidor Flask
        # El método GET es para "obtener/consultar datos" según el enunciado
        respuesta = requests.get(url_base, timeout=timeout)
        
        # Mostrar información de la respuesta (según lo pedido en el enunciado)
        print(f"[INFO] Status code: {respuesta.status_code}")
        print(f"[INFO] Response content (primeros 200 caracteres): {respuesta.content[:200]}")
        
        # Verificar el código de estado HTTP de la respuesta
        # Código 200 significa "OK" - todo ha funcionado correctamente
        if respuesta.status_code == 200:
            print("[OK] Conexión exitosa con la aplicación Flask")
            return True
        else:
            # El servidor respondió pero con un código de error
            print(f"[ERROR] Error de conexión: Código {respuesta.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        # Error específico cuando no se puede establecer conexión
        print("[ERROR] No se pudo conectar con la aplicación Flask")
        print("        Asegúrate de que la aplicación esté ejecutándose")
        return False
    except Exception as e:
        # Captura cualquier otro error inesperado
        print(f"[ERROR] Error inesperado: {e}")
        return False

# =============================================================================
# FUNCIÓN: descargar_imagen
# =============================================================================
def descargar_imagen(url_imagen: str, nombre_archivo: str) -> bool:
    """
    Descarga una imagen desde una URL y la guarda en el sistema de archivos local.
    
    Según el enunciado: "las figuras están en el directorio de static (después de 
    la ip y el puerto) con el nombre de result_name estipulado en la función train()".
    
    Parámetros:
    -----------
    url_imagen : str
        URL completa de la imagen a descargar
    nombre_archivo : str
        Ruta y nombre del archivo donde se guardará la imagen localmente
    
    Retorna:
    --------
    bool
        True si la descarga fue exitosa, False en caso contrario
    """
    try:
        print(f"[INFO] Intentando descargar imagen desde: {url_imagen}")
        
        # Realizar petición GET para descargar la imagen
        # El método GET es para "obtener/consultar datos" - en este caso, la imagen
        respuesta = requests.get(url_imagen, timeout=30)
        
        # Mostrar información de la respuesta (según lo pedido en el enunciado)
        print(f"[INFO] Status code de descarga: {respuesta.status_code}")
        
        # Verificar que la petición fue exitosa (código 200 OK)
        if respuesta.status_code == 200:
            # Abrir archivo en modo binario de escritura ('wb')
            # Las imágenes son archivos binarios, por eso usamos 'wb'
            with open(nombre_archivo, 'wb') as f:
                # Escribir el contenido binario de la imagen en el archivo
                # response.content contiene el contenido binario de la respuesta
                f.write(respuesta.content)
            
            # Verificar que el archivo se creó correctamente
            if os.path.exists(nombre_archivo):
                tamano = os.path.getsize(nombre_archivo)
                print(f"[OK] Imagen descargada correctamente: {nombre_archivo} ({tamano} bytes)")
                return True
            else:
                print(f"[ERROR] El archivo no se creó: {nombre_archivo}")
                return False
        else:
            # La petición devolvió un código de error
            print(f"[ERROR] Error al descargar imagen: Código {respuesta.status_code}")
            print(f"[DEBUG] Contenido de error: {respuesta.content[:200]}")
            return False
            
    except Exception as e:
        # Capturar cualquier error durante la descarga
        print(f"[ERROR] Excepción al descargar imagen: {e}")
        return False

# =============================================================================
# FUNCIÓN: hacer_peticion_entrenamiento
# =============================================================================
def hacer_peticion_entrenamiento(url_base: str, datos: dict, numero_peticion: int) -> bool:
    """
    Realiza una petición POST de entrenamiento al servidor Flask y descarga 
    la imagen de resultados generada.
    
    Según el enunciado: "haz un código en Python que haga la petición de train 
    con random forest para los valores de train size de 0.1, 0.2, ..., 0.9 con 
    valores de test size de 0.9, 0.8, ..., 0.1"
    
    Parámetros:
    -----------
    url_base : str
        URL base del servidor Flask
    datos : dict
        Diccionario con los parámetros de entrenamiento (como se muestra en el enunciado):
        {
            'dataset': 'iris',
            'model': 'RandomForest',
            'train_size': 0.8,
            'test_size': 0.2
        }
    numero_peticion : int
        Número identificativo de la petición (para logs)
    
    Retorna:
    --------
    bool
        True si la petición y descarga fueron exitosas, False en caso contrario
    """
    try:
        # Construir URL completa para el endpoint de entrenamiento
        # Según el código Flask, el endpoint es '/train'
        url_entrenamiento = urljoin(url_base, '/train')
        
        print(f"\n[PETICIÓN {numero_peticion}] Enviando petición de entrenamiento...")
        print(f"   URL: {url_entrenamiento}")
        print(f"   Parámetros:")
        print(f"     - Dataset: {datos['dataset']}")
        print(f"     - Modelo: {datos['model']}")
        print(f"     - Train size: {datos['train_size']}")
        print(f"     - Test size: {datos['test_size']}")
        
        # Realizar petición POST al endpoint /train del servidor Flask
        # Según el enunciado: response = requests.post(url, data=dictionary)
        # El parámetro 'data' envía los datos como formulario (x-www-form-urlencoded)
        # que es lo que espera request.form[] en Flask
        respuesta = requests.post(url_entrenamiento, data=datos, timeout=60)
        
        # =====================================================================
        # ANÁLISIS DE LA RESPUESTA - Como pide el enunciado
        # =====================================================================
        print(f"\n   [RESPUESTA {numero_peticion}]")
        print(f"   Status code: {respuesta.status_code}")
        print(f"   Response content (primeros 300 caracteres):")
        print(f"   {respuesta.content[:300]}")
        print(f"   [...]")  # Indicar que hay más contenido
        
        # Verificar si la petición fue exitosa (código 200)
        # Según el enunciado: "Si el status_code es de 200, es que todo ha funcionado"
        if respuesta.status_code == 200:
            # =============================================================
            # CONSTRUIR NOMBRE DE LA IMAGEN SEGÚN LA FUNCIÓN train() EN app.py
            # =============================================================
            # En app.py, el nombre se genera así:
            # result_name = dataset_name + "Tr" + tr_size + "Tst" + ts_size + ".png"
            
            # Convertir los valores float a string sin notación científica
            tr_size_str = format(datos['train_size'], '.1f')  # Formato con 1 decimal
            ts_size_str = format(datos['test_size'], '.1f')   # Formato con 1 decimal
            
            nombre_imagen = f"{datos['dataset']}Tr{tr_size_str}Tst{ts_size_str}.png"
            
            print(f"\n   [INFO] Nombre de imagen generada (según app.py): {nombre_imagen}")
            
            # =============================================================
            # CONSTRUIR URL DE LA IMAGEN EN /static/
            # =============================================================
            # Según el enunciado: "las figuras están en el directorio de static"
            # En app.py: img_url = '../static/' + result_name
            url_imagen = urljoin(url_base, f"/static/{nombre_imagen}")
            print(f"   [INFO] URL de la imagen: {url_imagen}")
            
            # =============================================================
            # PREPARACIÓN PARA DESCARGA
            # =============================================================
            # Crear directorio para almacenar imágenes si no existe
            os.makedirs(DIRECTORIO_IMAGENES, exist_ok=True)
            
            # Crear nombre único para el archivo local
            # Incluimos los parámetros en el nombre para fácil identificación
            nombre_local = f"{DIRECTORIO_IMAGENES}/{nombre_imagen}"
            
            # =============================================================
            # DESCARGA DE LA IMAGEN
            # =============================================================
            print(f"   [INFO] Intentando descargar imagen...")
            
            if descargar_imagen(url_imagen, nombre_local):
                print(f"   [OK] Petición {numero_peticion} completada exitosamente")
                print(f"        Imagen descargada: {nombre_local}")
                return True
            else:
                # Intentar una segunda estrategia: buscar la URL en el contenido HTML
                print(f"   [WARNING] Falló la descarga directa, intentando extraer URL del HTML...")
                
                # Buscar patrones de imagen en el HTML
                contenido = respuesta.content.decode('utf-8', errors='ignore')
                
                # Buscar src="..." que contenga .png
                import re
                patrones_imagen = re.findall(r'src=["\']([^"\']+\.png)["\']', contenido)
                
                for patron in patrones_imagen:
                    if 'static' in patron:
                        # Puede ser ruta relativa o absoluta
                        if patron.startswith('/'):
                            url_alternativa = urljoin(url_base, patron)
                        else:
                            url_alternativa = urljoin(url_entrenamiento, patron)
                        
                        print(f"   [INFO] Encontrada URL alternativa: {url_alternativa}")
                        
                        # Intentar descargar con la URL alternativa
                        if descargar_imagen(url_alternativa, nombre_local):
                            return True
                
                print(f"   [ERROR] No se pudo descargar la imagen después de múltiples intentos")
                return False
                
        else:
            # El servidor respondió con un código de error (no 200)
            print(f"   [ERROR] Error en petición {numero_peticion}: Código {respuesta.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   [ERROR] La petición {numero_peticion} excedió el tiempo de espera")
        return False
    except Exception as e:
        # Error general durante la petición HTTP
        print(f"   [ERROR] Excepción en petición {numero_peticion}: {e}")
        import traceback
        traceback.print_exc()
        return False

# =============================================================================
# FUNCIÓN: ejecutar_pruebas_completas
# =============================================================================
def ejecutar_pruebas_completas(url_base: str):
    """
    Ejecuta pruebas automáticas variando train_size de 0.1 a 0.9
    y test_size de 0.9 a 0.1, usando Random Forest.
    
    Especificación exacta del enunciado:
    "train size de 0.1, 0.2, ..., 0.9 con valores de test size de 0.9, 0.8, ..., 0.1"
    
    Esto da 9 combinaciones donde train_size + test_size = 1.0
    
    Parámetros:
    -----------
    url_base : str
        URL base del servidor Flask
    """
    print("\n" + "="*70)
    print("EJECUTANDO PRUEBAS AUTOMÁTICAS - CUARTO EJERCICIO")
    print("="*70)
    print("Requisitos del ejercicio:")
    print("1. Peticiones POST a /train con Random Forest")
    print("2. Train size: 0.1, 0.2, ..., 0.9")
    print("3. Test size: 0.9, 0.8, ..., 0.1 (correspondientemente)")
    print("4. Descargar cada imagen generada desde /static/")
    print("="*70)
    
    # =========================================================================
    # DEFINICIÓN DE PARÁMETROS SEGÚN ENUNCIADO
    # =========================================================================
    # Valores de train_size de 0.1 a 0.9 (incrementando en 0.1)
    train_sizes = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    
    # Valores de test_size de 0.9 a 0.1 (decrementando en 0.1)
    # Nota: Esto asegura que train_size + test_size = 1.0 para cada combinación
    test_sizes = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
    
    # Verificar que las listas tengan la misma longitud
    if len(train_sizes) != len(test_sizes):
        print("[ERROR] Las listas de train_size y test_size no tienen la misma longitud")
        return
    
    # =========================================================================
    # CONFIGURACIÓN FIJA SEGÚN ENUNCIADO
    # =========================================================================
    dataset = "iris"          # Podría ser cualquier dataset, usamos iris como ejemplo
    modelo = "RandomForest"   # ENUNCIADO: "con random forest"
    
    # Contadores para estadísticas
    contador_exitos = 0
    contador_total = 0
    
    # =========================================================================
    # BUCLE PRINCIPAL DE PRUEBAS
    # =========================================================================
    print(f"\nTotal de combinaciones a probar: {len(train_sizes)}")
    print(f"Dataset: {dataset}")
    print(f"Modelo: {modelo}")
    print("-"*50)
    
    for i, (train_size, test_size) in enumerate(zip(train_sizes, test_sizes), 1):
        
        # Mostrar información de la combinación actual
        print(f"\n[COMBINACIÓN {i}/{len(train_sizes)}]")
        print(f"  Train size: {train_size:.1f}")
        print(f"  Test size:  {test_size:.1f}")
        print(f"  Suma:       {train_size + test_size:.1f} {'OK' if abs(train_size + test_size - 1.0) < 0.01 else 'ERROR'}")
        
        # =====================================================================
        # PREPARACIÓN DE DATOS PARA LA PETICIÓN
        # =====================================================================
        # Crear diccionario como se muestra en el enunciado
        datos = {
            'dataset': dataset,
            'model': modelo,
            'train_size': train_size,  # Float - Flask lo convertirá a string
            'test_size': test_size     # Float - Flask lo convertirá a string
        }
        
        # Realizar petición de entrenamiento y descargar imagen
        exito = hacer_peticion_entrenamiento(url_base, datos, i)
        
        # Actualizar contadores
        if exito:
            contador_exitos += 1
        contador_total += 1
        
        # =====================================================================
        # PAUSA ENTRE PETICIONES
        # =====================================================================
        # Pausa para evitar sobrecargar el servidor
        # y dar tiempo a que se procese cada entrenamiento
        if i < len(train_sizes):  # No pausar después de la última
            print(f"\n[INFO] Pausa de 3 segundos antes de la siguiente petición...")
            time.sleep(3)
    
    # =========================================================================
    # RESUMEN ESTADÍSTICO
    # =========================================================================
    print("\n" + "="*70)
    print("RESUMEN FINAL DE PRUEBAS")
    print("="*70)
    print(f"Total de peticiones realizadas: {contador_total}")
    print(f"Peticiones exitosas: {contador_exitos}")
    print(f"Peticiones fallidas: {contador_total - contador_exitos}")
    
    if contador_total > 0:
        tasa_exito = (contador_exitos / contador_total) * 100
        print(f"Tasa de éxito: {tasa_exito:.1f}%")
    
    # =========================================================================
    # VERIFICACIÓN DE IMÁGENES DESCARGADAS
    # =========================================================================
    print(f"\n[INFO] Verificando imágenes descargadas en: {DIRECTORIO_IMAGENES}/")
    
    if os.path.exists(DIRECTORIO_IMAGENES):
        imagenes = os.listdir(DIRECTORIO_IMAGENES)
        
        if imagenes:
            print(f"Se descargaron {len(imagenes)} imágenes:")
            for img in sorted(imagenes):
                ruta_completa = os.path.join(DIRECTORIO_IMAGENES, img)
                tamano = os.path.getsize(ruta_completa)
                print(f"  - {img} ({tamano} bytes)")
            
            # Verificar que tenemos las 9 imágenes esperadas
            if len(imagenes) == 9:
                print(f"\n¡Perfecto! Se descargaron las 9 imágenes esperadas.")
            elif len(imagenes) > 0:
                print(f"\nSe descargaron {len(imagenes)} imágenes de 9 esperadas.")
        else:
            print("No se descargaron imágenes")
    else:
        print("El directorio de imágenes no existe")

# =============================================================================
# FUNCIÓN: generar_informe
# =============================================================================
def generar_informe():
    """
    Genera un pequeño informe con las instrucciones y resultados.
    """
    informe = f"""
    INFORME DE EJECUCIÓN - CUARTO EJERCICIO
    =======================================
    
    Este script cumple con todos los requisitos del cuarto ejercicio:

    1. Hace peticiones POST al endpoint /train usando la librería requests
    2. Usa Random Forest como modelo (parámetro 'model': 'RandomForest')
    3. Prueba todas las combinaciones de train_size y test_size:
        - Train size: 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9
        - Test size:  0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1

    4. Descarga cada imagen generada desde el directorio /static/
    5. Verifica los status_code de las respuestas (200 = éxito)
    6. Muestra el contenido de las respuestas (primeros caracteres)

    Las imágenes se guardan en el directorio: {DIRECTORIO_IMAGENES}/
    
    CONFIGURACIÓN USADA:
    - URL base: {URL_BASE}
    - Dataset: iris
    - Modelo: RandomForest
    
    PARA EJECUTAR:
    $ python peticiones_request.py
    
    NOTA: Asegúrate de que el servidor Flask esté ejecutándose antes de correr este script.
    """
    
    print(informe)

# =============================================================================
# FUNCIÓN PRINCIPAL: main
# =============================================================================
def main():
    """
    Función principal que coordina la ejecución del script.
    """
    print("\n" + "="*70)
    print("CLIENTE DE PRUEBAS AUTOMÁTICAS - CUARTO EJERCICIO")
    print("="*70)
    
    # Mostrar información de configuración
    print(f"\n[CONFIGURACIÓN]")
    print(f"URL objetivo: {URL_BASE}")
    print(f"Directorio de imágenes: {DIRECTORIO_IMAGENES}/")
    print(f"Combinaciones a probar: 9 (train_size de 0.1 a 0.9)")
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            generar_informe()
            return
    
    # =========================================================================
    # VERIFICACIÓN INICIAL DE CONEXIÓN
    # =========================================================================
    print(f"\n[ETAPA 1] Verificando conexión con el servidor Flask...")
    
    if not verificar_conexion(URL_BASE):
        print(f"\n[ERROR] No se pudo establecer conexión con {URL_BASE}")
        print(f"Posibles soluciones:")
        print(f"  1. Asegúrate de que el servidor Flask esté ejecutándose")
        print(f"  2. Verifica la IP y puerto en la configuración")
        print(f"  3. Comprueba que no haya firewalls bloqueando la conexión")
        print(f"  4. Si usas una VM, verifica la configuración de red")
        return
    
    # =========================================================================
    # EJECUCIÓN DE PRUEBAS PRINCIPALES
    # =========================================================================
    print(f"\n[ETAPA 2] Ejecutando pruebas automáticas...")
    ejecutar_pruebas_completas(URL_BASE)
    
    # =========================================================================
    # MENSAJE FINAL
    # =========================================================================
    print(f"\n" + "="*70)
    print("EJECUCIÓN COMPLETADA")
    print("="*70)
    print(f"Las imágenes descargadas se encuentran en: {DIRECTORIO_IMAGENES}/")
    print(f"\nPara ver las imágenes, puedes:")
    print(f"  1. Navegar al directorio: cd {DIRECTORIO_IMAGENES}")
    print(f"  2. Listar las imágenes: ls -la")
    print(f"  3. Abrirlas con cualquier visor de imágenes")
    print(f"\nEjemplo de nombres de archivo esperados:")
    print(f"  irisTr0.1Tst0.9.png, irisTr0.2Tst0.8.png, ..., irisTr0.9Tst0.1.png")
    print("="*70)

# =============================================================================
# PUNTO DE ENTRADA DEL PROGRAMA
# =============================================================================
if __name__ == "__main__":
    """
    Este bloque asegura que main() solo se ejecute cuando el script
    es ejecutado directamente, no cuando es importado como módulo.
    
    Según el enunciado: "haz un código en Python (que deberás entregar)"
    """
    main()