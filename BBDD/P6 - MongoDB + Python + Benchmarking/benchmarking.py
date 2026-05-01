import mysql.connector
from pymongo import MongoClient
import time
import matplotlib.pyplot as plt
import numpy as np

# Configuración de credenciales (MODIFICAR AQUÍ)
MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "Reviews"
MONGODB_COLLECTION = "Videogames"

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DATABASE = "reviews_db"


def get_mongo_connection():
    """Obtiene conexión a MongoDB"""
    client = MongoClient(MONGODB_HOST, MONGODB_PORT)
    db = client[MONGODB_DB]
    return db[MONGODB_COLLECTION]


def get_mysql_connection():
    """Obtiene conexión a MySQL"""
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )


def Benchmark_1():
    """Encontrar los usuarios distintos que han hecho alguna review"""
    print("\n=== Benchmark 1: Usuarios distintos ===")
    
    # MySQL
    mysql_times = []
    for i in range(5):
        start = time.time()
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT reviewerID) FROM videogames")
        count = cursor.fetchone()[0]
        mysql_times.append(time.time() - start)
        cursor.close()
        conn.close()
    
    avg_mysql = sum(mysql_times) / len(mysql_times)
    print(f"MySQL - Registros: {count}")
    print(f"Tiempo MySQL (x5): {avg_mysql:.6f} segundos")
    
    # MongoDB
    mongo_times = []
    for i in range(5):
        start = time.time()
        collection = get_mongo_connection()
        distinct_users = collection.distinct("reviewerID")
        mongo_times.append(time.time() - start)
    
    avg_mongo = sum(mongo_times) / len(mongo_times)
    print(f"MongoDB - Registros: {len(distinct_users)}")
    print(f"Tiempo MongoDB (x5): {avg_mongo:.6f} segundos")
    
    return avg_mysql, avg_mongo


def Benchmark_2():
    """Por cada usuario, obtener la media de notas (overall) y su número total de reviews"""
    print("\n=== Benchmark 2: Media de overall por cada usuario ===")
    
    # MySQL
    mysql_times = []
    for i in range(5):
        start = time.time()
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT reviewerID, AVG(overall) as avg_rating, COUNT(*) as review_count 
            FROM videogames 
            GROUP BY reviewerID
        """)
        results = cursor.fetchall()
        mysql_times.append(time.time() - start)
        cursor.close()
        conn.close()
    
    avg_mysql = sum(mysql_times) / len(mysql_times)
    print(f"MySQL - Registros: {len(results)}")
    print(f"Tiempo MySQL (x5): {avg_mysql:.6f} segundos")
    
    # MongoDB
    mongo_times = []
    for i in range(5):
        start = time.time()
        collection = get_mongo_connection()
        pipeline = [
            {"$group": {
                "_id": "$reviewerID",
                "avg_rating": {"$avg": "$overall"},
                "review_count": {"$sum": 1}
            }}
        ]
        results = list(collection.aggregate(pipeline))
        mongo_times.append(time.time() - start)
    
    avg_mongo = sum(mongo_times) / len(mongo_times)
    print(f"MongoDB - Registros: {len(results)}")
    print(f"Tiempo MongoDB (x5): {avg_mongo:.6f} segundos")
    
    return avg_mysql, avg_mongo


def Benchmark_3():
    """Encontrar todas las reviews que tengan en el campo 'summary' la palabra 'great'"""
    print("\n=== Benchmark 3: Encontrar la palabra 'great' en summary ===")
    
    # MySQL (sin índices)
    mysql_times = []
    for i in range(5):
        start = time.time()
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM videogames 
            WHERE LOWER(summary) LIKE '%great%'
        """)
        count = cursor.fetchone()[0]
        mysql_times.append(time.time() - start)
        cursor.close()
        conn.close()
    
    avg_mysql = sum(mysql_times) / len(mysql_times)
    print(f"MySQL - Registros: {count}")
    print(f"Tiempo MySQL (x5): {avg_mysql:.6f} segundos")
    
    # MongoDB (sin índices)
    mongo_times = []
    for i in range(5):
        start = time.time()
        collection = get_mongo_connection()
        count = collection.count_documents({
            "summary": {"$regex": "great", "$options": "i"}
        })
        mongo_times.append(time.time() - start)
    
    avg_mongo = sum(mongo_times) / len(mongo_times)
    print(f"MongoDB - Registros: {count}")
    print(f"Tiempo MongoDB (x5): {avg_mongo:.6f} segundos")
    
    return avg_mysql, avg_mongo


def Benchmark_4():
    """Mostrar el item/asin (solo 1) con la media más alta"""
    print("\n=== Benchmark 4: Item con la media más alta ===")
    
    # MySQL
    mysql_times = []
    for i in range(5):
        start = time.time()
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT asin, AVG(overall) as avg_rating 
            FROM videogames 
            GROUP BY asin 
            ORDER BY avg_rating DESC, asin ASC 
            LIMIT 1
        """)
        result = cursor.fetchone()
        mysql_times.append(time.time() - start)
        cursor.close()
        conn.close()
    
    avg_mysql = sum(mysql_times) / len(mysql_times)
    print(f"MySQL - Registros: {1 if result else 0}")
    if result:
        print(f"Item con mayor media: ASIN={result[0]}, Media={result[1]:.2f}")
    print(f"Tiempo MySQL (x5): {avg_mysql:.6f} segundos")
    
    # MongoDB
    mongo_times = []
    for i in range(5):
        start = time.time()
        collection = get_mongo_connection()
        pipeline = [
            {"$group": {
                "_id": "$asin",
                "avg_rating": {"$avg": "$overall"}
            }},
            {"$sort": {"avg_rating": -1, "_id": 1}},
            {"$limit": 1}
        ]
        result = list(collection.aggregate(pipeline))
        mongo_times.append(time.time() - start)
    
    avg_mongo = sum(mongo_times) / len(mongo_times)
    print(f"MongoDB - Registros: {len(result)}")
    if result:
        print(f"Item con mayor media: ASIN={result[0]['_id']}, Media={result[0]['avg_rating']:.2f}")
    print(f"Tiempo MongoDB (x5): {avg_mongo:.6f} segundos")
    
    return avg_mysql, avg_mongo


def Benchmark_5():
    """Misma consulta anterior pero solo para aquellos que tengan al menos 10 reviews"""
    print("\n=== Benchmark 5: Item con la media más alta (al menos 10 reviews) ===")
    
    # MySQL
    mysql_times = []
    for i in range(5):
        start = time.time()
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT asin, AVG(overall) as avg_rating, COUNT(*) as review_count 
            FROM videogames 
            GROUP BY asin 
            HAVING review_count >= 10 
            ORDER BY avg_rating DESC, asin ASC 
            LIMIT 1
        """)
        result = cursor.fetchone()
        mysql_times.append(time.time() - start)
        cursor.close()
        conn.close()
    
    avg_mysql = sum(mysql_times) / len(mysql_times)
    print(f"MySQL - Registros: {1 if result else 0}")
    if result:
        print(f"Item con mayor media: ASIN={result[0]}, Media={result[1]:.2f}, Reviews={result[2]}")
    print(f"Tiempo MySQL (x5): {avg_mysql:.6f} segundos")
    
    # MongoDB
    mongo_times = []
    for i in range(5):
        start = time.time()
        collection = get_mongo_connection()
        pipeline = [
            {"$group": {
                "_id": "$asin",
                "avg_rating": {"$avg": "$overall"},
                "review_count": {"$sum": 1}
            }},
            {"$match": {"review_count": {"$gte": 10}}},
            {"$sort": {"avg_rating": -1, "_id": 1}},
            {"$limit": 1}
        ]
        result = list(collection.aggregate(pipeline))
        mongo_times.append(time.time() - start)
    
    avg_mongo = sum(mongo_times) / len(mongo_times)
    print(f"MongoDB - Registros: {len(result)}")
    if result:
        print(f"Item con mayor media: ASIN={result[0]['_id']}, Media={result[0]['avg_rating']:.2f}, Reviews={result[0]['review_count']}")
    print(f"Tiempo MongoDB (x5): {avg_mongo:.6f} segundos")
    
    return avg_mysql, avg_mongo


def Benchmark_6():
    """Obtener el número de reviews totales que hay en función de la nota (overall) para unixReviewTime >= 1000000000"""
    print("\n=== Benchmark 6: Número de reviews por nota ===")
    
    # MySQL
    mysql_times = []
    for i in range(5):
        start = time.time()
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT overall, COUNT(*) as review_count 
            FROM videogames 
            WHERE unixReviewTime >= 1000000000 
            GROUP BY overall 
            ORDER BY review_count ASC
        """)
        results = cursor.fetchall()
        mysql_times.append(time.time() - start)
        cursor.close()
        conn.close()
    
    avg_mysql = sum(mysql_times) / len(mysql_times)
    print(f"MySQL - Registros: {len(results)}")
    print(f"Tiempo MySQL (x5): {avg_mysql:.6f} segundos")
    
    # MongoDB
    mongo_times = []
    for i in range(5):
        start = time.time()
        collection = get_mongo_connection()
        pipeline = [
            {"$match": {"unixReviewTime": {"$gte": 1000000000}}},
            {"$group": {
                "_id": "$overall",
                "review_count": {"$sum": 1}
            }},
            {"$sort": {"review_count": 1}}
        ]
        results = list(collection.aggregate(pipeline))
        mongo_times.append(time.time() - start)
    
    avg_mongo = sum(mongo_times) / len(mongo_times)
    print(f"MongoDB - Registros: {len(results)}")
    print(f"Tiempo MongoDB (x5): {avg_mongo:.6f} segundos")
    
    return avg_mysql, avg_mongo


def Benchmark_7():
    """Obtener el número de reviews que contienen la palabra RPG en summary o reviewText"""
    print("\n=== Benchmark 7: Texto de RPGs ===")
    
    # MySQL
    start = time.time()
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM videogames 
        WHERE LOWER(summary) LIKE '%rpg%' OR LOWER(reviewText) LIKE '%rpg%'
    """)
    count_mysql = cursor.fetchone()[0]
    mysql_time = time.time() - start
    cursor.close()
    conn.close()
    
    print(f"MySQL - Registros: {count_mysql}")
    print(f"Tiempo MySQL: {mysql_time:.6f} segundos")
    
    # MongoDB
    start = time.time()
    collection = get_mongo_connection()
    count_mongo = collection.count_documents({
        "$or": [
            {"summary": {"$regex": "rpg", "$options": "i"}},
            {"reviewText": {"$regex": "rpg", "$options": "i"}}
        ]
    })
    mongo_time = time.time() - start
    
    print(f"MongoDB - Registros: {count_mongo}")
    print(f"Tiempo MongoDB: {mongo_time:.6f} segundos")
    
    return mysql_time, mongo_time


def plot_results(times):
    """Genera gráfico de comparación de tiempos"""
    benchmarks = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7']
    mysql_times = [times[i][0] for i in range(7)]
    mongo_times = [times[i][1] for i in range(7)]
    
    x = np.arange(len(benchmarks))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    rects1 = ax.bar(x - width/2, mysql_times, width, label='MySQL', color='skyblue')
    rects2 = ax.bar(x + width/2, mongo_times, width, label='MongoDB', color='lightcoral')
    
    ax.set_xlabel('Benchmarks')
    ax.set_ylabel('Tiempo (segundos)')
    ax.set_title('Comparativa de tiempos: MySQL vs MongoDB')
    ax.set_xticks(x)
    ax.set_xticklabels(benchmarks)
    ax.legend()
    
    # Añadir valores en las barras
    ax.bar_label(rects1, padding=3, fmt='%.2f')
    ax.bar_label(rects2, padding=3, fmt='%.2f')
    
    plt.tight_layout()
    plt.savefig('benchmark_results.png', dpi=300)
    plt.show()
    print("\nGráfico guardado como 'benchmark_results.png'")


if __name__ == "__main__":

    print("Ejecutando consultas...")
    
    results = []
    
    results.append(Benchmark_1())

    
    results.append(Benchmark_2())

    
    results.append(Benchmark_3())

    
    results.append(Benchmark_4())

    
    results.append(Benchmark_5())

    
    results.append(Benchmark_6())

    
    results.append(Benchmark_7())

    
    # Generar gráfico (opcional)
    try:
        plot_results(results)
    except Exception as e:
        print(f"\nNo se pudo generar el gráfico: {e}")
    
