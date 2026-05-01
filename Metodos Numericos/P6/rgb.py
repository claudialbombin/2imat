"""
Practica 6 - Apartados d y e: Cifrado de imagenes RGB con factorizacion LU
Curso 2025-2026
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import lu
from PIL import Image


# ============================================================================
# CARGA Y GENERACION DE IMAGENES
# ============================================================================

def cargar_imagen_rgb(ruta, tamanyo_cuadrado=None):
    """
    Carga una imagen RGB desde archivo local.

    Retorna la matriz normalizada en [0, 1] con forma (n, n, 3).
    """
    img = Image.open(ruta).convert('RGB')

    if tamanyo_cuadrado is not None:
        img = img.resize((tamanyo_cuadrado, tamanyo_cuadrado), Image.Resampling.LANCZOS)
        n = tamanyo_cuadrado
    else:
        ancho, alto = img.size
        lado = min(ancho, alto)
        izq = (ancho - lado) // 2
        sup = (alto - lado) // 2
        img = img.crop((izq, sup, izq + lado, sup + lado))
        n = lado

    matriz = np.array(img, dtype=np.float64) / 255.0
    print(f"Imagen RGB cargada: {n}x{n} pixeles")
    return matriz, n


def generar_cobertura_rgb(n, tipo="arcoiris"):
    """
    Genera una imagen de cobertura RGB sintetica de tamanyo n x n.

    Tipos disponibles: 'degradados', 'ruido', 'colores_solidos', 'arcoiris'.
    """
    A_c = np.zeros((n, n, 3))

    if tipo == "degradados":
        A_c[:, :, 0] = np.linspace(0, 1, n).reshape(1, n)
        A_c[:, :, 1] = np.linspace(0, 1, n).reshape(n, 1)
        A_c[:, :, 2] = 0.5

    elif tipo == "ruido":
        A_c[:, :, 0] = np.random.rand(n, n)
        A_c[:, :, 1] = np.random.rand(n, n)
        A_c[:, :, 2] = np.random.rand(n, n)

    elif tipo == "colores_solidos":
        m = n // 2
        A_c[:m, :m, 0] = 1.0
        A_c[:m, m:, 1] = 1.0
        A_c[m:, :m, 2] = 1.0
        A_c[m:, m:, 0] = 1.0
        A_c[m:, m:, 1] = 1.0

    else:  # arcoiris por defecto
        ii, jj = np.meshgrid(np.arange(n), np.arange(n), indexing='ij')
        A_c[:, :, 0] = (ii + jj) / (2 * n)
        A_c[:, :, 1] = ii / n
        A_c[:, :, 2] = jj / n

    print(f"Cobertura RGB generada (tipo: {tipo}, tamanyo: {n}x{n})")
    return A_c


def generar_secreta_sintetica(n, tipo="cuadrado"):
    """
    Genera una imagen secreta RGB sintetica de tamanyo n x n.

    Tipos disponibles: 'cuadrado', 'circulo', 'diagonal'.
    """
    A_s = np.zeros((n, n, 3))
    centro = n // 2

    if tipo == "cuadrado":
        tam = n // 6
        A_s[centro - tam:centro + tam, centro - tam:centro + tam, 1] = 1.0
        A_s[centro - tam:centro + tam, centro - tam:centro + tam, 2] = 1.0

    elif tipo == "circulo":
        radio = n // 5
        ii, jj = np.meshgrid(np.arange(n), np.arange(n), indexing='ij')
        mascara = (ii - centro) ** 2 + (jj - centro) ** 2 < radio ** 2
        A_s[mascara, 0] = 1.0
        A_s[mascara, 2] = 1.0

    elif tipo == "diagonal":
        idx = np.arange(n)
        A_s[idx, idx, 0] = 1.0

    print(f"Secreta sintetica generada (tipo: {tipo}, tamanyo: {n}x{n})")
    return A_s


# ============================================================================
# APARTADO d): CIFRADO Y DESCIFRADO RGB
# ============================================================================

def cifrar_rgb(A_c, A_s, alpha):
    """
    Cifrado de una imagen secreta en color RGB mediante factorizacion LU.

    El algoritmo sigue exactamente el enunciado:
        [Lc, Uc] = lu(Ac)
        [Ls, Us] = lu(As)
        Ae = Lc * (Uc + alpha * Us)

    Cada canal R, G, B se trata como una matriz independiente.

    Parametros
    ----------
    A_c : ndarray (n, n, 3)
        Imagen de cobertura, valores en [0, 1].
    A_s : ndarray (n, n, 3)
        Imagen secreta, valores en [0, 1].
    alpha : float
        Parametro de mezcla (alpha > 0).

    Retorna
    -------
    A_e : ndarray (n, n, 3)
        Imagen esteganografica.
    clave : dict
        Clave de descifrado: contiene Ls y Uc por canal, mas alpha.
        Equivale a (Ae, Ls) del enunciado; Uc se guarda porque el receptor
        necesita conocer Ac (o equivalentemente Uc) para descifrar.
    """
    n = A_c.shape[0]
    A_e = np.zeros_like(A_c)
    Ls_canales = []
    Uc_canales = []

    for c in range(3):
        _, Lc, Uc = lu(A_c[:, :, c])
        _, Ls, Us = lu(A_s[:, :, c])

        A_e[:, :, c] = Lc @ (Uc + alpha * Us)

        Ls_canales.append(Ls)
        Uc_canales.append(Uc)

    clave = {"Ls": Ls_canales, "Uc": Uc_canales, "alpha": alpha}
    print("Cifrado completado.")
    return A_e, clave


def descifrar_rgb(A_e, clave):
    """
    Descifrado de la imagen esteganografica para recuperar la imagen secreta.

    El algoritmo sigue exactamente el enunciado:
        [Le, Ue] = lu(Ae)
        As = Ls * (1/alpha) * (Ue - Uc)

    Parametros
    ----------
    A_e : ndarray (n, n, 3)
        Imagen esteganografica recibida.
    clave : dict
        Clave generada durante el cifrado (Ls, Uc, alpha por canal).

    Retorna
    -------
    A_s_rec : ndarray (n, n, 3)
        Imagen secreta recuperada.
    """
    Ls_canales = clave["Ls"]
    Uc_canales = clave["Uc"]
    alpha = clave["alpha"]

    A_s_rec = np.zeros_like(A_e)

    for c in range(3):
        _, Le, Ue = lu(A_e[:, :, c])

        # Segun el enunciado: As = Ls * (1/alpha) * (Ue - Uc)
        Us_rec = (Ue - Uc_canales[c]) / alpha
        A_s_rec[:, :, c] = Ls_canales[c] @ Us_rec

    print("Descifrado completado.")
    return A_s_rec


# ============================================================================
# APARTADO e): POR QUE NO FUNCIONA EL ENFOQUE TENSORIAL
# ============================================================================

def explicar_problema_tensor():
    """
    Explica por que tratar la imagen RGB como un unico tensor 3D
    no es compatible con la factorizacion LU, e ilustra el fallo
    numericamente con un ejemplo pequenyo.
    """
    print()
    print("Apartado e): Por que no funciona tratar la imagen RGB como tensor 3D")
    print("-" * 70)

    explicacion = (
        "La factorizacion LU esta definida exclusivamente para matrices\n"
        "bidimensionales. Una imagen en color es un tensor de orden 3\n"
        "(alto x ancho x canales), por lo que no admite LU directamente.\n"
        "\n"
        "Una estrategia tentadora consiste en apilar los tres canales y\n"
        "construir una unica matriz 2D, por ejemplo de dimension n x (3n)\n"
        "o (3n) x n, aplicar LU sobre ella y luego separar el resultado.\n"
        "El problema es que esto no funciona por las siguientes razones:\n"
        "\n"
        "1. Mezclado de informacion entre canales.\n"
        "   Al concatenar los canales en una sola matriz, la factorizacion\n"
        "   LU introduce dependencias entre filas o columnas que pertenecen\n"
        "   a canales distintos. L y U ya no son separables por canal, de\n"
        "   modo que al intentar recuperar cada canal por separado se\n"
        "   obtiene una mezcla incorrecta de los tres.\n"
        "\n"
        "2. Perdida de la estructura de la mezcla.\n"
        "   El cifrado construye Ae = Lc * (Uc + alpha * Us) canal a canal.\n"
        "   Si en cambio se forma una matriz aumentada M_c con los tres\n"
        "   canales de A_c y se factoriza como [L, U] = lu(M_c), la matriz\n"
        "   L obtenida no coincide con el apilamiento de las Lc individuales.\n"
        "   En consecuencia, el descifrado As = Ls * (1/alpha) * (Ue - Uc)\n"
        "   no puede aplicarse de forma coherente.\n"
        "\n"
        "3. No existe una generalizacion canonica de LU a tensores.\n"
        "   A diferencia de otros objetos del algebra lineal tensorial\n"
        "   (como la SVD, que si admite generalizacion via descomposicion\n"
        "   de Tucker o HOSVD), la factorizacion LU no tiene un analogo\n"
        "   para tensores de orden superior que conserve las propiedades\n"
        "   de triangularidad y que sea invertible canal a canal.\n"
        "\n"
        "Solucion correcta: aplicar LU de forma independiente a cada canal\n"
        "y recomponer el tensor al final. Asi se preserva la estructura de\n"
        "la imagen, el cifrado es invertible y el error de reconstruccion\n"
        "queda en el orden de la precision de punto flotante."
    )

    print(explicacion)

    # Demostracion numerica del fallo
    print()
    print("Demostracion numerica:")
    np.random.seed(0)
    n = 4
    A_c = np.random.rand(n, n, 3)
    A_s = np.random.rand(n, n, 3)
    alpha = 0.3

    # Enfoque canal a canal (correcto)
    _, clave = cifrar_rgb(A_c, A_s, alpha)
    A_s_correcto = descifrar_rgb(cifrar_rgb(A_c, A_s, alpha)[0], clave)
    error_correcto = np.linalg.norm(A_s - A_s_correcto)

    # Enfoque tensorial (incorrecto): se apilan los canales en columnas
    M_c = np.hstack([A_c[:, :, c] for c in range(3)])  # n x (3n)
    M_s = np.hstack([A_s[:, :, c] for c in range(3)])
    _, Lc_t, Uc_t = lu(M_c)
    _, Ls_t, Us_t = lu(M_s)
    M_e = Lc_t @ (Uc_t + alpha * Us_t)
    _, Le_t, Ue_t = lu(M_e)
    M_s_rec = Ls_t @ ((Ue_t - Uc_t) / alpha)
    # Separar canales del resultado
    A_s_tensor = np.stack(
        [M_s_rec[:, c * n:(c + 1) * n] for c in range(3)], axis=2
    )
    error_tensor = np.linalg.norm(A_s - A_s_tensor)

    print(f"  Error de reconstruccion (canal a canal): {error_correcto:.2e}")
    print(f"  Error de reconstruccion (enfoque tensorial): {error_tensor:.2e}")
    print()
    if error_tensor > 1e-6:
        print("  El enfoque tensorial no recupera la imagen secreta correctamente.")
    else:
        print("  (Coincidencia numerica inesperada en este ejemplo.)")


# ============================================================================
# VISUALIZACION
# ============================================================================

def visualizar(A_c, A_s, A_e, A_s_rec, guardar=False, nombre="comparacion_rgb.png"):
    """Muestra las cuatro imagenes en una fila."""
    titulos = ["Cobertura", "Secreta original", "Esteganografica", "Secreta recuperada"]
    imagenes = [A_c, A_s, A_e, A_s_rec]

    fig, ejes = plt.subplots(1, 4, figsize=(16, 4))
    for ax, img, tit in zip(ejes, imagenes, titulos):
        ax.imshow(np.clip(img, 0, 1))
        ax.set_title(tit, fontsize=11)
        ax.axis('off')

    plt.tight_layout()
    if guardar:
        plt.savefig(nombre, dpi=150, bbox_inches='tight')
        print(f"Figura guardada como '{nombre}'")
    plt.show()


# ============================================================================
# EJECUCION PRINCIPAL
# ============================================================================

def main():
    print("Practica 6 - Cifrado de imagenes RGB con factorizacion LU")
    print("=" * 60)

    # Parametros
    TAMANYO = 128
    ALPHA = 0.3
    TIPO_COBERTURA = "arcoiris"

    # Ruta a la imagen secreta real (None para usar imagen sintetica)
    RUTA_SECRETA = None
    # RUTA_SECRETA = "ruta/a/tu/imagen.jpg"

    # Cobertura
    A_c = generar_cobertura_rgb(TAMANYO, tipo=TIPO_COBERTURA)

    # Secreta
    if RUTA_SECRETA is not None:
        try:
            A_s, _ = cargar_imagen_rgb(RUTA_SECRETA, tamanyo_cuadrado=TAMANYO)
        except Exception as e:
            print(f"No se pudo cargar la imagen ({e}). Se usa imagen sintetica.")
            A_s = generar_secreta_sintetica(TAMANYO, tipo="cuadrado")
    else:
        A_s = generar_secreta_sintetica(TAMANYO, tipo="cuadrado")

    print(f"Alpha = {ALPHA}")

    # Cifrado
    A_e, clave = cifrar_rgb(A_c, A_s, ALPHA)

    # Descifrado
    A_s_rec = descifrar_rgb(A_e, clave)

    # Metricas
    norma_s = np.linalg.norm(A_s)
    error_rel = np.linalg.norm(A_s - A_s_rec) / norma_s if norma_s > 0 else float('inf')
    print(f"Error relativo de reconstruccion: {error_rel:.2e}")

    if error_rel < 1e-8:
        print("Recuperacion correcta dentro de la precision numerica.")
    else:
        print("Advertencia: el error es mayor de lo esperado.")

    # Visualizacion
    visualizar(A_c, A_s, A_e, A_s_rec, guardar=True)

    # Apartado e
    explicar_problema_tensor()


if __name__ == "__main__":
    main()