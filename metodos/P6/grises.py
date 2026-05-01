import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import lu
from PIL import Image
import requests
from io import BytesIO

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def cargar_imagen_grises_como_cuadrada(ruta_o_url, tamaño_cuadrado=None):
    """
    Carga una imagen y la convierte a escala de grises y cuadrada.
    
    Parámetros:
    -----------
    ruta_o_url : str
        Ruta local o URL de la imagen
    tamaño_cuadrado : int, opcional
        Si se proporciona, redimensiona a (tamaño_cuadrado, tamaño_cuadrado).
        Si no se proporciona, toma el menor lado y recorta al centro para hacerla cuadrada.
    
    Retorna:
    --------
    matriz : numpy.ndarray (2D) de floats en [0,1]
    tamaño : int (n)
    """
    # Cargar imagen
    if ruta_o_url.startswith('http://') or ruta_o_url.startswith('https://'):
        respuesta = requests.get(ruta_o_url)
        img = Image.open(BytesIO(respuesta.content))
    else:
        img = Image.open(ruta_o_url)
    
    # Convertir a escala de grises
    img_gris = img.convert('L')
    
    # Hacerla cuadrada
    if tamaño_cuadrado is not None:
        # Redimensionar directamente al tamaño deseado
        img_cuadrada = img_gris.resize((tamaño_cuadrado, tamaño_cuadrado), Image.Resampling.LANCZOS)
        n = tamaño_cuadrado
    else:
        # Hacer cuadrada recortando al centro
        ancho, alto = img_gris.size
        lado = min(ancho, alto)
        izquierda = (ancho - lado) // 2
        superior = (alto - lado) // 2
        img_cuadrada = img_gris.crop((izquierda, superior, izquierda + lado, superior + lado))
        n = lado
    
    # Convertir a numpy y normalizar
    matriz = np.array(img_cuadrada, dtype=np.float64) / 255.0
    
    print(f"Imagen cargada como cuadrada de tamaño {n}x{n}")
    return matriz, n


def cifrar_imagen(A_c, A_s, alpha):
    """
    Cifra A_s dentro de A_c usando factorización LU.
    A_c y A_s deben ser matrices cuadradas del mismo tamaño.
    """
    # Factorización LU de la cobertura
    P_c, L_c, U_c = lu(A_c)
    
    # Factorización LU de la secreta
    P_s, L_s, U_s = lu(A_s)
    
    # Mezcla
    A_e = L_c @ (U_c + alpha * U_s)
    
    return A_e, L_s, U_c  # U_c se guarda para descifrar


def descifrar_imagen(A_e, L_s, U_c, alpha):
    """
    Descifra para recuperar A_s.
    """
    P_e, L_e, U_e = lu(A_e)
    
    U_s_recuperada = (U_e - U_c) / alpha
    
    A_s_descifrada = L_s @ U_s_recuperada
    
    return A_s_descifrada


def visualizar_comparacion(A_c, A_s, A_e, A_s_desc, titulos=None):
    """
    Muestra las 4 imágenes en una cuadrícula.
    """
    if titulos is None:
        titulos = ["Cobertura", "Secreta original", "Esteganográfica", "Descifrada"]
    
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    
    imagenes = [A_c, A_s, A_e, A_s_desc]
    for i, (ax, img, tit) in enumerate(zip(axes, imagenes, titulos)):
        ax.imshow(img, cmap='gray', vmin=0, vmax=1)
        ax.set_title(tit)
        ax.axis('off')
    
    plt.tight_layout()
    plt.show()


# ============================================================================
# EJEMPLO CON IMÁGENES REALES (MODIFICADO PARA QUE USE BIEN n)
# ============================================================================

print("=" * 70)
print("EJEMPLO CON IMÁGENES REALES (escala de grises)")
print("=" * 70)

# --------------------------------------------------------------
# CAMBIA ESTAS RUTAS (imágenes locales o URLs)
# --------------------------------------------------------------
#ruta_cobertura = "mi_imagen_cobertura.jpg"   
ruta_secreta = "/Users/claudialbombin/Desktop/2025 - 2026/Practicas/Metodos/P6/extracto-cuadrado-color-blanco-negro-sorprende-fondo_38782-108.jpg.avif"       
# --------------------------------------------------------------

# También puedes usar URLs, por ejemplo:
# ruta_cobertura = "https://raw.githubusercontent.com/scikit-image/skimage-data/master/data/astronaut.png"
# ruta_secreta = "https://raw.githubusercontent.com/scikit-image/skimage-data/master/data/camera.png"

try:
    # PASO 1: Cargar la imagen secreta con el MISMO tamaño n
    A_s, n = cargar_imagen_grises_como_cuadrada(ruta_secreta, tamaño_cuadrado=None)
    # PASO 2: Cargar la imagen de cobertura y obtener su tamaño n
    A_c = np.linspace(0, 1, n).reshape(1, n) + np.zeros((n, 1))
    A_c = A_c / np.max(A_c)

    
    print(f"\nAmbas imágenes redimensionadas a {n}x{n}")
    
    alpha = 0.3  # Parámetro de mezcla (ajústalo si ves ruido)
    
    # Cifrar
    print("\n--- CIFRANDO ---")
    A_e, L_s, U_c = cifrar_imagen(A_c, A_s, alpha)
    print("Imagen esteganográfica generada")
    
    # Descifrar
    print("\n--- DESCIFRANDO ---")
    A_s_desc = descifrar_imagen(A_e, L_s, U_c, alpha)
    print("Imagen secreta recuperada")
    
    # Visualizar
    visualizar_comparacion(A_c, A_s, A_e, A_s_desc)
    
    # Error
    error = np.linalg.norm(A_s - A_s_desc) / np.linalg.norm(A_s)
    print(f"\nError relativo de reconstrucción: {error:.2e}")
    
except FileNotFoundError:
    print("\nError: No se encontró el archivo. Revisa las rutas de las imágenes.")
    print("   Asegúrate de que los archivos existan y las rutas sean correctas.")
    
except Exception as e:
    print(f"\n Error inesperado: {e}")
    print("\nProbando con imágenes sintéticas de respaldo...")
    
    # Opción de respaldo: imágenes sintéticas
    n = 128
    # Cobertura: degradado
    A_c = np.linspace(0, 1, n).reshape(1, n) + np.zeros((n, 1))
    A_c = A_c / np.max(A_c)
    # Secreta: círculo blanco
    A_s = np.zeros((n, n))
    centro = n // 2
    radio = n // 4
    for i in range(n):
        for j in range(n):
            if (i - centro)**2 + (j - centro)**2 < radio**2:
                A_s[i, j] = 0.9
    
    alpha = 0.5
    
    print(f"Usando imágenes sintéticas de tamaño {n}x{n}")
    A_e, L_s, U_c = cifrar_imagen(A_c, A_s, alpha)
    A_s_desc = descifrar_imagen(A_e, L_s, U_c, alpha)
    
    visualizar_comparacion(A_c, A_s, A_e, A_s_desc)
    error = np.linalg.norm(A_s - A_s_desc) / np.linalg.norm(A_s)
    print(f"\nError relativo: {error:.2e}")