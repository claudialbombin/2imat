"""
=============================================================================
PROYECTO FINAL - BASES DE DATOS - NEO4J (VERSIÓN CORREGIDA)
=============================================================================
"""

from neo4j import GraphDatabase
import random
from itertools import combinations
import math
import os
from configuracion import (
    NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD,
    TOP_USUARIOS_SIMILITUD, NUM_ARTICULOS_ALEATORIOS, TOP_USUARIOS_NOMBRE
)


class Neo4jProyecto:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.similitudes_file = "similitudes_usuarios.txt"
    
    def close(self):
        self.driver.close()
    
    def limpiar_base_datos(self):
        """Elimina todos los nodos y relaciones de la base de datos"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Base de datos limpiada correctamente")
    
    def mostrar_instrucciones_visualizacion(self, seccion):
        """Muestra instrucciones para visualizar los grafos en Neo4j Browser"""
        print("INSTRUCCIONES PARA VISUALIZAR EL GRAFO EN NEO4J BROWSER")
        print("1. Abre tu navegador web y ve a: http://localhost:7474")
        print("2. Conéctate con las credenciales:")
        print(f"   - Usuario: {NEO4J_USER}")
        print(f"   - Contraseña: {NEO4J_PASSWORD}")
        print("3. En la línea de comandos de Neo4j Browser, ejecuta la siguiente consulta:")
        print()
        
        if seccion == "similitudes":
            print("   ----- CONSULTA PARA VER SIMILITUDES ENTRE USUARIOS (4.1) -----")
            print("   MATCH (u:Usuario)-[s:SIMILAR]-(v:Usuario)")
            print("   RETURN u, s, v LIMIT 100")
            
        elif seccion == "articulos_aleatorios":
            print("   ----- CONSULTA PARA VER ARTÍCULOS Y SUS REVIEWS (4.2) -----")
            print("   MATCH (a:Articulo)-[r:REVIEW]-(u:Usuario)")
            print("   RETURN a, r, u LIMIT 100")
            
        elif seccion == "usuarios_tipos":
            print("   ----- CONSULTA PARA VER USUARIOS Y TIPOS DE ARTÍCULOS (4.3) -----")
            print("   MATCH (u:Usuario)-[c:CONSUME]->(t:Tipo)")
            print("   RETURN u, c, t LIMIT 100")
            
        elif seccion == "populares":
            print("   ----- CONSULTA PARA VER ARTÍCULOS POPULARES (4.4) -----")
            print("   MATCH (a:Articulo {popular: true})<-[r:REVIEW]-(u:Usuario)")
            print("   OPTIONAL MATCH (u1:Usuario)-[c:COMUN]->(u2:Usuario)")
            print("   RETURN a, r, u, c LIMIT 200")
        
        print("\n4. Para una mejor visualización:")
        print("   - Puedes hacer zoom con la rueda del ratón")
        print("   - Arrastra los nodos para reorganizarlos")
        print("   - Usa el botón de 'Layout' (círculo, fuerza, etc.)")
    
    # ==================== 4.1 SIMILITUDES ENTRE USUARIOS ====================
    
    def obtener_usuarios_top_reviews(self, n=30):
        """Obtiene los n usuarios con más reviews (CORREGIDO)"""
        query = """
        MATCH (u:Usuario)-[r:REVIEW]->()
        RETURN u.id AS usuario_id, COUNT(r) AS num_reviews
        ORDER BY num_reviews DESC
        LIMIT $n
        """
        with self.driver.session() as session:
            result = session.run(query, n=n)
            usuarios = [{"id": record["usuario_id"], 
                        "num_reviews": record["num_reviews"]} for record in result]
            return usuarios
    
    def obtener_valoraciones_usuario(self, usuario_id):
        """Obtiene todas las valoraciones de un usuario"""
        query = """
        MATCH (u:Usuario {id: $usuario_id})-[r:REVIEW]->(a:Articulo)
        RETURN a.id AS articulo_id, r.nota AS nota
        """
        with self.driver.session() as session:
            result = session.run(query, usuario_id=usuario_id)
            valoraciones = {record["articulo_id"]: record["nota"] for record in result}
            return valoraciones
    
    def calcular_similitud_pearson(self, valoraciones_u, valoraciones_v):
        """Calcula la correlación de Pearson entre dos usuarios"""
        # Obtener artículos valorados en común
        articulos_comunes = set(valoraciones_u.keys()) & set(valoraciones_v.keys())
        
        if len(articulos_comunes) < 2:
            return 0
        
        # Calcular medias
        media_u = sum(valoraciones_u.values()) / len(valoraciones_u)
        media_v = sum(valoraciones_v.values()) / len(valoraciones_v)
        
        # Calcular numerador y denominadores
        numerador = 0
        denom_u = 0
        denom_v = 0
        
        for articulo in articulos_comunes:
            diff_u = valoraciones_u[articulo] - media_u
            diff_v = valoraciones_v[articulo] - media_v
            numerador += diff_u * diff_v
            denom_u += diff_u ** 2
            denom_v += diff_v ** 2
        
        if denom_u == 0 or denom_v == 0:
            return 0
        
        return numerador / (math.sqrt(denom_u) * math.sqrt(denom_v))
    
    def calcular_y_guardar_similitudes(self, num_usuarios=30):
        """Calcula similitudes entre los top N usuarios y las guarda en archivo"""
        print(f"\nCalculando similitudes para {num_usuarios} usuarios...")
        
        # Obtener usuarios
        usuarios = self.obtener_usuarios_top_reviews(num_usuarios)
        
        if len(usuarios) == 0:
            print("No hay usuarios con reviews en la base de datos")
            print("   Asegúrate de haber cargado los datos primero con carga_neo4j.py")
            return []
        
        print(f"Obtenidos {len(usuarios)} usuarios con más reviews")
        
        # Mostrar los top usuarios
        print("\nTOP USUARIOS POR NÚMERO DE REVIEWS:")
        for i, u in enumerate(usuarios[:10]):
            print(f"   {i+1}. Usuario {u['id']}: {u['num_reviews']} reviews")
        
        # Obtener valoraciones de todos los usuarios
        print("\nObteniendo valoraciones de usuarios...")
        valoraciones_usuarios = {}
        for i, usuario in enumerate(usuarios):
            valoraciones_usuarios[usuario["id"]] = self.obtener_valoraciones_usuario(usuario["id"])
            if (i + 1) % 10 == 0:
                print(f"   Procesados {i+1}/{len(usuarios)} usuarios")
        
        # Calcular similitudes
        print("\nCalculando similitudes de Pearson...")
        similitudes = []
        total_pares = len(usuarios) * (len(usuarios) - 1) // 2
        
        for idx, (i, j) in enumerate(combinations(range(len(usuarios)), 2)):
            u_id = usuarios[i]["id"]
            v_id = usuarios[j]["id"]
            
            similitud = self.calcular_similitud_pearson(
                valoraciones_usuarios[u_id], 
                valoraciones_usuarios[v_id]
            )
            
            if similitud > 0:  # Solo guardar similitudes positivas
                similitudes.append({
                    "usuario1": u_id,
                    "usuario2": v_id,
                    "similitud": round(similitud, 4)
                })
            
            if (idx + 1) % 100 == 0:
                print(f"   Procesados {idx+1}/{total_pares} pares")
        
        # Guardar en archivo
        with open(self.similitudes_file, "w", encoding="utf-8") as f:
            f.write("usuario1,usuario2,similitud\n")
            for sim in similitudes:
                f.write(f"{sim['usuario1']},{sim['usuario2']},{sim['similitud']}\n")
        
        print(f"\nCalculadas {len(similitudes)} similitudes (positivas) y guardadas en '{self.similitudes_file}'")
        return similitudes
    
    def cargar_similitudes_en_neo4j(self, similitudes):
        """Carga las similitudes como relaciones en Neo4j"""
        if len(similitudes) == 0:
            print("No hay similitudes para cargar")
            return
        
        print("\nCargando similitudes en Neo4j...")
        
        for i, sim in enumerate(similitudes):
            query = """
            MATCH (u1:Usuario {id: $id1})
            MATCH (u2:Usuario {id: $id2})
            MERGE (u1)-[s:SIMILAR {similitud: $similitud}]-(u2)
            """
            with self.driver.session() as session:
                session.run(query, id1=sim["usuario1"], id2=sim["usuario2"], 
                          similitud=sim["similitud"])
            
            if (i + 1) % 50 == 0:
                print(f"   Cargadas {i+1}/{len(similitudes)} similitudes")
        
        print(f"Cargadas {len(similitudes)} relaciones de similitud en Neo4j")
    
    def obtener_usuario_mas_vecinos(self):
        """Consulta el usuario con más vecinos (relaciones SIMILAR)"""
        query = """
        MATCH (u:Usuario)-[:SIMILAR]-(vecino)
        RETURN u.id AS usuario_id, COUNT(vecino) AS num_vecinos
        ORDER BY num_vecinos DESC
        LIMIT 1
        """
        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            if record:
                print(f"\nUSUARIO CON MÁS VECINOS:")
                print(f"   ID: {record['usuario_id']}")
                print(f"   Número de vecinos: {record['num_vecinos']}")
                return record
            else:
                print("\nNo se encontraron relaciones de similitud")
                return None
    
    # ==================== 4.2 ENLACES ENTRE USUARIOS Y ARTÍCULOS ====================
    
    def obtener_articulos_aleatorios_con_reviews(self, tipo_articulo, numero_articulos):
        """Obtiene N artículos aleatorios y muestra sus reviews"""
        query = """
        MATCH (a:Articulo)
        WHERE a.tipo CONTAINS $tipo OR $tipo CONTAINS a.tipo
        WITH a, rand() AS random
        ORDER BY random
        LIMIT $limite
        OPTIONAL MATCH (u:Usuario)-[r:REVIEW]->(a)
        RETURN a.id AS id_articulo, 
               a.nombre AS nombre_articulo,
               a.tipo AS tipo_articulo,
               u.id AS id_usuario,
               r.nota AS nota,
               r.momento AS momento
        ORDER BY a.id, r.momento
        """
        
        with self.driver.session() as session:
            result = session.run(query, tipo=tipo_articulo, limite=numero_articulos)
            records = list(result)
            
            if not records:
                print(f"No se encontraron artículos del tipo '{tipo_articulo}'")
                print("   Tipos disponibles: Videojuegos, Discos, Juguetes, Instrumentos")
                return
            
            print(f"MOSTRANDO {numero_articulos} ARTÍCULOS ALEATORIOS DE TIPO: {tipo_articulo}")
            
            articulos_mostrados = {}
            for record in records:
                id_art = record["id_articulo"]
                
                if id_art not in articulos_mostrados:
                    articulos_mostrados[id_art] = True
                    print(f"\nARTÍCULO: {record['nombre_articulo']} (ID: {id_art})")
                    print(f"   Tipo: {record['tipo_articulo']}")
                    
                    if record["id_usuario"]:
                        print(f"   Usuario ID: {record['id_usuario']}")
                        print(f"   Nota: {record['nota']}/10")
                        print(f"   Momento: {record['momento']}")
                    else:
                        print("   Este artículo no tiene reviews aún")
            
            print(f"\nRESUMEN:")
            print(f"   Total artículos mostrados: {len(articulos_mostrados)}")
            print(f"   Total relaciones review: {len([r for r in records if r['id_usuario']])}")
    
    # ==================== 4.3 USUARIOS CON MÚLTIPLES TIPOS ====================
    
    def obtener_usuarios_con_tipos_distintos(self, limite=400):
        """Obtiene los primeros N usuarios que han puntuado al menos 2 tipos distintos"""
        print(f"\nBuscando usuarios que hayan puntuado al menos 2 tipos de artículos...")
        
        query = """
        MATCH (u:Usuario)
        WITH u
        ORDER BY u.id
        LIMIT $limite
        MATCH (u)-[r:REVIEW]->(a:Articulo)
        WITH u, COLLECT(DISTINCT a.tipo) AS tipos_puntuados
        WHERE SIZE(tipos_puntuados) >= 2
        RETURN u.id AS usuario_id, 
               tipos_puntuados,
               SIZE(tipos_puntuados) AS num_tipos
        ORDER BY u.id
        """
        
        with self.driver.session() as session:
            result = session.run(query, limite=limite)
            usuarios = list(result)
            
            if not usuarios:
                print(f"No se encontraron usuarios que cumplan el criterio")
                return []
            
            print(f"Encontrados {len(usuarios)} usuarios que puntuaron al menos 2 tipos")
            return usuarios
    
    def cargar_relaciones_usuario_tipo(self, usuarios):
        """Crea nodos de Tipo y relaciones con usuarios indicando cantidad consumida"""
        print("\nCargando relaciones usuario-tipo en Neo4j...")
        
        for i, usuario in enumerate(usuarios):
            usuario_id = usuario["usuario_id"]
            
            # Para cada tipo, contar cuántos artículos consumió
            query_tipos = """
            MATCH (u:Usuario {id: $usuario_id})-[r:REVIEW]->(a:Articulo)
            RETURN a.tipo AS tipo, COUNT(DISTINCT a) AS cantidad
            """
            
            with self.driver.session() as session:
                tipos = session.run(query_tipos, usuario_id=usuario_id)
                
                for tipo_record in tipos:
                    tipo = tipo_record["tipo"]
                    cantidad = tipo_record["cantidad"]
                    
                    # Crear nodo Tipo si no existe
                    session.run("MERGE (t:Tipo {nombre: $tipo})", tipo=tipo)
                    
                    # Crear relación CONSUME
                    session.run("""
                    MATCH (u:Usuario {id: $usuario_id})
                    MATCH (t:Tipo {nombre: $tipo})
                    MERGE (u)-[c:CONSUME {cantidad: $cantidad}]->(t)
                    """, usuario_id=usuario_id, tipo=tipo, cantidad=cantidad)
            
            if (i + 1) % 50 == 0:
                print(f"   Procesados {i+1}/{len(usuarios)} usuarios")
        
        print(f"Cargadas relaciones para {len(usuarios)} usuarios")
    
    # ==================== 4.4 ARTÍCULOS POPULARES Y EN COMÚN ====================
    
    def obtener_articulos_populares_limitados(self, max_reviews=40, num_articulos=5):
        """Obtiene los artículos más populares con menos de N reviews"""
        query = """
        MATCH (a:Articulo)<-[r:REVIEW]-(u:Usuario)
        WITH a, COUNT(r) AS num_reviews, COLLECT(u) AS usuarios
        WHERE num_reviews < $max_reviews
        RETURN a.id AS id_articulo,
               a.nombre AS nombre,
               a.tipo AS tipo,
               num_reviews,
               usuarios
        ORDER BY num_reviews DESC
        LIMIT $num_articulos
        """
        
        with self.driver.session() as session:
            result = session.run(query, max_reviews=max_reviews, num_articulos=num_articulos)
            articulos = list(result)
            
            if not articulos:
                print(f"No se encontraron artículos con menos de {max_reviews} reviews")
                return []
            
            print(f"\nTOP {num_articulos} ARTÍCULOS POPULARES (menos de {max_reviews} reviews):")
            for art in articulos:
                print(f"   - {art['nombre']}: {art['num_reviews']} reviews")
            
            return articulos
    
    def cargar_articulos_populares_y_relaciones_comunes(self, articulos):
        """Carga artículos populares y crea relaciones entre usuarios por artículos en común"""
        print("\nCargando artículos populares...")
        
        # Primero, marcar los artículos como populares
        for articulo in articulos:
            query_articulo = """
            MATCH (a:Articulo {id: $id})
            SET a.popular = true
            """
            with self.driver.session() as session:
                session.run(query_articulo, id=articulo["id_articulo"])
        
        print("Artículos marcados como populares")
        
        # Ahora, crear relaciones COMUN entre usuarios que comparten artículos
        print("\nCalculando relaciones entre usuarios por artículos en común...")
        
        # Obtener todos los usuarios que puntuaron estos artículos
        usuarios_set = set()
        for articulo in articulos:
            for usuario in articulo["usuarios"]:
                usuarios_set.add(usuario["id"])
        
        usuarios_lista = list(usuarios_set)
        
        if len(usuarios_lista) < 2:
            print("No hay suficientes usuarios para crear relaciones COMUN")
            return set()
        
        # Crear relaciones COMUN entre usuarios que compartieron artículos
        relaciones_creadas = set()
        
        for i, j in combinations(range(len(usuarios_lista)), 2):
            u1_id = usuarios_lista[i]
            u2_id = usuarios_lista[j]
            
            # Contar artículos en común entre estos usuarios (solo entre los populares)
            query_comunes = """
            MATCH (u1:Usuario {id: $u1_id})-[:REVIEW]->(a:Articulo {popular: true})<-[:REVIEW]-(u2:Usuario {id: $u2_id})
            RETURN COUNT(DISTINCT a) AS articulos_comunes
            """
            with self.driver.session() as session:
                result = session.run(query_comunes, u1_id=u1_id, u2_id=u2_id)
                record = result.single()
                num_comunes = record["articulos_comunes"] if record else 0
            
            if num_comunes > 0:
                # Evitar duplicados (relación bidireccional)
                if (u1_id, u2_id) not in relaciones_creadas and (u2_id, u1_id) not in relaciones_creadas:
                    query_relacion = """
                    MATCH (u1:Usuario {id: $u1_id})
                    MATCH (u2:Usuario {id: $u2_id})
                    MERGE (u1)-[c:COMUN {articulos_compartidos: $num}]-(u2)
                    """
                    with self.driver.session() as session:
                        session.run(query_relacion, u1_id=u1_id, u2_id=u2_id, num=num_comunes)
                    relaciones_creadas.add((u1_id, u2_id))
        
        print(f"Creadas {len(relaciones_creadas)} relaciones COMUN entre usuarios")
        return relaciones_creadas


# ==================== FUNCIÓN PRINCIPAL CON MENÚ ====================

def mostrar_menu():
    """Muestra el menú principal"""
    print("                 NEO4J PROYECTO - MENÚ PRINCIPAL")
    print("1.  [4.1] Calcular similitudes entre usuarios (Pearson)")
    print("2.  [4.2] Mostrar artículos aleatorios con sus reviews")
    print("3.  [4.3] Mostrar usuarios que han visto más de un tipo de artículo")
    print("4.  [4.4] Mostrar artículos populares y relaciones entre usuarios")
    print("5.  Limpiar base de datos Neo4j")
    print("6.  Salir")


def main():
    # Configuración desde config.py
    URI = NEO4J_URI
    USER = NEO4J_USER
    PASSWORD = NEO4J_PASSWORD
    
    # Crear instancia
    neo4j_app = Neo4jProyecto(URI, USER, PASSWORD)
    
    try:
        print("INICIANDO APLICACIÓN NEO4J")
        print(f"Usando configuración de: config.py")
        print(f"   - TOP_USUARIOS_SIMILITUD = {TOP_USUARIOS_SIMILITUD}")
        print(f"   - NUM_ARTICULOS_ALEATORIOS = {NUM_ARTICULOS_ALEATORIOS}")
        print(f"   - TOP_USUARIOS_NOMBRE = {TOP_USUARIOS_NOMBRE}")
        
        # Verificar que hay datos
        with neo4j_app.driver.session() as session:
            result = session.run("MATCH (u:Usuario) RETURN count(u) AS total")
            total_usuarios = result.single()["total"]
            if total_usuarios == 0:
                print("\nATENCIÓN: La base de datos de Neo4j está VACÍA")
                print("   Debes ejecutar primero: python carga_neo4j.py")
                print("   Esto cargará los datos desde los archivos JSON")
                return
        
        
        while True:
            mostrar_menu()
            opcion = input("\nSeleccione una opción (1-6): ").strip()
            
            if opcion == "1":  # Sección 4.1
                print("SECCIÓN 4.1 - SIMILITUDES ENTRE USUARIOS")
                
                # Limpiar similitudes anteriores (pero no los datos originales)
                print("NOTA: No se limpia la BD para conservar los datos originales")
                
                # Calcular similitudes
                similitudes = neo4j_app.calcular_y_guardar_similitudes(TOP_USUARIOS_SIMILITUD)
                
                if similitudes:
                    # Cargar en Neo4j
                    neo4j_app.cargar_similitudes_en_neo4j(similitudes)
                    
                    # Mostrar usuario con más vecinos
                    neo4j_app.obtener_usuario_mas_vecinos()
                
                # Instrucciones para visualizar
                neo4j_app.mostrar_instrucciones_visualizacion("similitudes")
                
                print("CARGA COMPLETADA - Ya puedes ver el grafo en Neo4j Browser")
                
            elif opcion == "2":  # Sección 4.2
                print("SECCIÓN 4.2 - ARTÍCULOS ALEATORIOS CON REVIEWS")
                
                # Pedir datos al usuario
                print("\nTIPOS DE ARTÍCULOS DISPONIBLES:")
                print("   - Videojuegos")
                print("   - Discos")
                print("   - Juguetes")
                print("   - Instrumentos")
                
                tipo = input("\nIngrese el tipo de artículo: ").strip()
                
                while True:
                    try:
                        numero = int(input(f"Ingrese el número de artículos aleatorios a mostrar (por defecto {NUM_ARTICULOS_ALEATORIOS}): ") or NUM_ARTICULOS_ALEATORIOS)
                        if numero > 0:
                            break
                        else:
                            print("Por favor, ingrese un número positivo")
                    except ValueError:
                        print("Por favor, ingrese un número válido")
                
                # Obtener y mostrar resultados
                neo4j_app.obtener_articulos_aleatorios_con_reviews(tipo, numero)
                
                # Instrucciones para visualizar
                neo4j_app.mostrar_instrucciones_visualizacion("articulos_aleatorios")
                
                print("CARGA COMPLETADA - Ya puedes ver el grafo en Neo4j Browser")
                
            elif opcion == "3":  # Sección 4.3
                print("SECCIÓN 4.3 - USUARIOS CON MÚLTIPLES TIPOS DE ARTÍCULOS")
                
                # Obtener usuarios
                usuarios = neo4j_app.obtener_usuarios_con_tipos_distintos(TOP_USUARIOS_NOMBRE)
                
                if usuarios:
                    # Mostrar resultados en pantalla
                    print("\nUSUARIOS ENCONTRADOS:")
                    for u in usuarios[:20]:  # Mostrar primeros 20
                        print(f"   Usuario ID: {u['usuario_id']}")
                        print(f"      Tipos: {', '.join(u['tipos_puntuados'])}")
                        print(f"      Número de tipos: {u['num_tipos']}")
                        print()
                    
                    if len(usuarios) > 20:
                        print(f"   ... y {len(usuarios)-20} usuarios más")
                    
                    # Cargar relaciones en Neo4j
                    neo4j_app.cargar_relaciones_usuario_tipo(usuarios)
                    
                    # Instrucciones para visualizar
                    neo4j_app.mostrar_instrucciones_visualizacion("usuarios_tipos")
                    
                    print("CARGA COMPLETADA - Ya puedes ver el grafo en Neo4j Browser")
                else:
                    print("No se encontraron usuarios que cumplan el criterio")
                
            elif opcion == "4":  # Sección 4.4
                print("SECCIÓN 4.4 - ARTÍCULOS POPULARES Y RELACIONES ENTRE USUARIOS")
                
                # Parámetros (modificables fácilmente)
                max_reviews = 40
                num_articulos = 5
                
                print(f"\nConfiguración:")
                print(f"   - Máximo de reviews por artículo: {max_reviews}")
                print(f"   - Número de artículos a mostrar: {num_articulos}")
                
                # Obtener artículos populares
                articulos = neo4j_app.obtener_articulos_populares_limitados(max_reviews, num_articulos)
                
                if articulos:
                    # Cargar artículos y relaciones
                    relaciones = neo4j_app.cargar_articulos_populares_y_relaciones_comunes(articulos)
                    
                    # Instrucciones para visualizar
                    neo4j_app.mostrar_instrucciones_visualizacion("populares")
                    
                    print("CARGA COMPLETADA - Ya puedes ver el grafo en Neo4j Browser")
                else:
                    print("No se encontraron artículos que cumplan el criterio")
                
            elif opcion == "5":  # Limpiar BD
                print("LIMPIANDO BASE DE DATOS")
                confirm = input("¿Estás seguro? Esto eliminará TODOS los datos (s/n): ")
                if confirm.lower() == 's':
                    neo4j_app.limpiar_base_datos()
                    print("Base de datos limpia. Para recargar datos ejecuta: python carga_neo4j.py")
                else:
                    print("Operación cancelada")
                
            elif opcion == "6":  # Salir
                print("\n¡Hasta luego!")
                break
                
            else:
                print("\nOpción no válida. Por favor, seleccione 1-6")
            
            # Pausa antes de continuar
            if opcion != "6":
                input("\nPresione Enter para continuar...")
    
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido por el usuario")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        neo4j_app.close()
        print("\nConexión con Neo4j cerrada")


if __name__ == "__main__":
    main()