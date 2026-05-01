# ============================================================
# carga_emails.py
# Script para cargar los datos de emails en Neo4J
#
# Archivos necesarios:
#   - email-Eu-core1000.txt         (relaciones de emails)
#   - email-Eu-core-department-labels.txt  (usuario -> departamento)
# ============================================================

from neo4j import GraphDatabase

# --- Configuración de conexión ---
# Cambia estos valores si tu instancia de Neo4J tiene otra dirección o credenciales
URI = "bolt://localhost:7687"
USUARIO = "neo4j"
CONTRASENA = "password"  # pon aqui tu contraseña real


def leer_departamentos(ruta_fichero):
    """
    Lee el fichero de etiquetas de departamento.
    Devuelve un diccionario { id_usuario: id_departamento }.
    Cada línea tiene formato: <id_usuario> <id_departamento>
    """
    departamentos = {}
    with open(ruta_fichero, "r") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            partes = linea.split()
            id_usuario = int(partes[0])
            id_dept = int(partes[1])
            departamentos[id_usuario] = id_dept
    return departamentos


def leer_emails(ruta_fichero):
    """
    Lee el fichero de emails.
    Devuelve una lista de tuplas (emisor, receptor).
    Cada línea tiene formato: <id_emisor> <id_receptor>
    """
    emails = []
    with open(ruta_fichero, "r") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            partes = linea.split()
            emisor = int(partes[0])
            receptor = int(partes[1])
            emails.append((emisor, receptor))
    return emails


def borrar_todo(sesion):
    """
    Borra todos los nodos y relaciones de la base de datos.
    Esto limpia tanto los datos de la práctica anterior (películas)
    como cualquier dato previo.
    """
    print("Borrando todos los datos existentes...")
    sesion.run("MATCH (n) DETACH DELETE n")
    print("Base de datos limpia.")


def crear_usuarios_y_departamentos(sesion, departamentos):
    """
    Crea los nodos de Usuario y Departamento, y las relaciones
    PERTENECE_A entre ellos.
    Usamos MERGE para no crear duplicados si el script se ejecuta varias veces.
    """
    print(f"Creando {len(departamentos)} usuarios y sus departamentos...")

    # Creamos todos los nodos de departamento primero (sin repetición)
    ids_departamentos = set(departamentos.values())
    for id_dept in ids_departamentos:
        sesion.run(
            "MERGE (d:Departamento {id_departamento: $id_dept})",
            id_dept=id_dept
        )

    # Ahora creamos cada usuario y lo enlazamos con su departamento
    for id_usuario, id_dept in departamentos.items():
        sesion.run(
            """
            MERGE (u:Usuario {id_usuario: $id_usuario})
            WITH u
            MATCH (d:Departamento {id_departamento: $id_dept})
            MERGE (u)-[:PERTENECE_A]->(d)
            """,
            id_usuario=id_usuario,
            id_dept=id_dept
        )

    print("Usuarios y departamentos creados.")


def crear_relaciones_email(sesion, emails):
    """
    Crea las relaciones ENVIA_MAIL entre usuarios.
    Si un usuario emisor o receptor no existe todavía (porque no
    aparecía en el fichero de departamentos), lo creamos igualmente.
    """
    print(f"Creando {len(emails)} relaciones de email...")

    # Lo hacemos en lotes para no sobrecargar la memoria
    tamaño_lote = 500
    for i in range(0, len(emails), tamaño_lote):
        lote = emails[i:i + tamaño_lote]

        # Convertimos el lote en una lista de dicts para pasarlo a Cypher
        datos = [{"emisor": e, "receptor": r} for e, r in lote]

        sesion.run(
            """
            UNWIND $datos AS fila
            MERGE (u1:Usuario {id_usuario: fila.emisor})
            MERGE (u2:Usuario {id_usuario: fila.receptor})
            CREATE (u1)-[:ENVIA_MAIL]->(u2)
            """,
            datos=datos
        )

        print(f"  Procesadas {min(i + tamaño_lote, len(emails))} / {len(emails)} relaciones...")

    print("Relaciones de email creadas.")


def main():
    # Rutas a los ficheros de datos
    # Si los tienes en otra carpeta, cambia las rutas
    ruta_departamentos = "email-Eu-core-department-labels.txt"
    ruta_emails = "email-Eu-core1000.txt"

    # Leemos los datos de los ficheros
    print("Leyendo fichero de departamentos...")
    departamentos = leer_departamentos(ruta_departamentos)
    print(f"  {len(departamentos)} usuarios leídos.")

    print("Leyendo fichero de emails...")
    emails = leer_emails(ruta_emails)
    print(f"  {len(emails)} relaciones de email leídas.")

    # Conectamos con Neo4J y cargamos los datos
    print(f"\nConectando a Neo4J en {URI}...")
    driver = GraphDatabase.driver(URI, auth=(USUARIO, CONTRASENA))

    with driver.session() as sesion:
        # Paso 1: borrar todo lo que haya (datos de la parte anterior también)
        borrar_todo(sesion)

        # Paso 2: crear usuarios y departamentos
        crear_usuarios_y_departamentos(sesion, departamentos)

        # Paso 3: crear relaciones de email entre usuarios
        crear_relaciones_email(sesion, emails)

    driver.close()
    print("\n¡Datos cargados correctamente en Neo4J!")
    print("Puedes ejecutar ':config initialNodeDisplay: 2000' en Neo4J para ver más nodos.")


if __name__ == "__main__":
    main()


# ============================================================
# QUERIES OPCIONALES - para ejecutar en Neo4J Browser
# ============================================================

# Opcional 1:
# Nodos que solo tienen UNA relación ENVIA_MAIL y es consigo mismos.
#
# MATCH (u:Usuario)-[r:ENVIA_MAIL]->(u)
# WHERE NOT EXISTS {
#     MATCH (u)-[:ENVIA_MAIL]->(otro:Usuario)
#     WHERE otro <> u
# }
# AND NOT EXISTS {
#     MATCH (otro2:Usuario)-[:ENVIA_MAIL]->(u)
#     WHERE otro2 <> u
# }
# RETURN u

# Opcional 2:
# Número de usuarios por departamento.
#
# MATCH (u:Usuario)-[:PERTENECE_A]->(d:Departamento)
# RETURN d.id_departamento AS departamento, COUNT(u) AS num_usuarios
# ORDER BY num_usuarios DESC

# Opcional 3:
# Número de mensajes recibidos por cada usuario, ordenado desc.
#
# MATCH (emisor:Usuario)-[:ENVIA_MAIL]->(receptor:Usuario)
# RETURN receptor.id_usuario AS usuario, COUNT(*) AS mensajes_recibidos
# ORDER BY mensajes_recibidos DESC
