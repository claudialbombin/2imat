import json
import mysql.connector
from pymongo import MongoClient
import time

# Configuración de rutas y credenciales (MODIFICAR AQUÍ)
FILE_PATH = "Video_Games_5.json"  # Cambiar por la ruta del archivo

# Configuración MongoDB
MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "Reviews" 
MONGODB_COLLECTION = "Videogames"

# Configuración MySQL
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DATABASE = "reviews_db"


def inserta_mongodb():
    """Inserta los datos del archivo JSON en MongoDB"""
    try:
        # Conexión a MongoDB
        client = MongoClient(MONGODB_HOST, MONGODB_PORT)
        db = client[MONGODB_DB]
        collection = db[MONGODB_COLLECTION]
        
        print("Insertando datos en MongoDB...")
        
        # Leer archivo línea por línea
        documents = []
        with open(FILE_PATH, 'r', encoding='utf-8') as file:
            for i, line in enumerate(file):
                if line.strip():
                    review = json.loads(line)
                    documents.append(review)
                    
                    # Insertar en lotes de 1000 documentos para mejor rendimiento
                    if len(documents) >= 1000:
                        collection.insert_many(documents)
                        documents = []
                        print(f"Insertados {i+1} documentos...")
        
        # Insertar documentos restantes
        if documents:
            collection.insert_many(documents)
        
        print(f"Total de documentos insertados en MongoDB: {collection.count_documents({})}")
        client.close()
        
    except Exception as e:
        print(f"Error en MongoDB: {e}")


def inserta_datos_mysql():
    """Inserta los datos en MySQL"""
    try:
        # Conexión a MySQL
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        
        cursor = connection.cursor()
        
        # Crear tabla si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videogames (
                id INT AUTO_INCREMENT PRIMARY KEY,
                reviewerID VARCHAR(255),
                asin VARCHAR(255),
                reviewerName TEXT,
                helpful_yes INT,
                helpful_total INT,
                reviewText TEXT,
                overall INT,
                summary TEXT,
                unixReviewTime BIGINT,
                reviewTime VARCHAR(100)
            )
        """)
        
        print("Insertando datos en MySQL...")
        
        # Leer archivo línea por línea
        with open(FILE_PATH, 'r', encoding='utf-8') as file:
            insert_query = """
                INSERT INTO videogames 
                (reviewerID, asin, reviewerName, helpful_yes, helpful_total, 
                 reviewText, overall, summary, unixReviewTime, reviewTime) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            batch = []
            for i, line in enumerate(file):
                if line.strip():
                    review = json.loads(line)
                    
                    # Procesar campo helpful
                    helpful_yes = review['helpful'][0] if review.get('helpful') else 0
                    helpful_total = review['helpful'][1] if review.get('helpful') else 0
                    
                    # Preparar valores
                    values = (
                        review.get('reviewerID', ''),
                        review.get('asin', ''),
                        review.get('reviewerName', ''),
                        helpful_yes,
                        helpful_total,
                        review.get('reviewText', ''),
                        review.get('overall', 0),
                        review.get('summary', ''),
                        review.get('unixReviewTime', 0),
                        review.get('reviewTime', '')
                    )
                    batch.append(values)
                    
                    # Insertar en lotes de 1000 registros
                    if len(batch) >= 1000:
                        cursor.executemany(insert_query, batch)
                        connection.commit()
                        batch = []
                        print(f"Insertados {i+1} registros...")
            
            # Insertar registros restantes
            if batch:
                cursor.executemany(insert_query, batch)
                connection.commit()
        
        # Obtener total de registros
        cursor.execute("SELECT COUNT(*) FROM videogames")
        total = cursor.fetchone()[0]
        print(f"Total de registros insertados en MySQL: {total}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error en MySQL: {e}")


if __name__ == "__main__":
    print("=== Carga de datos para Benchmarking ===\n")
    
    start_time = time.time()
    inserta_mongodb()
    mongo_time = time.time() - start_time
    print(f"Tiempo de carga MongoDB: {mongo_time:.2f} segundos\n")
    
    start_time = time.time()
    inserta_datos_mysql()
    mysql_time = time.time() - start_time
    print(f"Tiempo de carga MySQL: {mysql_time:.2f} segundos")