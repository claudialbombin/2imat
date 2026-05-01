"""
=============================================================================
PROYECTO FINAL - BASES DE DATOS
Asignatura: Bases de Datos - 2º curso
Grado en Ingeniería Matemática e Inteligencia Artificial (IMAT)
=============================================================================
Alumna: Claudia Maria Lopez Bombin
=============================================================================
Descripcion:
    Fichero de carga de datos. Realiza las siguientes operaciones:
      1. Crea la base de datos MySQL y sus tablas (schema relacional).
      2. Crea la base de datos MongoDB y sus colecciones.
      3. Lee los ficheros JSON de reviews linea a linea (sin cargar
         el fichero entero en memoria) e inserta los datos en ambas BBDDs.
    
    CORREGIDO: Permite multiples reseñas de un mismo usuario a un mismo producto.
=============================================================================
"""

import json
from datetime import datetime
import mysql.connector
import pymongo

import configuracion as cfg


def parsear_fecha(fecha_str: str) -> str | None:
    """Convierte la cadena de fecha del JSON a formato YYYY-MM-DD."""
    if not fecha_str:
        return None
    fecha_str = fecha_str.strip()
    formatos = ["%m %d, %Y", "%m %d,%Y"]
    for fmt in formatos:
        try:
            return datetime.strptime(fecha_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def crear_conexion_mysql() -> mysql.connector.MySQLConnection:
    """Crea y devuelve una conexion a MySQL."""
    return mysql.connector.connect(
        host=cfg.MYSQL_HOST,
        port=cfg.MYSQL_PORT,
        user=cfg.MYSQL_USER,
        password=cfg.MYSQL_PASSWORD,
    )


def crear_conexion_mongo() -> pymongo.MongoClient:
    """Crea y devuelve un cliente de MongoDB."""
    return pymongo.MongoClient(cfg.MONGO_URI)


def crear_base_datos_mysql(conexion: mysql.connector.MySQLConnection) -> None:
    """Crea la base de datos y todas las tablas en MySQL."""
    cursor = conexion.cursor()

    # Crear base de datos
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{cfg.MYSQL_DATABASE}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    )
    cursor.execute(f"USE `{cfg.MYSQL_DATABASE}`;")

    # Tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            reviewerID   VARCHAR(50)  NOT NULL,
            reviewerName VARCHAR(255),
            PRIMARY KEY (reviewerID)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # Tabla de categorias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Categorias (
            id_categoria INT           NOT NULL AUTO_INCREMENT,
            nombre       VARCHAR(100)  NOT NULL,
            PRIMARY KEY (id_categoria),
            UNIQUE KEY uq_nombre (nombre)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # Tabla de articulos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Articulos (
            asin         VARCHAR(20)  NOT NULL,
            id_categoria INT,
            PRIMARY KEY (asin),
            CONSTRAINT fk_articulo_categoria
                FOREIGN KEY (id_categoria) REFERENCES Categorias(id_categoria)
                ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # Tabla de reviews (permite multiples reseñas del mismo usuario al mismo producto)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Reviews (
            id_review        INT         NOT NULL AUTO_INCREMENT,
            reviewerID       VARCHAR(50) NOT NULL,
            asin             VARCHAR(20) NOT NULL,
            overall          FLOAT       NOT NULL,
            helpful_votes    INT         DEFAULT 0,
            helpful_total    INT         DEFAULT 0,
            unix_review_time BIGINT,
            review_date      DATE,
            PRIMARY KEY (id_review),
            CONSTRAINT fk_review_usuario
                FOREIGN KEY (reviewerID) REFERENCES Usuarios(reviewerID)
                ON DELETE CASCADE,
            CONSTRAINT fk_review_articulo
                FOREIGN KEY (asin) REFERENCES Articulos(asin)
                ON DELETE CASCADE,
            INDEX idx_usuario (reviewerID),
            INDEX idx_articulo (asin),
            INDEX idx_fecha (review_date),
            INDEX idx_unix_time (unix_review_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    conexion.commit()
    cursor.close()
    print(f"[MySQL] Base de datos '{cfg.MYSQL_DATABASE}' y tablas creadas correctamente.")


def crear_base_datos_mongo(cliente: pymongo.MongoClient) -> None:
    """Inicializa MongoDB y crea los indices necesarios."""
    db = cliente[cfg.MONGO_DATABASE]
    
    # Eliminar coleccion si existe para empezar limpio
    if cfg.MONGO_COLECCION_REVIEWS in db.list_collection_names():
        db[cfg.MONGO_COLECCION_REVIEWS].drop()
    
    coleccion = db[cfg.MONGO_COLECCION_REVIEWS]

    # Crear indices para consultas eficientes
    coleccion.create_index("reviewerID")
    coleccion.create_index("asin")
    coleccion.create_index("unixReviewTime")
    coleccion.create_index([("reviewerID", pymongo.ASCENDING), ("asin", pymongo.ASCENDING)])

    print(f"[MongoDB] Base de datos '{cfg.MONGO_DATABASE}' e indices creados.")


def obtener_o_crear_categoria(cursor, nombre_categoria: str, cache_categorias: dict) -> int:
    """Obtiene el ID de una categoria o la crea si no existe."""
    if nombre_categoria in cache_categorias:
        return cache_categorias[nombre_categoria]

    cursor.execute(
        "INSERT IGNORE INTO Categorias (nombre) VALUES (%s);",
        (nombre_categoria,)
    )
    cursor.execute(
        "SELECT id_categoria FROM Categorias WHERE nombre = %s;",
        (nombre_categoria,)
    )
    row = cursor.fetchone()
    id_cat = row[0]
    cache_categorias[nombre_categoria] = id_cat
    return id_cat


def cargar_fichero(
    ruta_json: str,
    categoria: str,
    cursor_mysql,
    conexion_mysql: mysql.connector.MySQLConnection,
    coleccion_mongo,
    cache_usuarios: set,
    cache_articulos: set,
    cache_categorias: dict,
    batch_size: int = 1000
) -> int:
    """
    Lee un fichero JSON linea a linea y carga los datos en MySQL y MongoDB.
    
    Retorna el numero de reviews procesadas.
    """
    print(f"\n  Procesando {categoria} desde {ruta_json}")
    
    if not os.path.exists(ruta_json):
        print(f"  [ERROR] Archivo no encontrado: {ruta_json}")
        return 0
    
    id_categoria = obtener_o_crear_categoria(cursor_mysql, categoria, cache_categorias)
    
    batch_mysql_reviews = []
    batch_mongo = []
    total_procesadas = 0
    lineas_leidas = 0
    
    try:
        with open(ruta_json, 'r', encoding='utf-8') as f:
            for linea in f:
                lineas_leidas += 1
                linea = linea.strip()
                if not linea:
                    continue
                
                try:
                    review = json.loads(linea)
                except json.JSONDecodeError as e:
                    print(f"  [WARN] Error JSON en linea {lineas_leidas}: {e}")
                    continue
                
                # Extraer campos
                reviewer_id = review.get('reviewerID', '')
                asin = review.get('asin', '')
                reviewer_name = review.get('reviewerName', '')
                helpful = review.get('helpful', [0, 0])
                overall = review.get('overall', 0.0)
                review_text = review.get('reviewText', '')
                summary = review.get('summary', '')
                unix_time = review.get('unixReviewTime', None)
                review_time = review.get('reviewTime', '')
                
                # Validar campos obligatorios
                if not reviewer_id or not asin:
                    continue
                
                # Parsear fecha
                fecha_sql = parsear_fecha(review_time)
                
                helpful_votes = helpful[0] if len(helpful) > 0 else 0
                helpful_total = helpful[1] if len(helpful) > 1 else 0
                
                # Insertar usuario si es nuevo
                if reviewer_id not in cache_usuarios:
                    try:
                        cursor_mysql.execute(
                            "INSERT IGNORE INTO Usuarios (reviewerID, reviewerName) VALUES (%s, %s);",
                            (reviewer_id, reviewer_name[:255] if reviewer_name else '')
                        )
                        cache_usuarios.add(reviewer_id)
                    except Exception as e:
                        print(f"  [WARN] Error insertando usuario {reviewer_id}: {e}")
                
                # Insertar articulo si es nuevo
                if asin not in cache_articulos:
                    try:
                        cursor_mysql.execute(
                            "INSERT IGNORE INTO Articulos (asin, id_categoria) VALUES (%s, %s);",
                            (asin, id_categoria)
                        )
                        cache_articulos.add(asin)
                    except Exception as e:
                        print(f"  [WARN] Error insertando articulo {asin}: {e}")
                
                # Preparar para batch de MySQL
                batch_mysql_reviews.append((
                    reviewer_id, asin, overall,
                    helpful_votes, helpful_total,
                    unix_time, fecha_sql
                ))
                
                # Preparar para batch de MongoDB
                batch_mongo.append({
                    "reviewerID": reviewer_id,
                    "asin": asin,
                    "reviewText": review_text,
                    "summary": summary,
                    "overall": overall,
                    "helpful_votes": helpful_votes,
                    "helpful_total": helpful_total,
                    "unixReviewTime": unix_time,
                    "reviewTime": review_time,
                    "reviewDate": fecha_sql,
                    "categoria": categoria
                })
                
                total_procesadas += 1
                
                # Insertar batch cuando se alcanza el limite
                if len(batch_mysql_reviews) >= batch_size:
                    try:
                        cursor_mysql.executemany(
                            "INSERT INTO Reviews "
                            "(reviewerID, asin, overall, helpful_votes, helpful_total, "
                            " unix_review_time, review_date) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s);",
                            batch_mysql_reviews
                        )
                        conexion_mysql.commit()
                        
                        coleccion_mongo.insert_many(batch_mongo)
                        
                        print(f"    Procesadas {total_procesadas} reviews para {categoria}...")
                        
                        batch_mysql_reviews = []
                        batch_mongo = []
                        
                    except Exception as e:
                        print(f"  [ERROR] Error insertando batch: {e}")
                        conexion_mysql.rollback()
                        batch_mysql_reviews = []
                        batch_mongo = []
        
        # Insertar ultimo batch
        if batch_mysql_reviews:
            try:
                cursor_mysql.executemany(
                    "INSERT INTO Reviews "
                    "(reviewerID, asin, overall, helpful_votes, helpful_total, "
                    " unix_review_time, review_date) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s);",
                    batch_mysql_reviews
                )
                conexion_mysql.commit()
                
                if batch_mongo:
                    coleccion_mongo.insert_many(batch_mongo)
                    
            except Exception as e:
                print(f"  [ERROR] Error insertando batch final: {e}")
                conexion_mysql.rollback()
        
        print(f"  [OK] {categoria}: {total_procesadas} reviews cargadas")
        return total_procesadas
        
    except Exception as e:
        print(f"  [ERROR] Error procesando {ruta_json}: {e}")
        return total_procesadas


def main():
    """Funcion principal."""
    print("CARGA DE DATOS - Proyecto Bases de Datos")
    print("Permite multiples resenas de un mismo usuario al mismo producto")

    # Conectar a MySQL
    print("\n[1/4] Conectando a MySQL...")
    try:
        con_mysql = crear_conexion_mysql()
        cursor_mysql = con_mysql.cursor()
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a MySQL: {e}")
        return

    # Crear base de datos y tablas en MySQL
    print("\n[2/4] Creando esquema en MySQL...")
    crear_base_datos_mysql(con_mysql)

    # Conectar a MongoDB
    print("\n[3/4] Conectando a MongoDB...")
    try:
        cliente_mongo = crear_conexion_mongo()
        crear_base_datos_mongo(cliente_mongo)
        coleccion_mongo = cliente_mongo[cfg.MONGO_DATABASE][cfg.MONGO_COLECCION_REVIEWS]
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a MongoDB: {e}")
        con_mysql.close()
        return

    # Cargar datos
    print("\n[4/4] Cargando datasets...")
    
    cache_usuarios = set()
    cache_articulos = set()
    cache_categorias = {}
    total_reviews = 0
    
    for categoria, ruta in cfg.DATASETS.items():
        reviews_cargadas = cargar_fichero(
            ruta_json=ruta,
            categoria=categoria,
            cursor_mysql=cursor_mysql,
            conexion_mysql=con_mysql,
            coleccion_mongo=coleccion_mongo,
            cache_usuarios=cache_usuarios,
            cache_articulos=cache_articulos,
            cache_categorias=cache_categorias
        )
        total_reviews += reviews_cargadas

    # Estadisticas finales
    print("CARGA COMPLETADA")
    
    cursor_mysql.execute("SELECT COUNT(*) FROM Usuarios")
    total_usuarios = cursor_mysql.fetchone()[0]
    
    cursor_mysql.execute("SELECT COUNT(*) FROM Articulos")
    total_articulos = cursor_mysql.fetchone()[0]
    
    cursor_mysql.execute("SELECT COUNT(*) FROM Reviews")
    total_reviews_mysql = cursor_mysql.fetchone()[0]
    
    total_mongo = coleccion_mongo.count_documents({})
    
    print(f"MySQL - Usuarios: {total_usuarios}")
    print(f"MySQL - Articulos: {total_articulos}")
    print(f"MySQL - Reviews: {total_reviews_mysql}")
    print(f"MongoDB - Documentos: {total_mongo}")

    # Cerrar conexiones
    cursor_mysql.close()
    con_mysql.close()
    cliente_mongo.close()
    
    print("\nCarga completada con exito.")


if __name__ == "__main__":
    import os
    main()