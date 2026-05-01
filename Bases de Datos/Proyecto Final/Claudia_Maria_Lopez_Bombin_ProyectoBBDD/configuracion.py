"""
=============================================================================
PROYECTO FINAL - BASES DE DATOS
Asignatura: Bases de Datos - 2º curso
Grado en Ingeniería Matemática e Inteligencia Artificial (IMAT)
=============================================================================
Alumna: Claudia Maria Lopez Bombin
=============================================================================
Descripción:
    Fichero de configuración centralizado. Contiene:
    - Credenciales de MySQL
    - Credenciales de MongoDB
    - Credenciales de Neo4J
    - Rutas a los ficheros de datos originales
    - Nombres de bases de datos y colecciones

    ¡IMPORTANTE! Los profesores sólo deben modificar este fichero
    para ajustar rutas y credenciales. El resto del proyecto se
    ejecutará correctamente sin cambiar ningún otro fichero.
=============================================================================
"""

# ---------------------------------------------------------------------------
# RUTAS A LOS FICHEROS DE DATOS (modificar según donde estén los archivos)
# ---------------------------------------------------------------------------
RUTA_TOYS          = "data/Toys_and_Games_5.json"
RUTA_VIDEOGAMES    = "data/Video_Games_5.json"
RUTA_MUSIC         = "data/Digital_Music_5.json"
RUTA_INSTRUMENTS   = "data/Musical_Instruments_5.json"

# Mapeo categoria -> ruta (facilita iterar sobre todos los datasets)
DATASETS = {
    "Toys and Games":       RUTA_TOYS,
    "Video Games":          RUTA_VIDEOGAMES,
    "Digital Music":        RUTA_MUSIC,
    "Musical Instruments":  RUTA_INSTRUMENTS,
}

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DE MySQL
# ---------------------------------------------------------------------------
MYSQL_HOST     = "localhost"
MYSQL_PORT     = 3306
MYSQL_USER     = "root"
MYSQL_PASSWORD = "Carlota.22"
MYSQL_DATABASE = "amazon_reviews"   # nombre de la base de datos MySQL

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DE MongoDB
# ---------------------------------------------------------------------------
MONGO_URI      = "mongodb://localhost:27017/"
MONGO_DATABASE = "amazon_reviews_mongo"   # nombre de la base de datos MongoDB
MONGO_COLECCION_REVIEWS = "reviews"       # colección principal de reviews

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DE Neo4J
# ---------------------------------------------------------------------------
NEO4J_URI      = "bolt://localhost:7687"
NEO4J_USER     = "neo4j"
NEO4J_PASSWORD = "neo4j2026"

# ---------------------------------------------------------------------------
# PARÁMETROS DEL PROYECTO (fácilmente modificables)
# ---------------------------------------------------------------------------
# Número de usuarios top para calcular similitudes (sección 4.1)
TOP_USUARIOS_SIMILITUD = 30

# Número de artículos aleatorios en sección 4.2
NUM_ARTICULOS_ALEATORIOS = 5

# Número de usuarios ordenados por nombre para sección 4.3
TOP_USUARIOS_NOMBRE = 400
