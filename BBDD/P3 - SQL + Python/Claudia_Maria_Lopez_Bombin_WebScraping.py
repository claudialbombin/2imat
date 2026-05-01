"""
Web Scraping - Roland Garros Winners
Alumna: Claudia Maria Lopez Bombin
"""

import os
import csv
from datetime import datetime
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import pymysql
from pymysql import Error

# ================= CONFIGURACION =================
# Credenciales MySQL (mismas que en la practica principal)
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "Carlota.22"
MYSQL_DATABASE = "RolandGarros"

# URL de la pagina con la tabla de ganadores (Wikipedia)
URL = "https://en.wikipedia.org/wiki/List_of_French_Open_men%27s_singles_champions"

# Archivo CSV temporal
CSV_FILENAME = "roland_garros_winners.csv"
# =================================================

def scrape_roland_garros():
    """
    Extrae la tabla de ganadores de Roland Garros desde Wikipedia
    """
    print("Iniciando Web Scraping de Roland Garros...")
    
    try:
        # 1. Abrir conexion a la URL
        print("Conectando a:", URL)
        response = urlopen(URL)
        html = response.read()
        response.close()
        print("Pagina web descargada correctamente")
        
        # 2. Crear objeto BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        print("HTML parseado con BeautifulSoup")
        
        # 3. Encontrar todas las tablas
        tables = soup.find_all('table', class_='wikitable')
        print("Encontradas", len(tables), "tablas con clase 'wikitable'")
        
        # La tabla de ganadores suele ser la primera
        if len(tables) < 1:
            print("No se encontraron tablas")
            return None
        
        target_table = tables[0]
        print("Tabla objetivo identificada")
        
        # 4. Extraer datos de la tabla
        rows = target_table.find_all('tr')
        print("Filas encontradas:", len(rows))
        
        data = []
        
        for i, row in enumerate(rows):
            # Obtener celdas (th para cabeceras, td para datos)
            cells = row.find_all(['th', 'td'])
            
            if not cells:
                continue
            
            # Extraer texto de cada celda y limpiar
            row_data = []
            for cell in cells:
                # Eliminar notas al pie [1], [2], etc.
                text = cell.get_text().strip()
                # Limpiar referencias
                text = text.split('[')[0] if '[' in text else text
                # Limpiar saltos de linea
                text = ' '.join(text.split())
                row_data.append(text)
            
            # Identificar si es cabecera o dato
            if i == 0 or all(cell.name == 'th' for cell in cells):
                row_data = ['cabecera'] + row_data
            else:
                row_data = ['dato'] + row_data
            
            data.append(row_data)
            print("   Fila", i, ":", len(row_data)-1, "celdas")
        
        return data
        
    except HTTPError as e:
        print("Error HTTP:", e.code, "-", e.reason)
        return None
    except URLError as e:
        print("Error de URL:", e.reason)
        return None
    except Exception as e:
        print("Error inesperado:", e)
        return None

def save_to_csv(data, filename):
    """
    Guarda los datos extraidos en un archivo CSV
    """
    if not data:
        print("No hay datos para guardar")
        return False
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Escribir cada fila
            rows_written = 0
            for row in data:
                # Quitar el marcador de cabecera/dato
                writer.writerow(row[1:])
                rows_written += 1
            
        print("Datos guardados en", filename)
        print("Total filas:", rows_written)
        
        # Mostrar primeras filas como preview
        print("\nPreview de los datos:")
        for i, row in enumerate(data[:5]):
            tipo = "CABECERA" if row[0] == 'cabecera' else "DATO"
            print("   ", tipo, ":", row[1:3])
        
        return True
        
    except Exception as e:
        print("Error guardando CSV:", e)
        return False

def create_database_and_table():
    """
    Crea la base de datos y tabla para los ganadores
    """
    try:
        # Conectar sin base de datos
        connection = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            unix_socket='/tmp/mysql.sock'
        )
        
        cursor = connection.cursor()
        
        # Crear base de datos
        cursor.execute("DROP DATABASE IF EXISTS " + MYSQL_DATABASE)
        cursor.execute("CREATE DATABASE " + MYSQL_DATABASE)
        cursor.execute("USE " + MYSQL_DATABASE)
        print("Base de datos '" + MYSQL_DATABASE + "' creada")
        
        # Crear tabla para ganadores
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS roland_garros_winners (
            id INT AUTO_INCREMENT PRIMARY KEY,
            year INT,
            champion VARCHAR(255),
            runner_up VARCHAR(255),
            score VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_sql)
        print("Tabla 'roland_garros_winners' creada")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print("Error creando base de datos:", e)
        return False

def load_csv_to_mysql():
    """
    Carga los datos del CSV en MySQL
    """
    if not os.path.exists(CSV_FILENAME):
        print("No se encuentra el archivo", CSV_FILENAME)
        return False
    
    try:
        # Conectar a MySQL con la base de datos
        connection = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            unix_socket='/tmp/mysql.sock'
        )
        
        cursor = connection.cursor()
        
        # Limpiar tabla
        cursor.execute("TRUNCATE TABLE roland_garros_winners")
        
        # Leer CSV y cargar datos
        with open(CSV_FILENAME, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            # Saltar cabeceras
            headers = next(reader)
            print("Columnas detectadas:", headers)
            
            # Insertar datos
            insert_count = 0
            for row in reader:
                if len(row) >= 3:
                    try:
                        # Intentar convertir año a entero
                        year = int(row[0]) if row[0].isdigit() else None
                        
                        sql = """
                        INSERT INTO roland_garros_winners (year, champion, runner_up, score)
                        VALUES (%s, %s, %s, %s)
                        """
                        cursor.execute(sql, (year, row[1], row[2], row[3] if len(row) > 3 else None))
                        insert_count += 1
                        
                    except (ValueError, IndexError) as e:
                        print("Error procesando fila", row, ":", e)
            
            connection.commit()
            print(insert_count, "registros insertados en MySQL")
        
        # Verificar carga
        cursor.execute("SELECT COUNT(*) as total FROM roland_garros_winners")
        result = cursor.fetchone()
        total = result['total'] if result else 0
        
        # Mostrar algunos registros
        cursor.execute("SELECT * FROM roland_garros_winners LIMIT 5")
        samples = cursor.fetchall()
        
        print("\nTotal en BD:", total, "registros")
        print("Primeros 5 registros:")
        for sample in samples:
            print("   " + str(sample['year']) + ": " + sample['champion'] + " vs " + sample['runner_up'] + " - " + str(sample['score']))
        
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print("Error cargando datos en MySQL:", e)
        return False
    except Exception as e:
        print("Error inesperado:", e)
        return False

def main():
    """
    Funcion principal
    """
    print("============================================")
    print("WEB SCRAPING - ROLAND GARROS WINNERS")
    print("============================================\n")
    
    # PASO 1: Scraping
    print("FASE 1: Extraccion de datos")
    data = scrape_roland_garros()
    if not data:
        print("No se pudieron extraer datos")
        return
    
    # PASO 2: Guardar en CSV
    print("\nFASE 2: Guardando en CSV")
    if not save_to_csv(data, CSV_FILENAME):
        print("Error guardando CSV")
        return
    
    # PASO 3: Crear BD y tabla
    print("\nFASE 3: Creando base de datos")
    if not create_database_and_table():
        print("Error creando base de datos")
        return
    
    # PASO 4: Cargar en MySQL
    print("\nFASE 4: Cargando datos en MySQL")
    if not load_csv_to_mysql():
        print("Error cargando datos")
        return
    
    print("\n============================================")
    print("WEB SCRAPING COMPLETADO CON EXITO")
    print("============================================")
    print("\nArchivos generados:")
    print("   -", CSV_FILENAME)
    print("\nBase de datos:", MYSQL_DATABASE)
    print("   Tabla: roland_garros_winners")
    print("\nPara verificar:")
    print("   mysql -u root -pCarlota.22 --socket=/tmp/mysql.sock")
    print("   USE RolandGarros;")
    print("   SELECT * FROM roland_garros_winners LIMIT 10;")

if __name__ == "__main__":
    main()