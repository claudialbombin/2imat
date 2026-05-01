"""
=============================================================================
PROYECTO FINAL - BASES DE DATOS
Asignatura: Bases de Datos - 2º curso
Grado en Ingeniería Matemática e Inteligencia Artificial (IMAT)
=============================================================================
Alumna: Claudia Maria Lopez Bombin
=============================================================================
Descripción:
    Quinta parte del proyecto: recomendaciones simples basadas en popularidad.

    Dada la ID de un usuario y un tipo de artículo, devuelve los 10
    artículos más populares de esa categoría que el usuario aún NO ha
    valorado.

    Implementación:
      1. Obtiene el conjunto de artículos ya valorados por el usuario (MySQL).
      2. Obtiene los artículos más populares de la categoría indicada,
         ordenados por número de reviews (MySQL).
      3. Filtra los ya consumidos y devuelve los 10 primeros restantes.

    Descripción del modelo de ML (sección 5, parte descriptiva):
    ──────────────────────────────────────────────────────────────
    Para un sistema de recomendaciones más sofisticado se podría emplear
    Filtrado Colaborativo basado en usuarios (User-Based CF):
      • Representar a cada usuario como un vector de valoraciones
        (artículo -> nota, 0 si no lo ha valorado).
      • Usar la similitud de Pearson (ya calculada en 4.1) para
        encontrar los k vecinos más cercanos al usuario objetivo.
      • Predecir la valoración de artículos no consumidos como la
        media ponderada de las valoraciones de los vecinos.
      • Recomendar los artículos con mayor valoración predicha.
    Alternativa: Matrix Factorization (SVD) con surprise/implicit.

    Diagrama (simplificado):
      Usuario objetivo
          │
          ▼
      Vector valoraciones  ──► Similitud Pearson ──► Top-k vecinos
          │                                               │
          │                                      Artículos valorados
          │                                      por vecinos (no consumidos)
          │                                               │
          └─────────────────────────────────────► Ranking predicho
                                                          │
                                                   Top-10 recomendaciones
=============================================================================
"""

import sys
import mysql.connector
import configuracion as cfg


def conectar_mysql() -> mysql.connector.MySQLConnection:
    """Abre y devuelve una conexión MySQL."""
    return mysql.connector.connect(
        host=cfg.MYSQL_HOST,
        port=cfg.MYSQL_PORT,
        user=cfg.MYSQL_USER,
        password=cfg.MYSQL_PASSWORD,
        database=cfg.MYSQL_DATABASE,
    )


def articulos_consumidos_por_usuario(cursor, reviewer_id: str) -> set:
    """
    Devuelve el conjunto de ASINs que el usuario ya ha valorado.

    Parámetros
    ----------
    cursor      : cursor MySQL activo
    reviewer_id : str

    Retorna
    -------
    set  conjunto de asins
    """
    cursor.execute(
        "SELECT DISTINCT asin FROM Reviews WHERE reviewerID = %s;",
        (reviewer_id,)
    )
    return {row[0] for row in cursor.fetchall()}


def top_populares_categoria(cursor, categoria: str, limite: int = 200) -> list[tuple]:
    """
    Devuelve los artículos más populares de la categoría indicada,
    ordenados de mayor a menor número de reviews.

    Parámetros
    ----------
    cursor    : cursor MySQL activo
    categoria : str  nombre de la categoría
    limite    : int  número máximo de candidatos (margen para filtrar)

    Retorna
    -------
    list[tuple]  [(asin, num_reviews), ...]
    """
    cursor.execute("""
        SELECT r.asin, COUNT(*) AS total
        FROM Reviews r
        JOIN Articulos a ON r.asin = a.asin
        JOIN Categorias c ON a.id_categoria = c.id_categoria
        WHERE c.nombre = %s
        GROUP BY r.asin
        ORDER BY total DESC
        LIMIT %s;
    """, (categoria, limite))
    return cursor.fetchall()


def recomendar(reviewer_id: str, categoria: str, top_n: int = 10) -> None:
    """
    Función principal de recomendación.
    Imprime los top_n artículos más populares de la categoría indicada
    que el usuario aún no ha valorado.

    Parámetros
    ----------
    reviewer_id : str  ID del usuario
    categoria   : str  nombre de la categoría
    top_n       : int  número de recomendaciones (por defecto 10)
    """
    con = conectar_mysql()
    cursor = con.cursor()

    # Verificar que el usuario existe
    cursor.execute(
        "SELECT COUNT(*) FROM Usuarios WHERE reviewerID = %s;",
        (reviewer_id,)
    )
    if cursor.fetchone()[0] == 0:
        print(f"[ERROR] El usuario '{reviewer_id}' no existe en la base de datos.")
        cursor.close(); con.close(); return

    # Artículos ya consumidos por el usuario
    consumidos = articulos_consumidos_por_usuario(cursor, reviewer_id)

    # Artículos populares de la categoría
    populares = top_populares_categoria(cursor, categoria)
    cursor.close()
    con.close()

    if not populares:
        print(f"No hay artículos en la categoría '{categoria}'.")
        return

    # Filtrar los ya consumidos y quedarse con los top_n
    recomendaciones = [
        (asin, total)
        for asin, total in populares
        if asin not in consumidos
    ][:top_n]

    if not recomendaciones:
        print("El usuario ya ha valorado todos los artículos populares de esa categoría.")
        return

    print(f"\nTop {top_n} recomendaciones para '{reviewer_id}' en '{categoria}':")
    print(f"{'Pos':>3}  {'ASIN':<15}  {'Reviews':>8}")
    for i, (asin, total) in enumerate(recomendaciones, 1):
        print(f"{i:>3}. {asin:<15}  {total:>8,}")


def main():
    """
    Punto de entrada interactivo.
    Solicita el ID del usuario y la categoría al usuario por terminal.
    """
    print("  RECOMENDACIONES — Top 10 artículos no consumidos")

    reviewer_id = input("\nIntroduce el reviewerID del usuario: ").strip()
    print("\nCategorías disponibles:")
    categorias = list(cfg.DATASETS.keys())
    for i, cat in enumerate(categorias, 1):
        print(f"  {i}. {cat}")

    opcion = input("Selecciona categoría (número): ").strip()
    try:
        categoria = categorias[int(opcion) - 1]
    except (ValueError, IndexError):
        print("Opción no válida.")
        sys.exit(1)

    recomendar(reviewer_id, categoria)


if __name__ == "__main__":
    main()
