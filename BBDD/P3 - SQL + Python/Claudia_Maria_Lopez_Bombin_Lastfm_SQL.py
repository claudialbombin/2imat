import pymysql
from pymysql import Error
from datetime import datetime
import os

# ================= CONFIGURACIÓN (EDITAR ESTO) =================
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "Carlota.22"  
MYSQL_DATABASE = "Lastfm"

# Rutas de los archivos TSV (ASUMIENDO QUE ESTÁN EN LA MISMA CARPETA)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
USER_PROFILE_PATH = os.path.join(CURRENT_DIR, "userid-profile.tsv")
LISTENS_PATH = os.path.join(CURRENT_DIR, "userid-timestamp-artid-artname-traid-traname.tsv")

# Número máximo de escuchas a cargar (1 millón)
MAX_LISTENS = 1000000
# ==============================================================

def create_connection(use_database=True):
    """Crear conexión a MySQL"""
    try:
        # Configuración de conexión
        config = {
            'host': MYSQL_HOST,
            'user': MYSQL_USER,
            'password': MYSQL_PASSWORD,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        
        # Solo añadir database si se especifica
        if use_database:
            config['database'] = MYSQL_DATABASE
            
        # Intentar con socket para macOS
        try:
            connection = pymysql.connect(**config, unix_socket='/tmp/mysql.sock')
            #print("Conexión establecida (con socket)")
        except:
            # Intentar sin socket
            connection = pymysql.connect(**config)
            #print("Conexión establecida (sin socket)")
        
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def create_database_and_tables():
    """Crear base de datos y tablas"""
    # Primero conexión SIN base de datos (para crearla)
    connection = create_connection(use_database=False)
    if not connection:
        return None
    
    cursor = connection.cursor()
    
    try:
        # Crear base de datos
        cursor.execute(f"DROP DATABASE IF EXISTS {MYSQL_DATABASE}")
        cursor.execute(f"CREATE DATABASE {MYSQL_DATABASE}")
        print(f"Base de datos '{MYSQL_DATABASE}' creada")
        
        # Ahora seleccionar la base de datos
        cursor.execute(f"USE {MYSQL_DATABASE}")
        
        # Crear tablas
        tables = [
            """
            CREATE TABLE IF NOT EXISTS artistas (
                id_artista INT AUTO_INCREMENT PRIMARY KEY,
                id_lastfm_artista VARCHAR(250),
                nombre_artista VARCHAR(250),
                INDEX idx_lastfm_artista (id_lastfm_artista)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INT AUTO_INCREMENT PRIMARY KEY,
                id_lastfm_usuario VARCHAR(250),
                genero VARCHAR(50),
                edad INT,
                pais VARCHAR(100),
                fecha_registro DATE,
                INDEX idx_lastfm_usuario (id_lastfm_usuario)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS canciones (
                id_cancion INT AUTO_INCREMENT PRIMARY KEY,
                id_lastfm_cancion VARCHAR(250),
                nombre_cancion VARCHAR(250),
                id_artista INT,
                FOREIGN KEY (id_artista) REFERENCES artistas(id_artista),
                INDEX idx_lastfm_cancion (id_lastfm_cancion)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS escuchas (
                id_escucha INT AUTO_INCREMENT PRIMARY KEY,
                id_usuario INT,
                id_cancion INT,
                fecha_hora DATETIME,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
                FOREIGN KEY (id_cancion) REFERENCES canciones(id_cancion),
                INDEX idx_fecha_hora (fecha_hora),
                INDEX idx_usuario_cancion (id_usuario, id_cancion)
            )
            """
        ]
        
        for i, table_sql in enumerate(tables, 1):
            cursor.execute(table_sql)
            #print(f"Tabla {i}/4 creada")
        
        connection.commit()
        print("Todas las tablas creadas correctamente")
        
        # Ahora crear una conexión con la base de datos
        cursor.close()
        connection.close()
        
        # Devolver una nueva conexión con la base de datos seleccionada
        return create_connection(use_database=True)
        
    except Error as e:
        print(f"Error creando base de datos: {e}")
        connection.rollback()
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.open:
            connection.close()

def load_user_profiles(connection):
    """Cargar datos de usuarios"""
    cursor = connection.cursor()
    
    try:
        with open(USER_PROFILE_PATH, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"ERROR: No se encuentra {USER_PROFILE_PATH}")
        return {}
    
    user_counter = 1
    user_map = {}
    
    #print(f"Procesando {len(lines)} perfiles de usuario...")
    
    for line_num, line in enumerate(lines, 1):
        line = line.replace('\r', '').replace('\n', '')
        
        if not line.strip():
            continue
            
        parts = line.strip().split('\t')
        
        if len(parts) >= 5:
            user_id = parts[0].strip()
            gender = parts[1].strip() if len(parts) > 1 and parts[1].lower() != 'null' else None
            age_str = parts[2].strip() if len(parts) > 2 else ''
            country = parts[3].strip() if len(parts) > 3 and parts[3].lower() != 'null' else None
            signup_str = parts[4].strip() if len(parts) > 4 else ''
            
            # Convertir edad
            age = 0
            if age_str and age_str.isdigit():
                age = int(age_str)
            
            # Convertir fecha de registro
            signup_date = None
            if signup_str and signup_str.lower() != 'null':
                try:
                    signup_date = datetime.strptime(signup_str, '%b %d, %Y').date()
                except ValueError:
                    try:
                        signup_date = datetime.strptime(signup_str, '%Y-%m-%d').date()
                    except:
                        signup_date = None
            
            # Insertar usuario
            try:
                sql = """
                INSERT INTO usuarios (id_usuario, id_lastfm_usuario, genero, edad, pais, fecha_registro)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (user_counter, user_id, gender, age, country, signup_date))
                user_map[user_id] = user_counter
                user_counter += 1
                
                # Mostrar progreso
                if user_counter % 100 == 0:
                    connection.commit()
                    #print(f"   Usuarios insertados: {user_counter-1}")
                    
            except Error as e:
                # Solo mostrar error si no es de usuario duplicado
                if "Duplicate entry" not in str(e):
                    print(f"Error en usuario {user_id}: {e}")
    
    connection.commit()
    cursor.close()
    print(f"Usuarios cargados: {user_counter - 1}")
    return user_map

def load_listens(connection, user_map):
    """Cargar escuchas"""
    cursor = connection.cursor()
    
    artist_map = {}
    song_map = {}
    artist_counter = 1
    song_counter = 1
    listen_counter = 0
    
    try:
        file_size = os.path.getsize(LISTENS_PATH)
        print(f"Procesando archivo de {file_size/1024/1024:.2f} MB...")
        
        with open(LISTENS_PATH, 'r', encoding='utf-8', errors='ignore') as file:
            for line_num, line in enumerate(file, 1):
                if listen_counter >= MAX_LISTENS:
                    print(f"Límite de {MAX_LISTENS} escuchas alcanzado")
                    break
                
                line = line.replace('\r', '').replace('\n', '')
                
                if not line.strip():
                    continue
                    
                parts = line.strip().split('\t')
                
                if len(parts) >= 6:
                    user_id = parts[0].strip()
                    timestamp_str = parts[1].strip()
                    artist_id = parts[2].strip()
                    artist_name = parts[3].strip()
                    song_id = parts[4].strip()
                    song_name = parts[5].strip()
                    
                    # Solo procesar si song_id no está vacío
                    if not song_id or song_id == '':
                        continue
                    
                    # Verificar si usuario existe
                    if user_id not in user_map:
                        # Crear usuario básico si no existe
                        try:
                            # Obtener el siguiente ID de usuario
                            cursor.execute("SELECT COALESCE(MAX(id_usuario), 0) + 1 as next_id FROM usuarios")
                            result = cursor.fetchone()
                            next_id = result['next_id'] if isinstance(result, dict) else result[0]
                            
                            sql_user = """
                            INSERT INTO usuarios (id_usuario, id_lastfm_usuario)
                            VALUES (%s, %s)
                            """
                            cursor.execute(sql_user, (next_id, user_id))
                            user_map[user_id] = next_id
                        except Error as e:
                            if "Duplicate entry" not in str(e):
                                continue
                    
                    # Convertir timestamp
                    try:
                        listen_date = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ')
                    except ValueError:
                        try:
                            listen_date = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        except:
                            continue
                    
                    # Gestionar artista
                    if artist_id not in artist_map:
                        try:
                            sql_artist = """
                            INSERT INTO artistas (id_artista, id_lastfm_artista, nombre_artista)
                            VALUES (%s, %s, %s)
                            """
                            cursor.execute(sql_artist, (artist_counter, artist_id, artist_name))
                            artist_map[artist_id] = artist_counter
                            artist_counter += 1
                        except Error as e:
                            if "Duplicate entry" not in str(e):
                                print(f"Error artista {artist_id}: {e}")
                            continue
                    
                    current_artist_id = artist_map[artist_id]
                    
                    # Gestionar canción
                    song_key = (song_id, current_artist_id)
                    if song_key not in song_map:
                        try:
                            sql_song = """
                            INSERT INTO canciones (id_cancion, id_lastfm_cancion, nombre_cancion, id_artista)
                            VALUES (%s, %s, %s, %s)
                            """
                            cursor.execute(sql_song, (song_counter, song_id, song_name, current_artist_id))
                            song_map[song_key] = song_counter
                            song_counter += 1
                        except Error as e:
                            if "Duplicate entry" not in str(e):
                                print(f"Error canción {song_id}: {e}")
                            continue
                    
                    current_song_id = song_map[song_key]
                    
                    # Insertar escucha
                    try:
                        sql_listen = """
                        INSERT INTO escuchas (id_usuario, id_cancion, fecha_hora)
                        VALUES (%s, %s, %s)
                        """
                        cursor.execute(sql_listen, (user_map[user_id], current_song_id, listen_date))
                        listen_counter += 1
                    except Error as e:
                        if "Duplicate entry" not in str(e):
                            print(f"Error escucha: {e}")
                    
                    # Commit periódico
                    if listen_counter % 10000 == 0:
                        connection.commit()
                        print(f"   Escuchas procesadas: {listen_counter:,}")
                        
    except FileNotFoundError:
        print(f"ERROR: No se encuentra {LISTENS_PATH}")
        return 0
    except Exception as e:
        print(f"Error inesperado: {e}")
        return 0
    
    connection.commit()
    cursor.close()
    
    print(f"\nRESUMEN DE CARGA:")
    print(f"   Total escuchas: {listen_counter:,}")
    print(f"   Total artistas: {artist_counter - 1:,}")
    print(f"   Total canciones: {song_counter - 1:,}")
    
    return listen_counter

def main():
    """Función principal"""
    print("============================================")
    print("    CARGA DE DATOS LAST.FM EN MySQL        ")
    print("============================================")
    
    # Verificar archivos
    if not os.path.exists(USER_PROFILE_PATH):
        print(f"No encontrado: {USER_PROFILE_PATH}")
        return
    if not os.path.exists(LISTENS_PATH):
        print(f"No encontrado: {LISTENS_PATH}")
        return
    
    print(f"Usuarios: {USER_PROFILE_PATH}")
    print(f"Escuchas: {LISTENS_PATH}")
    print(f"Límite: {MAX_LISTENS:,} escuchas\n")
    
    # 1. Crear base de datos y tablas
    print(" Creando base de datos y tablas...")
    connection = create_database_and_tables()
    if not connection:
        print("Fallo al crear base de datos")
        return
    
    try:
        # 2. Cargar usuarios
        print("\nCargando usuarios...")
        user_map = load_user_profiles(connection)
        
        if not user_map:
            print("No se cargaron usuarios")
            return
        
        # 3. Cargar escuchas
        print("\nCargando escuchas...")
        total_listens = load_listens(connection, user_map)
        
        print("\n============================================")
        print("          CARGA COMPLETADA               ")
        print("============================================")
        
        # Mostrar estadísticas finales
        cursor = connection.cursor()
        
        print("\nESTADÍSTICAS FINALES:")
        
        queries = [
            ("Usuarios", "SELECT COUNT(*) as count FROM usuarios"),
            ("Artistas", "SELECT COUNT(*) as count FROM artistas"),
            ("Canciones", "SELECT COUNT(*) as count FROM canciones"),
            ("Escuchas", "SELECT COUNT(*) as count FROM escuchas"),
        ]
        
        for label, sql in queries:
            try:
                cursor.execute(sql)
                result = cursor.fetchone()
                count = result['count'] if isinstance(result, dict) else result[0]
                print(f"   {label}: {count:,}")
            except Error as e:
                print(f"   {label}: Error - {e}")
        
        cursor.close()
        
        print("\nBase de datos lista para consultas!")
        print("Ejecuta: mysql -u root -pCarlota.22 --socket=/tmp/mysql.sock")
        print("   USE Lastfm;")
        print("   -- Y luego tus consultas SQL")
        
    except Error as e:
        print(f"\nError durante la carga: {e}")
    finally:
        if connection and connection.open:
            connection.close()
            print("\nConexión cerrada")

if __name__ == "__main__":
    main()