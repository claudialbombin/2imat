"""
=============================================================================
PROYECTO FINAL - BASES DE DATOS
Asignatura: Bases de Datos - 2º curso
Grado en Ingeniería Matemática e Inteligencia Artificial (IMAT)
=============================================================================
Alumna: Claudia Maria Lopez Bombin
=============================================================================
Descripción:
    Menú interactivo de visualización de datos de reviews Amazon.
    Conecta a MySQL y MongoDB para obtener los datos y genera gráficas
    con matplotlib/wordcloud.

    Cada gráfica se muestra en pantalla Y se guarda automáticamente
    en la carpeta  outputs/graficas/  con un nombre descriptivo.

    Opciones disponibles:
      1. Evolución de reviews por años (histograma)
      2. Popularidad de artículos (curva ordenada)
      3. Histograma por nota (overall)
      4. Evolución acumulada de reviews a lo largo del tiempo
      5. Histograma de reviews por usuario
      6. Nube de palabras por categoría
      7. Ratio de utilidad (helpful) por categoría  <- opción extra libre
      0. Salir
=============================================================================
"""

import sys
from pathlib import Path
from datetime import datetime

import matplotlib

# Configuración robusta del backend de matplotlib
def configurar_matplotlib():
    """Configura el backend de matplotlib de forma robusta."""
    # Lista de backends probables en orden de preferencia
    backends = ['TkAgg', 'Qt5Agg', 'MacOSX', 'Agg']
    
    for backend in backends:
        try:
            matplotlib.use(backend)
            import matplotlib.pyplot as plt
            
            # Probar que funciona creando una figura temporal
            fig = plt.figure()
            plt.close(fig)
            
            print(f"[INFO] Usando backend: {backend}")
            return plt
        except (ImportError, RuntimeError, Exception) as e:
            print(f"[WARN] Falló backend {backend}: {e}")
            continue
    
    # Si todo falla, usar Agg (solo guardado, sin display)
    print("[INFO] Usando backend 'Agg' (solo guardado, sin visualización)")
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    return plt

# Configurar matplotlib y obtener plt
plt = configurar_matplotlib()

import matplotlib.ticker as ticker
import mysql.connector
import pymongo
from wordcloud import WordCloud

import configuracion as cfg


# =============================================================================
# CARPETA DE SALIDA PARA LAS GRAFICAS
# =============================================================================

# Obtener el directorio donde está este script
SCRIPT_DIR = Path(__file__).parent.absolute()
CARPETA_OUTPUTS = SCRIPT_DIR / "outputs" / "graficas"

# Crear la carpeta si no existe
try:
    CARPETA_OUTPUTS.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Carpeta de salida: {CARPETA_OUTPUTS}")
except Exception as e:
    print(f"[ERROR] No se pudo crear la carpeta {CARPETA_OUTPUTS}: {e}")
    sys.exit(1)


def guardar_figura(fig, nombre_base: str) -> Path:
    """
    Guarda la figura matplotlib en la carpeta outputs/graficas/ con un
    nombre descriptivo que incluye un timestamp para evitar sobreescrituras.

    La imagen se guarda en formato PNG a 150 DPI.

    Parámetros
    ----------
    fig         : plt.Figure  figura matplotlib a guardar
    nombre_base : str         nombre descriptivo sin extensión

    Retorna
    -------
    Path  ruta completa del fichero guardado, o None si falla
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_fichero = f"{nombre_base}_{timestamp}.png"
    ruta = CARPETA_OUTPUTS / nombre_fichero
    
    try:
        fig.savefig(ruta, dpi=150, bbox_inches="tight", facecolor="white")
        print(f"  [OK] Gráfica guardada en: {ruta}")
        
        # Verificar que el archivo existe
        if ruta.exists():
            tamaño = ruta.stat().st_size
            print(f"  [INFO] Tamaño: {tamaño} bytes")
        return ruta
    except Exception as e:
        print(f"  [ERROR] No se pudo guardar la figura: {e}")
        return None


# =============================================================================
# CONEXIONES
# =============================================================================

def conectar_mysql():
    """Abre y devuelve una conexion MySQL usando los parametros de configuracion.py."""
    return mysql.connector.connect(
        host=cfg.MYSQL_HOST,
        port=cfg.MYSQL_PORT,
        user=cfg.MYSQL_USER,
        password=cfg.MYSQL_PASSWORD,
        database=cfg.MYSQL_DATABASE,
    )


def conectar_mongo():
    """Devuelve la coleccion principal de MongoDB."""
    cliente = pymongo.MongoClient(cfg.MONGO_URI)
    return cliente[cfg.MONGO_DATABASE][cfg.MONGO_COLECCION_REVIEWS]


# =============================================================================
# OPCION 1: Evolucion de reviews por años
# =============================================================================

def opcion_reviews_por_anio() -> None:
    """
    Solicita al usuario el tipo de producto y muestra un histograma
    con el numero de reviews por año extraido de MySQL.
    
    Si el usuario elige "todo", primero muestra el histograma conjunto
    y luego pregunta si quiere ver cada categoría por separado.
    """
    print("\nCategorias disponibles:", list(cfg.DATASETS.keys()), "o 'todo'")
    categoria = input("Introduce la categoria (o 'todo'): ").strip()

    con = conectar_mysql()
    cursor = con.cursor()

    # Caso: categoría específica
    if categoria.lower() != "todo":
        cursor.execute("""
            SELECT YEAR(r.review_date) AS anio, COUNT(*) AS total
            FROM Reviews r
            JOIN Articulos a ON r.asin = a.asin
            JOIN Categorias c ON a.id_categoria = c.id_categoria
            WHERE r.review_date IS NOT NULL
              AND c.nombre = %s
            GROUP BY anio
            ORDER BY anio;
        """, (categoria,))
        
        filas = cursor.fetchall()
        cursor.close()
        con.close()
        
        if not filas:
            print(f"No se encontraron datos para la categoría '{categoria}'.")
            return
        
        anios = [str(f[0]) for f in filas]
        totales = [f[1] for f in filas]
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(anios, totales, color="steelblue", edgecolor="white")
        ax.set_title(f"Evolución de reviews por año — {categoria}")
        ax.set_xlabel("Año")
        ax.set_ylabel("Número de reviews")
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        nombre_cat_safe = categoria.replace(" ", "_").replace("/", "-")
        guardar_figura(fig, f"01_reviews_por_anio_{nombre_cat_safe}")
        
        plt.show()
        plt.close(fig)
        return
    
    # Caso: "todo" - obtener todas las categorías
    cursor.execute("""
        SELECT c.nombre, YEAR(r.review_date) AS anio, COUNT(*) AS total
        FROM Reviews r
        JOIN Articulos a ON r.asin = a.asin
        JOIN Categorias c ON a.id_categoria = c.id_categoria
        WHERE r.review_date IS NOT NULL
        GROUP BY c.nombre, anio
        ORDER BY c.nombre, anio;
    """)
    
    filas = cursor.fetchall()
    cursor.close()
    con.close()
    
    if not filas:
        print("No hay datos.")
        return
    
    # Organizar datos por categoría
    datos_por_categoria = {}
    for nombre_cat, anio, total in filas:
        if nombre_cat not in datos_por_categoria:
            datos_por_categoria[nombre_cat] = {'anios': [], 'totales': []}
        datos_por_categoria[nombre_cat]['anios'].append(str(anio))
        datos_por_categoria[nombre_cat]['totales'].append(total)
    
    # ===== GRÁFICA 1: Todas las categorías (barras agrupadas) =====
    print("\n[1/2] Generando gráfica de TODAS las categorías...")
    
    # Obtener todos los años únicos
    todos_anios = sorted(set([str(a) for _, a, _ in filas]))
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Ancho de cada barra
    n_categorias = len(datos_por_categoria)
    ancho_barra = 0.8 / n_categorias if n_categorias > 0 else 0.1
    
    # Colores para las diferentes categorías
    colores = ['steelblue', 'darkorange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    
    for i, (cat, datos) in enumerate(datos_por_categoria.items()):
        # Crear diccionario año -> total para esta categoría
        anio_total = dict(zip(datos['anios'], datos['totales']))
        # Valores para cada año
        valores = [anio_total.get(anio, 0) for anio in todos_anios]
        # Posiciones de las barras
        posiciones = [j + (i - n_categorias/2) * ancho_barra for j in range(len(todos_anios))]
        ax.bar(posiciones, valores, width=ancho_barra, label=cat, color=colores[i % len(colores)])
    
    ax.set_title("Evolución de reviews por año (TODAS las categorías)")
    ax.set_xlabel("Año")
    ax.set_ylabel("Número de reviews")
    ax.set_xticks(range(len(todos_anios)))
    ax.set_xticklabels(todos_anios, rotation=45)
    ax.legend(loc='best', fontsize=8)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()
    
    guardar_figura(fig, "01_reviews_por_anio_todas_categorias")
    
    plt.show()
    plt.close(fig)
    
    # ===== PREGUNTAR SI QUIERE CADA UNA POR SEPARADO =====
    respuesta = input("¿Quieres ver también cada categoría por separado? (s/n): ").strip().lower()
    
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("Ok. Solo se ha generado la gráfica conjunta.")
        return
    
    # ===== GRÁFICAS 2-N: Cada categoría por separado =====
    print(f"\n[2/2] Generando gráficas individuales para {len(datos_por_categoria)} categorías...")
    
    for cat, datos in datos_por_categoria.items():
        print(f"  Generando gráfica para: {cat}...")
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(datos['anios'], datos['totales'], color="steelblue", edgecolor="white")
        ax.set_title(f"Evolución de reviews por año — {cat}")
        ax.set_xlabel("Año")
        ax.set_ylabel("Número de reviews")
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        nombre_cat_safe = cat.replace(" ", "_").replace("/", "-")
        guardar_figura(fig, f"01_reviews_por_anio_{nombre_cat_safe}")
        
        plt.show()
        plt.close(fig)
    
    print(f"\n[OK] Generadas {len(datos_por_categoria)} gráficas individuales + 1 conjunta.")


# =============================================================================
# OPCION 2: Popularidad de articulos
# =============================================================================

def opcion_popularidad_articulos() -> None:
    """
    Muestra una curva de popularidad (numero de reviews) de los articulos
    ordenados de mayor a menor. Permite filtrar por categoria o mostrar todo.
    """
    print("\nCategorias disponibles:", list(cfg.DATASETS.keys()), "o 'todo'")
    categoria = input("Introduce la categoria (o 'todo'): ").strip()

    con = conectar_mysql()
    cursor = con.cursor()

    if categoria.lower() == "todo":
        cursor.execute("""
            SELECT asin, COUNT(*) AS num_reviews
            FROM Reviews
            GROUP BY asin
            ORDER BY num_reviews DESC;
        """)
    else:
        cursor.execute("""
            SELECT r.asin, COUNT(*) AS num_reviews
            FROM Reviews r
            JOIN Articulos a ON r.asin = a.asin
            JOIN Categorias c ON a.id_categoria = c.id_categoria
            WHERE c.nombre = %s
            GROUP BY r.asin
            ORDER BY num_reviews DESC;
        """, (categoria,))

    filas = cursor.fetchall()
    cursor.close()
    con.close()

    if not filas:
        print("No se encontraron datos.")
        return

    popularidades = [f[1] for f in filas]
    posiciones    = list(range(1, len(popularidades) + 1))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(posiciones, popularidades, color="darkorange", linewidth=1.2)
    ax.set_title(f"Popularidad de articulos (por n de reviews) — {categoria}")
    ax.set_xlabel("Articulo (posicion por popularidad)")
    ax.set_ylabel("Numero de reviews")
    ax.set_yscale("log")
    plt.tight_layout()

    nombre_cat_safe = categoria.replace(" ", "_").replace("/", "-")
    guardar_figura(fig, f"02_popularidad_articulos_{nombre_cat_safe}")

    plt.show()
    plt.close(fig)


# =============================================================================
# OPCION 3: Histograma por nota
# =============================================================================

def opcion_histograma_nota() -> None:
    """
    Histograma del numero de reviews segun la nota (overall: 1-5).
    Permite filtrar por categoria o articulo individual.
    """
    print("\nOpciones: (1) Por tipo de articulo  (2) Por articulo individual")
    modo = input("Selecciona modo [1/2]: ").strip()

    con = conectar_mysql()
    cursor = con.cursor()

    if modo == "2":
        asin = input("Introduce el ASIN del articulo: ").strip()
        cursor.execute(
            "SELECT overall, COUNT(*) FROM Reviews WHERE asin = %s GROUP BY overall ORDER BY overall;",
            (asin,)
        )
        filas = cursor.fetchall()
        if not filas:
            print(f"No se encontro el articulo con ASIN '{asin}'.")
            cursor.close()
            con.close()
            return
        titulo_graf = f"Histograma por nota — ASIN: {asin}"
        sufijo_fn   = f"ASIN_{asin}"
    else:
        print("\nCategorias disponibles:", list(cfg.DATASETS.keys()), "o 'todo'")
        categoria = input("Introduce la categoria (o 'todo'): ").strip()

        if categoria.lower() == "todo":
            cursor.execute("""
                SELECT overall, COUNT(*) AS total
                FROM Reviews
                GROUP BY overall ORDER BY overall;
            """)
        else:
            cursor.execute("""
                SELECT r.overall, COUNT(*) AS total
                FROM Reviews r
                JOIN Articulos a ON r.asin = a.asin
                JOIN Categorias c ON a.id_categoria = c.id_categoria
                WHERE c.nombre = %s
                GROUP BY r.overall ORDER BY r.overall;
            """, (categoria,))
        filas       = cursor.fetchall()
        titulo_graf = f"Histograma por nota — {categoria}"
        sufijo_fn   = categoria.replace(" ", "_").replace("/", "-")

    cursor.close()
    con.close()

    if not filas:
        print("No hay datos.")
        return

    notas   = [str(int(f[0])) for f in filas]
    totales = [f[1] for f in filas]

    colores = ["#d9534f", "#e67e22", "#f1c40f", "#2ecc71", "#27ae60"]
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(notas, totales, color=colores[:len(notas)], edgecolor="white")
    ax.bar_label(bars, fmt="{:,.0f}", padding=3, fontsize=9)
    ax.set_title(titulo_graf)
    ax.set_xlabel("Nota (overall)")
    ax.set_ylabel("Numero de reviews")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()

    guardar_figura(fig, f"03_histograma_nota_{sufijo_fn}")

    plt.show()
    plt.close(fig)


# =============================================================================
# OPCION 4: Evolucion acumulada de reviews por categoria
# =============================================================================

def opcion_evolucion_temporal() -> None:
    """
    Para cada categoria muestra la evolucion acumulada del numero de reviews
    a lo largo del tiempo usando unix_review_time como eje X.
    
    Si el usuario elige "todo", primero muestra la gráfica acumulada de todas
    las categorías juntas y luego pregunta si quiere ver cada una por separado.
    """
    print("\nCategorias disponibles:", list(cfg.DATASETS.keys()), "o 'todo'")
    categoria = input("Introduce la categoria (o 'todo'): ").strip()
    
    con = conectar_mysql()
    cursor = con.cursor()
    
    # Caso: categoría específica
    if categoria.lower() != "todo":
        cursor.execute("""
            SELECT c.nombre, r.unix_review_time
            FROM Reviews r
            JOIN Articulos a ON r.asin = a.asin
            JOIN Categorias c ON a.id_categoria = c.id_categoria
            WHERE r.unix_review_time IS NOT NULL
              AND c.nombre = %s
            ORDER BY r.unix_review_time;
        """, (categoria,))
        
        filas = cursor.fetchall()
        cursor.close()
        con.close()
        
        if not filas:
            print(f"No hay datos temporales para la categoría '{categoria}'.")
            return
        
        # Preparar datos para una sola categoría
        timestamps = [f[1] for f in filas]
        ts_ord = sorted(timestamps)
        acumulado = list(range(1, len(ts_ord) + 1))
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(ts_ord, acumulado, label=categoria, linewidth=2)
        ax.set_title(f"Evolución acumulada de reviews — {categoria}")
        ax.set_xlabel("Unix timestamp")
        ax.set_ylabel("Reviews acumuladas")
        ax.legend()
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
        plt.tight_layout()
        
        nombre_cat_safe = categoria.replace(" ", "_").replace("/", "-")
        guardar_figura(fig, f"04_evolucion_temporal_{nombre_cat_safe}")
        
        plt.show()
        plt.close(fig)
        return
    
    # Caso: "todo" - obtener todas las categorías
    cursor.execute("""
        SELECT c.nombre, r.unix_review_time
        FROM Reviews r
        JOIN Articulos a ON r.asin = a.asin
        JOIN Categorias c ON a.id_categoria = c.id_categoria
        WHERE r.unix_review_time IS NOT NULL
        ORDER BY c.nombre, r.unix_review_time;
    """)
    
    filas = cursor.fetchall()
    cursor.close()
    con.close()
    
    if not filas:
        print("No hay datos temporales.")
        return
    
    # Organizar datos por categoría
    datos = {}
    for nombre_cat, ts in filas:
        datos.setdefault(nombre_cat, []).append(ts)
    
    # ===== GRÁFICA 1: Todas las categorías juntas =====
    print("\n[1/2] Generando gráfica acumulada de TODAS las categorías...")
    
    fig, ax = plt.subplots(figsize=(14, 7))
    colores = ['steelblue', 'darkorange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    
    for i, (cat, timestamps) in enumerate(datos.items()):
        ts_ord = sorted(timestamps)
        acumulado = list(range(1, len(ts_ord) + 1))
        ax.plot(ts_ord, acumulado, label=cat, linewidth=1.5, color=colores[i % len(colores)])
    
    ax.set_title("Evolución acumulada de reviews por categoría (TODAS)")
    ax.set_xlabel("Unix timestamp")
    ax.set_ylabel("Reviews acumuladas")
    ax.legend(loc='best', fontsize=8)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    plt.tight_layout()
    
    guardar_figura(fig, "04_evolucion_temporal_todas_categorias")
    
    plt.show()
    plt.close(fig)
    
    # ===== PREGUNTAR SI QUIERE CADA UNA POR SEPARADO =====
    respuesta = input("¿Quieres ver también cada categoría por separado? (s/n): ").strip().lower()
    
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("Ok. Solo se ha generado la gráfica conjunta.")
        return
    
    # ===== GRÁFICAS 2-N: Cada categoría por separado =====
    print(f"\n[2/2] Generando gráficas individuales para {len(datos)} categorías...")
    
    for cat, timestamps in datos.items():
        print(f"  Generando gráfica para: {cat}...")
        
        ts_ord = sorted(timestamps)
        acumulado = list(range(1, len(ts_ord) + 1))
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(ts_ord, acumulado, label=cat, linewidth=2, color='steelblue')
        ax.set_title(f"Evolución acumulada de reviews — {cat}")
        ax.set_xlabel("Unix timestamp")
        ax.set_ylabel("Reviews acumuladas")
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        nombre_cat_safe = cat.replace(" ", "_").replace("/", "-")
        guardar_figura(fig, f"04_evolucion_temporal_{nombre_cat_safe}")
        
        plt.show()
        plt.close(fig)
    
    print(f"\n[OK] Generadas {len(datos)} gráficas individuales + 1 conjunta.")


# =============================================================================
# OPCION 5: Histograma de reviews por usuario
# =============================================================================

def opcion_reviews_por_usuario() -> None:
    """
    Histograma donde el eje X es el numero de reviews realizadas y el eje Y
    es cuantos usuarios han hecho esa cantidad de reviews.
    """
    con = conectar_mysql()
    cursor = con.cursor()

    cursor.execute("""
        SELECT num_reviews, COUNT(*) AS num_usuarios
        FROM (
            SELECT reviewerID, COUNT(*) AS num_reviews
            FROM Reviews
            GROUP BY reviewerID
        ) conteo
        GROUP BY num_reviews
        ORDER BY num_reviews;
    """)
    filas = cursor.fetchall()
    cursor.close()
    con.close()

    if not filas:
        print("No hay datos.")
        return

    num_reviews  = [f[0] for f in filas]
    num_usuarios = [f[1] for f in filas]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(num_reviews, num_usuarios, color="mediumpurple", edgecolor="white", width=0.8)
    ax.set_title("Distribucion de reviews por usuario")
    ax.set_xlabel("Numero de reviews realizadas")
    ax.set_ylabel("Numero de usuarios")
    ax.set_yscale("log")
    ax.set_xlim(0, min(max(num_reviews), 100))
    plt.tight_layout()

    guardar_figura(fig, "05_reviews_por_usuario")

    plt.show()
    plt.close(fig)


# =============================================================================
# OPCION 6: Nube de palabras por categoria
# =============================================================================

def opcion_nube_palabras() -> None:
    """
    Genera una nube de palabras con el campo 'summary' de MongoDB para
    la categoria seleccionada. Solo considera palabras de longitud > 3.
    """
    categorias = list(cfg.DATASETS.keys())
    print("\nCategorias disponibles:")
    for i, cat in enumerate(categorias, 1):
        print(f"  {i}. {cat}")
    opcion = input("Selecciona una categoria (numero): ").strip()

    try:
        idx               = int(opcion) - 1
        categoria_elegida = categorias[idx]
    except (ValueError, IndexError):
        print("Opcion no valida.")
        return

    con = conectar_mysql()
    cursor = con.cursor()
    cursor.execute("""
        SELECT a.asin FROM Articulos a
        JOIN Categorias c ON a.id_categoria = c.id_categoria
        WHERE c.nombre = %s;
    """, (categoria_elegida,))
    asins = {row[0] for row in cursor.fetchall()}
    cursor.close()
    con.close()

    if not asins:
        print("No hay articulos para esa categoria.")
        return

    coleccion = conectar_mongo()
    docs = coleccion.find(
        {"asin": {"$in": list(asins)}},
        {"summary": 1, "_id": 0}
    )

    texto_total = ""
    for doc in docs:
        summary = doc.get("summary", "")
        if summary:
            palabras = " ".join(p for p in summary.split() if len(p) > 3)
            texto_total += " " + palabras

    if not texto_total.strip():
        print("No hay texto suficiente para generar la nube de palabras.")
        return

    wc = WordCloud(
        width=900, height=500,
        background_color="white",
        colormap="viridis",
        max_words=200,
    ).generate(texto_total)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title(f"Nube de palabras — {categoria_elegida}", fontsize=14)
    plt.tight_layout()

    nombre_cat_safe = categoria_elegida.replace(" ", "_").replace("/", "-")
    guardar_figura(fig, f"06_nube_palabras_{nombre_cat_safe}")

    plt.show()
    plt.close(fig)


# =============================================================================
# OPCION 7: Ratio de utilidad por categoria (opcion extra)
# =============================================================================

def opcion_ratio_utilidad() -> None:
    """
    OPCION EXTRA (libre): Muestra el ratio medio de utilidad de las reviews
    (helpful_votes / helpful_total) por categoria.
    Solo considera reviews donde helpful_total > 0.
    """
    con = conectar_mysql()
    cursor = con.cursor()

    cursor.execute("""
        SELECT c.nombre,
               AVG(r.helpful_votes / r.helpful_total) AS ratio_medio
        FROM Reviews r
        JOIN Articulos a ON r.asin = a.asin
        JOIN Categorias c ON a.id_categoria = c.id_categoria
        WHERE r.helpful_total > 0
        GROUP BY c.nombre
        ORDER BY ratio_medio DESC;
    """)
    filas = cursor.fetchall()
    cursor.close()
    con.close()

    if not filas:
        print("No hay datos de utilidad.")
        return

    categorias = [f[0] for f in filas]
    ratios     = [f[1] for f in filas]

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(categorias, ratios, color="teal", edgecolor="white")
    ax.bar_label(bars, fmt="{:.2f}", padding=3, fontsize=9)
    ax.set_title("Ratio medio de utilidad (helpful) por categoria")
    ax.set_xlabel("Ratio medio (votos utiles / total votos)")
    ax.set_xlim(0, 1.05)
    plt.tight_layout()

    guardar_figura(fig, "07_ratio_utilidad_por_categoria")

    plt.show()
    plt.close(fig)


# =============================================================================
# MENU PRINCIPAL
# =============================================================================

def mostrar_menu() -> None:
    """Imprime las opciones del menu e indica la carpeta de guardado."""
    print("  MENU DE VISUALIZACION — Reviews Amazon")
    print(f"  Graficas en: {CARPETA_OUTPUTS}")
    print("  1. Evolucion de reviews por años")
    print("  2. Popularidad de articulos")
    print("  3. Histograma por nota (overall)")
    print("  4. Evolucion acumulada de reviews por categoria")
    print("  5. Histograma de reviews por usuario")
    print("  6. Nube de palabras por categoria")
    print("  7. Ratio de utilidad por categoria [EXTRA]")
    print("  0. Salir")


def main():
    """
    Bucle principal del menu.
    Se repite hasta que el usuario elige la opcion 0 (salir).
    """
    print(f"\n[INFO] Las graficas se guardaran en: {CARPETA_OUTPUTS}")

    opciones = {
        "1": opcion_reviews_por_anio,
        "2": opcion_popularidad_articulos,
        "3": opcion_histograma_nota,
        "4": opcion_evolucion_temporal,
        "5": opcion_reviews_por_usuario,
        "6": opcion_nube_palabras,
        "7": opcion_ratio_utilidad,
    }

    while True:
        mostrar_menu()
        eleccion = input("Selecciona una opcion: ").strip()

        if eleccion == "0":
            print(f"\nHasta luego! Graficas guardadas en: {CARPETA_OUTPUTS}")
            sys.exit(0)
        elif eleccion in opciones:
            try:
                opciones[eleccion]()
            except Exception as e:
                print(f"[ERROR] {e}")
                import traceback
                traceback.print_exc()
        else:
            print("Opcion no valida. Introduce un numero del 0 al 7.")


if __name__ == "__main__":
    main()