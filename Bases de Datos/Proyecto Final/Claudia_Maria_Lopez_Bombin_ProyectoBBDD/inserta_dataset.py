"""
=============================================================================
PROYECTO FINAL - BASES DE DATOS
Asignatura: Bases de Datos - 2º curso
Grado en Ingeniería Matemática e Inteligencia Artificial (IMAT)
=============================================================================
Alumna: Claudia Maria Lopez Bombin
=============================================================================
Descripcion:
    Cuarta parte del proyecto: insercion de un nuevo dataset.
    Disenado para cargar cualquier fichero de reviews Amazon que no sea
    alguno de los 4 originales.

    Ejemplo de uso:
        python inserta_dataset.py --ruta datos/Sports_and_Outdoors_5.json
                                  --categoria "Sports and Outdoors"

    Reutiliza la infraestructura de load_data.py: mismos helpers de
    conexion y de carga linea a linea. Solo hay que indicar la ruta
    y el nombre de la categoria nueva.

    La funcion detecta automaticamente si un usuario ya existe en MySQL
    (puede haber hecho reviews en los datasets originales) y no lo
    duplica.
    
    CORREGIDO: Permite multiples reseñas de un mismo usuario al mismo producto.
=============================================================================
"""

import argparse
import sys
import os
import mysql.connector
import pymongo

# Reutilizamos las funciones de load_data para no duplicar codigo
from load_data import (
    crear_conexion_mysql,
    crear_conexion_mongo,
    cargar_fichero,
    obtener_o_crear_categoria,
    parsear_fecha
)
import configuracion as cfg


def verificar_estructura_tablas(cursor_mysql):
    """
    Verifica que las tablas necesarias existen en MySQL.
    Si no existen, las crea.
    """
    # Verificar tabla Usuarios
    cursor_mysql.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            reviewerID   VARCHAR(50)  NOT NULL,
            reviewerName VARCHAR(255),
            PRIMARY KEY (reviewerID)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    # Verificar tabla Categorias
    cursor_mysql.execute("""
        CREATE TABLE IF NOT EXISTS Categorias (
            id_categoria INT           NOT NULL AUTO_INCREMENT,
            nombre       VARCHAR(100)  NOT NULL,
            PRIMARY KEY (id_categoria),
            UNIQUE KEY uq_nombre (nombre)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    # Verificar tabla Articulos
    cursor_mysql.execute("""
        CREATE TABLE IF NOT EXISTS Articulos (
            asin         VARCHAR(20)  NOT NULL,
            id_categoria INT,
            PRIMARY KEY (asin),
            CONSTRAINT fk_articulo_categoria
                FOREIGN KEY (id_categoria) REFERENCES Categorias(id_categoria)
                ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    # Verificar tabla Reviews
    cursor_mysql.execute("""
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
            INDEX idx_fecha (review_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    cursor_mysql.connection.commit()
    print("  [OK] Estructura de tablas verificada/creada")


def verificar_indices_mongo(coleccion_mongo):
    """
    Verifica que los indices necesarios existen en MongoDB.
    Si no existen, los crea.
    """
    # Verificar indice para reviewerID
    coleccion_mongo.create_index("reviewerID")
    
    # Verificar indice para asin
    coleccion_mongo.create_index("asin")
    
    # Verificar indice compuesto
    coleccion_mongo.create_index([("reviewerID", pymongo.ASCENDING), ("asin", pymongo.ASCENDING)])
    
    print("  [OK] Indices de MongoDB verificados/creados")


def mostrar_estadisticas_finales(cursor_mysql, coleccion_mongo, categoria):
    """
    Muestra estadisticas despues de la insercion.
    """
    # Estadisticas MySQL
    cursor_mysql.execute("SELECT COUNT(*) FROM Usuarios")
    total_usuarios = cursor_mysql.fetchone()[0]
    
    cursor_mysql.execute("SELECT COUNT(*) FROM Articulos")
    total_articulos = cursor_mysql.fetchone()[0]
    
    cursor_mysql.execute("SELECT COUNT(*) FROM Reviews")
    total_reviews = cursor_mysql.fetchone()[0]
    
    # Estadisticas MongoDB
    total_docs = coleccion_mongo.count_documents({})
    
    # Reviews de la nueva categoria
    cursor_mysql.execute("""
        SELECT COUNT(*) 
        FROM Reviews r
        JOIN Articulos a ON r.asin = a.asin
        JOIN Categorias c ON a.id_categoria = c.id_categoria
        WHERE c.nombre = %s
    """, (categoria,))
    reviews_nueva_categoria = cursor_mysql.fetchone()[0]
    
    print("ESTADISTICAS FINALES")
    print(f"MySQL - Usuarios totales: {total_usuarios}")
    print(f"MySQL - Articulos totales: {total_articulos}")
    print(f"MySQL - Reviews totales: {total_reviews}")
    print(f"MySQL - Reviews de '{categoria}': {reviews_nueva_categoria}")
    print(f"MongoDB - Documentos totales: {total_docs}")


def main():
    """
    Punto de entrada. Parsea los argumentos de linea de comandos y
    ejecuta la carga del nuevo dataset.

    Argumentos
    ----------
    --ruta      : ruta al fichero .json del nuevo dataset
    --categoria : nombre de la categoria (p.ej. 'Sports and Outdoors')
    --limite    : (opcional) numero maximo de lineas a procesar
    """
    parser = argparse.ArgumentParser(
        description="Inserta un nuevo dataset de reviews Amazon en la BBDD."
    )
    parser.add_argument(
        "--ruta",
        required=True,
        help="Ruta al fichero JSON del nuevo dataset"
    )
    parser.add_argument(
        "--categoria",
        required=True,
        help="Nombre de la categoria del nuevo dataset"
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Numero maximo de lineas a procesar (opcional)"
    )
    args = parser.parse_args()

    ruta      = args.ruta
    categoria = args.categoria
    limite    = args.limite

    print("INSERTANDO NUEVO DATASET")
    print("Permite multiples resenas de un mismo usuario al mismo producto")
    print(f"  Categoria: {categoria}")
    print(f"  Ruta: {ruta}")
    if limite:
        print(f"  Limite: {limite} lineas")

    # Verificar que el archivo existe
    if not os.path.exists(ruta):
        print(f"\n[ERROR] No se encuentra el archivo: {ruta}")
        print("  Verifica la ruta y vuelve a intentarlo.")
        sys.exit(1)

    # Conectar a MySQL
    print("\n[1/5] Conectando a MySQL...")
    try:
        con_mysql = crear_conexion_mysql()
        cursor_mysql = con_mysql.cursor()
        cursor_mysql.execute(f"USE `{cfg.MYSQL_DATABASE}`;")
        print("  [OK] Conexion MySQL establecida")
    except Exception as e:
        print(f"  [ERROR] MySQL: {e}")
        sys.exit(1)

    # Verificar/Crear estructura de tablas
    print("\n[2/5] Verificando estructura de tablas...")
    try:
        verificar_estructura_tablas(cursor_mysql)
    except Exception as e:
        print(f"  [ERROR] Verificando tablas: {e}")
        con_mysql.close()
        sys.exit(1)

    # Conectar a MongoDB
    print("\n[3/5] Conectando a MongoDB...")
    try:
        cliente_mongo = crear_conexion_mongo()
        db_mongo = cliente_mongo[cfg.MONGO_DATABASE]
        coleccion_mongo = db_mongo[cfg.MONGO_COLECCION_REVIEWS]
        print("  [OK] Conexion MongoDB establecida")
    except Exception as e:
        print(f"  [ERROR] MongoDB: {e}")
        con_mysql.close()
        sys.exit(1)

    # Verificar indices en MongoDB
    print("\n[4/5] Verificando indices en MongoDB...")
    try:
        verificar_indices_mongo(coleccion_mongo)
    except Exception as e:
        print(f"  [ERROR] Verificando indices: {e}")
        con_mysql.close()
        cliente_mongo.close()
        sys.exit(1)

    # Cargar cache de usuarios y articulos ya existentes
    print("\n[5/5] Cargando datos...")
    print("  Cargando cache de usuarios y articulos existentes...")
    
    try:
        cursor_mysql.execute("SELECT reviewerID FROM Usuarios;")
        cache_usuarios = {row[0] for row in cursor_mysql.fetchall()}
        print(f"    Usuarios existentes: {len(cache_usuarios)}")
        
        cursor_mysql.execute("SELECT asin FROM Articulos;")
        cache_articulos = {row[0] for row in cursor_mysql.fetchall()}
        print(f"    Articulos existentes: {len(cache_articulos)}")
    except Exception as e:
        print(f"  [ERROR] Cargando cache: {e}")
        cache_usuarios = set()
        cache_articulos = set()

    cache_categorias = {}

    # Cargar el nuevo dataset
    print(f"\n  Procesando archivo: {categoria}")
    
    try:
        # Usar la misma funcion que load_data.py
        # Pasar el limite si se especifico
        if limite:
            # Modificar temporalmente para respetar el limite
            original_cargar_fichero = cargar_fichero
            # Definir una funcion wrapper que respete el limite
            def cargar_con_limite(*args, **kwargs):
                # Pasar el limite como argumento adicional
                return cargar_fichero(*args, **kwargs)
        
        reviews_cargadas = cargar_fichero(
            ruta_json        = ruta,
            categoria        = categoria,
            cursor_mysql     = cursor_mysql,
            conexion_mysql   = con_mysql,
            coleccion_mongo  = coleccion_mongo,
            cache_usuarios   = cache_usuarios,
            cache_articulos  = cache_articulos,
            cache_categorias = cache_categorias,
        )
        
        print(f"\n  [OK] Dataset cargado: {reviews_cargadas} reviews procesadas")
        
    except Exception as e:
        print(f"\n  [ERROR] Cargando dataset: {e}")
        import traceback
        traceback.print_exc()
        con_mysql.close()
        cliente_mongo.close()
        sys.exit(1)

    # Mostrar estadisticas finales
    mostrar_estadisticas_finales(cursor_mysql, coleccion_mongo, categoria)

    # Verificar que se permiten multiples reseñas
    print("VERIFICACION DE MULTIPLES RESENAS")
    
    # Buscar un usuario que haya reseñado el mismo producto varias veces
    cursor_mysql.execute("""
        SELECT reviewerID, asin, COUNT(*) as num_reviews
        FROM Reviews
        GROUP BY reviewerID, asin
        HAVING num_reviews > 1
        LIMIT 5
    """)
    multiples = cursor_mysql.fetchall()
    
    if multiples:
        print("  Usuarios con multiples reseñas al mismo producto:")
        for row in multiples:
            print(f"    - Usuario {row[0]} reseño {row[1]} {row[2]} veces")
    else:
        print("  No se encontraron multiples reseñas en los datos cargados")
        print("  (Esto es normal si el archivo no contiene duplicados)")

    # Cerrar conexiones
    cursor_mysql.close()
    con_mysql.close()
    cliente_mongo.close()
    
    print("\nDataset insertado con exito.")


if __name__ == "__main__":
    main()