"""
=============================================================================
PROYECTO FINAL - BASES DE DATOS - CARGA DE DATOS EN NEO4J
Asignatura: Bases de Datos - 2º curso
Grado en Ingeniería Matemática e Inteligencia Artificial (IMAT)
=============================================================================
Alumna: Claudia Maria Lopez Bombin
=============================================================================
Descripcion:
    Script para cargar los datos de Amazon Reviews en Neo4J.
    Lee los archivos JSON de las diferentes categorias y crea:
    - Nodos Usuario con sus propiedades
    - Nodos Articulo con sus propiedades
    - Relaciones REVIEW entre usuarios y artículos
    
    CORREGIDO: Permite multiples reseñas de un mismo usuario a un mismo articulo
    usando CREATE en lugar de MERGE para las relaciones REVIEW.
    Los datos se cargan desde los archivos especificados en configuracion.py
=============================================================================
"""

from neo4j import GraphDatabase
import json
import os
import sys
from datetime import datetime
from configuracion import (
    NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD,
    DATASETS, RUTA_TOYS, RUTA_VIDEOGAMES, RUTA_MUSIC, RUTA_INSTRUMENTS
)


class CargarDatosNeo4j:
    """
    Clase para gestionar la carga de datos en Neo4J.
    """
    
    def __init__(self, uri, user, password):
        """
        Inicializa la conexion con Neo4J.
        
        Args:
            uri (str): URI de conexion a Neo4J
            user (str): Nombre de usuario
            password (str): Contraseña
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        print(f"Conectando a Neo4J en {uri}")
    
    def close(self):
        """Cierra la conexion con Neo4J."""
        self.driver.close()
        print("Conexion con Neo4J cerrada")
    
    def limpiar_base_datos(self):
        """
        Elimina todos los nodos y relaciones de la base de datos.
        ATENCION: Esta operacion es irreversible.
        """
        with self.driver.session() as session:
            print("Limpiando base de datos...")
            session.run("MATCH (n) DETACH DELETE n")
            print("Base de datos limpiada correctamente")
    
    def crear_indices(self):
        """
        Crea indices en Neo4J para mejorar el rendimiento de las consultas.
        Los indices se crean en las propiedades mas utilizadas.
        """
        with self.driver.session() as session:
            print("Creando indices...")
            
            # Indices para usuarios
            session.run("CREATE INDEX IF NOT EXISTS FOR (u:Usuario) ON (u.id)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (u:Usuario) ON (u.nombre)")
            
            # Indices para articulos
            session.run("CREATE INDEX IF NOT EXISTS FOR (a:Articulo) ON (a.id)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (a:Articulo) ON (a.tipo)")
            session.run("CREATE INDEX IF NOT EXISTS FOR (a:Articulo) ON (a.nombre)")
            
            print("Indices creados correctamente")
    
    def mapear_tipo_articulo(self, categoria_dataset):
        """
        Mapea la categoria del dataset a un tipo mas legible.
        
        Args:
            categoria_dataset (str): Categoria original del dataset
            
        Returns:
            str: Tipo de articulo simplificado
        """
        mapping = {
            "Video Games": "Videojuegos",
            "Toys and Games": "Juguetes",
            "Digital Music": "Discos",
            "Musical Instruments": "Instrumentos Musicales"
        }
        return mapping.get(categoria_dataset, categoria_dataset)
    
    def cargar_dataset(self, ruta_archivo, tipo_articulo, limite=200):
        """
        Carga un archivo JSON completo en Neo4J.
        
        Args:
            ruta_archivo (str): Ruta al archivo JSON
            tipo_articulo (str): Tipo de articulo (Videojuegos, Discos, etc.)
            limite (int): Numero maximo de reviews a cargar por archivo
            
        Returns:
            int: Numero de reviews cargadas
        """
        print(f"\nCargando {tipo_articulo} desde {ruta_archivo}...")
        
        # Verificar que el archivo existe
        if not os.path.exists(ruta_archivo):
            print(f"ERROR: Archivo no encontrado: {ruta_archivo}")
            print(f"       Asegurate de que el archivo existe en la ruta especificada")
            return 0
        
        contador_reviews = 0
        errores = 0
        usuarios_creados = set()
        articulos_creados = set()
        
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                for num_linea, linea in enumerate(f):
                    # Limite de reviews por archivo
                    if num_linea >= limite:
                        break
                    
                    try:
                        # Parsear la linea JSON
                        review = json.loads(linea.strip())
                        
                        # Extraer datos de la review
                        usuario_id = review.get('reviewerID', '')
                        usuario_nombre = review.get('reviewerName', f'Usuario_{usuario_id[:8]}')
                        articulo_id = review.get('asin', '')
                        articulo_nombre = review.get('title', f'Articulo_{articulo_id[:8]}')
                        nota = float(review.get('overall', 3.0))
                        momento = review.get('reviewTime', '')
                        unix_time = review.get('unixReviewTime', None)
                        
                        # Validar datos minimos necesarios
                        if not usuario_id or not articulo_id:
                            errores += 1
                            continue
                        
                        # Crear nodos y relacion en Neo4J
                        with self.driver.session() as session:
                            # Crear o actualizar nodo Usuario (MERGE para evitar duplicados)
                            session.run("""
                                MERGE (u:Usuario {id: $usuario_id})
                                SET u.nombre = $nombre
                            """, usuario_id=usuario_id, nombre=usuario_nombre)
                            
                            # Crear o actualizar nodo Articulo (MERGE para evitar duplicados)
                            session.run("""
                                MERGE (a:Articulo {id: $articulo_id})
                                SET a.nombre = $nombre, a.tipo = $tipo
                            """, articulo_id=articulo_id, nombre=articulo_nombre, tipo=tipo_articulo)
                            
                            # CREAR relacion REVIEW (CREATE para permitir multiples reseñas)
                            # Un mismo usuario puede reseñar el mismo articulo multiples veces
                            session.run("""
                                MATCH (u:Usuario {id: $usuario_id})
                                MATCH (a:Articulo {id: $articulo_id})
                                CREATE (u)-[r:REVIEW {nota: $nota, momento: $momento, unix_time: $unix_time}]->(a)
                            """, usuario_id=usuario_id, articulo_id=articulo_id, 
                                 nota=nota, momento=momento, unix_time=unix_time)
                        
                        contador_reviews += 1
                        
                        if contador_reviews % 100 == 0:
                            print(f"   Procesadas {contador_reviews} reviews...")
                            
                    except json.JSONDecodeError as e:
                        print(f"   Error JSON en linea {num_linea}: {e}")
                        errores += 1
                        continue
                    except Exception as e:
                        print(f"   Error en linea {num_linea}: {e}")
                        errores += 1
                        continue
        
        except FileNotFoundError:
            print(f"ERROR: No se encontro el fichero: {ruta_archivo}")
            return 0
        except Exception as e:
            print(f"ERROR general procesando {ruta_archivo}: {e}")
            return 0
        
        print(f"Cargadas {contador_reviews} reviews para {tipo_articulo} (errores: {errores})")
        return contador_reviews
    
    def cargar_datos_ejemplo(self):
        """
        Carga datos de ejemplo si no existen los archivos reales.
        Incluye ejemplos de multiples reseñas de un mismo usuario al mismo articulo.
        """
        print("\nCargando datos de ejemplo...")
        
        # Datos de ejemplo - Usuarios
        usuarios = [
            ("U001", "Juan Perez"),
            ("U002", "Maria Garcia"),
            ("U003", "Carlos Lopez"),
            ("U004", "Ana Martinez"),
            ("U005", "Luis Fernandez"),
            ("U006", "Carmen Ruiz"),
            ("U007", "Jose Sanchez"),
            ("U008", "Isabel Torres")
        ]
        
        # Datos de ejemplo - Articulos
        articulos = [
            ("A001", "The Legend of Zelda", "Videojuegos"),
            ("A002", "FIFA 24", "Videojuegos"),
            ("A003", "Super Mario Odyssey", "Videojuegos"),
            ("A004", "Call of Duty", "Videojuegos"),
            ("A005", "Thriller - Michael Jackson", "Discos"),
            ("A006", "Abbey Road - The Beatles", "Discos"),
            ("A007", "Dark Side of the Moon - Pink Floyd", "Discos"),
            ("A008", "Lego Star Wars", "Juguetes"),
            ("A009", "Barbie Dreamhouse", "Juguetes"),
            ("A010", "Chess Set", "Juguetes"),
            ("A011", "Yamaha Piano", "Instrumentos Musicales"),
            ("A012", "Fender Guitar", "Instrumentos Musicales")
        ]
        
        # Datos de ejemplo - Reviews (incluyendo multiples reseñas del mismo usuario al mismo articulo)
        # NOTA: El usuario U001 (Juan) reseña Zelda (A001) DOS VECES en diferentes fechas
        reviews = [
            # Juan U001 - multiples reseñas a Zelda
            ("U001", "A001", 9, "2024-01-15", 1705305600),
            ("U001", "A001", 8, "2024-06-20", 1718870400),  # Segunda reseña de Juan a Zelda
            ("U001", "A002", 8, "2024-01-16", 1705392000),
            ("U001", "A005", 7, "2024-01-17", 1705478400),
            
            # Maria U002
            ("U002", "A001", 8, "2024-01-18", 1705564800),
            ("U002", "A003", 9, "2024-01-19", 1705651200),
            ("U002", "A006", 8, "2024-01-20", 1705737600),
            ("U002", "A008", 7, "2024-01-21", 1705824000),
            
            # Carlos U003
            ("U003", "A002", 7, "2024-01-22", 1705910400),
            ("U003", "A004", 8, "2024-01-23", 1705996800),
            ("U003", "A007", 9, "2024-01-24", 1706083200),
            ("U003", "A011", 6, "2024-01-25", 1706169600),
            
            # Ana U004
            ("U004", "A001", 9, "2024-01-26", 1706256000),
            ("U004", "A005", 8, "2024-01-27", 1706342400),
            ("U004", "A009", 9, "2024-01-28", 1706428800),
            ("U004", "A010", 7, "2024-01-29", 1706515200),
            
            # Luis U005
            ("U005", "A002", 6, "2024-01-30", 1706601600),
            ("U005", "A006", 9, "2024-01-31", 1706688000),
            ("U005", "A012", 8, "2024-02-01", 1706774400),
            
            # Carmen U006
            ("U006", "A001", 7, "2024-02-02", 1706860800),
            ("U006", "A003", 8, "2024-02-03", 1706947200),
            ("U006", "A005", 9, "2024-02-04", 1707033600),
            ("U006", "A008", 8, "2024-02-05", 1707120000),
            
            # Jose U007
            ("U007", "A002", 5, "2024-02-06", 1707206400),
            ("U007", "A004", 7, "2024-02-07", 1707292800),
            ("U007", "A007", 8, "2024-02-08", 1707379200),
            ("U007", "A009", 6, "2024-02-09", 1707465600),
            
            # Isabel U008
            ("U008", "A001", 8, "2024-02-10", 1707552000),
            ("U008", "A003", 9, "2024-02-11", 1707638400),
            ("U008", "A006", 7, "2024-02-12", 1707724800),
            ("U008", "A010", 8, "2024-02-13", 1707811200),
            ("U008", "A011", 7, "2024-02-14", 1707897600)
        ]
        
        with self.driver.session() as session:
            # Crear usuarios
            print("   Creando usuarios...")
            for uid, nombre in usuarios:
                session.run("MERGE (u:Usuario {id: $id}) SET u.nombre = $nombre", 
                           id=uid, nombre=nombre)
            
            # Crear articulos
            print("   Creando articulos...")
            for aid, nombre, tipo in articulos:
                session.run("MERGE (a:Articulo {id: $id}) SET a.nombre = $nombre, a.tipo = $tipo",
                           id=aid, nombre=nombre, tipo=tipo)
            
            # Crear reviews con CREATE (permite multiples reseñas)
            print("   Creando reviews (incluyendo multiples reseñas)...")
            for uid, aid, nota, momento, unix_time in reviews:
                session.run("""
                    MATCH (u:Usuario {id: $uid})
                    MATCH (a:Articulo {id: $aid})
                    CREATE (u)-[r:REVIEW {nota: $nota, momento: $momento, unix_time: $unix_time}]->(a)
                """, uid=uid, aid=aid, nota=nota, momento=momento, unix_time=unix_time)
        
        print("Datos de ejemplo cargados correctamente:")
        print(f"   - {len(usuarios)} usuarios")
        print(f"   - {len(articulos)} articulos")
        print(f"   - {len(reviews)} reviews (incluyendo reseñas multiples)")
        
        # Verificar multiples reseñas
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:Usuario)-[r:REVIEW]->(a:Articulo)
                RETURN u.id AS usuario, a.id AS articulo, COUNT(r) AS num_reviews
                ORDER BY num_reviews DESC
                LIMIT 5
            """)
            multiples = list(result)
            if multiples:
                print("\n   VERIFICACION: Usuarios con multiples reseñas al mismo articulo:")
                for row in multiples:
                    if row["num_reviews"] > 1:
                        print(f"      - Usuario {row['usuario']} reseño {row['articulo']} {row['num_reviews']} veces")


def main():
    """
    Funcion principal del script de carga.
    """
    print("CARGANDO DATOS EN NEO4J")
    print("Version corregida - Permite multiples reseñas de un mismo usuario al mismo articulo")
    
    cargador = CargarDatosNeo4j(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # Limpiar base de datos
        print("\n[1/4] Limpiando base de datos...")
        cargador.limpiar_base_datos()
        
        # Crear indices
        print("\n[2/4] Creando indices...")
        cargador.crear_indices()
        
        # Verificar archivos y cargar datos reales o de ejemplo
        print("\n[3/4] Verificando archivos de datos...")
        total_reviews = 0
        archivos_cargados = False
        
        # Lista de datasets a procesar
        datasets_a_procesar = [
            (RUTA_TOYS, "Juguetes"),
            (RUTA_VIDEOGAMES, "Videojuegos"),
            (RUTA_MUSIC, "Discos"),
            (RUTA_INSTRUMENTS, "Instrumentos Musicales")
        ]
        
        for ruta, nombre in datasets_a_procesar:
            if os.path.exists(ruta):
                print(f"\n   Encontrado: {ruta}")
                tipo = cargador.mapear_tipo_articulo(nombre)
                reviews_cargadas = cargador.cargar_dataset(ruta, tipo, limite=200)
                total_reviews += reviews_cargadas
                archivos_cargados = True
            else:
                print(f"\n   No encontrado: {ruta}")
        
        # Si no se cargo ningun archivo real, usar datos de ejemplo
        if not archivos_cargados:
            print("\n[4/4] No se encontraron archivos de datos reales")
            print("   Cargando datos de ejemplo...")
            cargador.cargar_datos_ejemplo()
        else:
            print(f"\n[4/4] Carga completada. Total reviews: {total_reviews}")
        
        # Verificar resultados finales
        print("VERIFICANDO RESULTADOS")
        
        with cargador.driver.session() as session:
            # Contar usuarios
            result = session.run("MATCH (u:Usuario) RETURN COUNT(u) AS total")
            total_usuarios = result.single()["total"]
            
            # Contar articulos
            result = session.run("MATCH (a:Articulo) RETURN COUNT(a) AS total")
            total_articulos = result.single()["total"]
            
            # Contar reviews (relaciones)
            result = session.run("MATCH ()-[r:REVIEW]->() RETURN COUNT(r) AS total")
            total_relaciones = result.single()["total"]
            
            # Verificar multiples reseñas
            result = session.run("""
                MATCH (u:Usuario)-[r:REVIEW]->(a:Articulo)
                RETURN u.id AS usuario, a.id AS articulo, COUNT(r) AS num_reviews
                ORDER BY num_reviews DESC
                LIMIT 10
            """)
            multiples = list(result)
            
            # Contar cuantos usuarios tienen multiples reseñas
            result = session.run("""
                MATCH (u:Usuario)-[r:REVIEW]->(a:Articulo)
                WITH u, a, COUNT(r) AS num_reviews
                WHERE num_reviews > 1
                RETURN COUNT(DISTINCT u) AS usuarios_con_multiples
            """)
            usuarios_multiples = result.single()["usuarios_con_multiples"]
        
        print(f"\nESTADISTICAS FINALES:")
        print(f"   - Usuarios: {total_usuarios}")
        print(f"   - Articulos: {total_articulos}")
        print(f"   - Reviews (relaciones): {total_relaciones}")
        print(f"   - Usuarios con multiples reseñas al mismo articulo: {usuarios_multiples}")
        
        if multiples:
            print("\nEJEMPLOS DE MULTIPLES RESEÑAS:")
            for row in multiples:
                if row["num_reviews"] > 1:
                    print(f"   - Usuario {row['usuario']} reseño {row['articulo']} {row['num_reviews']} veces")
        
        print("CARGA COMPLETADA EXITOSAMENTE")
        
        print("\nPara verificar en Neo4j Browser (http://localhost:7474):")
        print("   MATCH (n) RETURN n LIMIT 50")
        print("   MATCH (u:Usuario)-[r:REVIEW]->(a:Articulo) RETURN u, r, a LIMIT 25")
        print("   MATCH (u:Usuario)-[r:REVIEW]->(a:Articulo)")
        print("   RETURN u.id, a.id, COUNT(r) as veces")
        print("   ORDER BY veces DESC LIMIT 10")
        
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cargador.close()
        print("\nConexion con Neo4J cerrada")


if __name__ == "__main__":
    main()