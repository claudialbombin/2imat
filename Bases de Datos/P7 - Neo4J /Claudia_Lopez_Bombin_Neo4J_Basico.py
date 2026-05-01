# ============================================================
# Práctica 7 - Neo4J
# Fichero de queries Cypher para la base de datos de películas
# ============================================================

queries = {

    # ----------------------------------------------------------
    # Pregunta 1:
    # Muestra el título (solo título) de las películas que fueron
    # estrenadas en 2006.
    # ----------------------------------------------------------
    "pregunta1":
    """
MATCH (p:Movie)
WHERE p.released = 2006
RETURN p.title AS titulo
    """,

    # ----------------------------------------------------------
    # Pregunta 2:
    # Obtén las personas (con todos los datos) que han dirigido
    # películas estrenadas en 2006. Muestra la persona y la película.
    # ----------------------------------------------------------
    "pregunta2":
    """
MATCH (persona:Person)-[:DIRECTED]->(pelicula:Movie)
WHERE pelicula.released = 2006
RETURN persona, pelicula
    """,

    # ----------------------------------------------------------
    # Pregunta 3:
    # Obtén todas las películas en las que estuvo involucrado
    # Clint Eastwood y muestra el tipo de relación.
    # ----------------------------------------------------------
    "pregunta3":
    """
MATCH (persona:Person)-[r]->(pelicula:Movie)
WHERE persona.name = 'Clint Eastwood'
RETURN pelicula.title AS titulo, TYPE(r) AS tipo_relacion
    """,

    # ----------------------------------------------------------
    # Pregunta 4:
    # Muestra el título de la película y el personaje que interpreta
    # Keanu Reeves en cada película en la que actúa.
    # ----------------------------------------------------------
    "pregunta4":
    """
MATCH (persona:Person)-[r:ACTED_IN]->(pelicula:Movie)
WHERE persona.name = 'Keanu Reeves'
RETURN pelicula.title AS titulo, r.roles AS personaje
    """,

    # ----------------------------------------------------------
    # Pregunta 5:
    # Mostrar relaciones REVIEWED donde el resumen contiene "but"
    # (mayúsculas o minúsculas). Muestra nombre, título, calificación
    # y resumen.
    # ----------------------------------------------------------
    "pregunta5":
    """
MATCH (persona:Person)-[r:REVIEWED]->(pelicula:Movie)
WHERE toLower(r.summary) CONTAINS 'but'
RETURN persona.name AS nombre, pelicula.title AS titulo,
       r.rating AS calificacion, r.summary AS resumen
    """,

    # ----------------------------------------------------------
    # Pregunta 6:
    # Muestra personas que han dirigido alguna película y también
    # han actuado en otra distinta. Devuelve el nodo persona y las
    # películas donde actúa pero no dirige.
    # ----------------------------------------------------------
    "pregunta6":
    """
MATCH (persona:Person)-[:DIRECTED]->(dirigida:Movie),
      (persona)-[:ACTED_IN]->(actuada:Movie)
WHERE dirigida <> actuada
RETURN persona, actuada
    """,

    # ----------------------------------------------------------
    # Pregunta 7:
    # Muestra personas que han producido una película pero NO la
    # han dirigido NI han actuado en ella. Devuelve persona y película.
    # ----------------------------------------------------------
    "pregunta7":
    """
MATCH (persona:Person)-[:PRODUCED]->(pelicula:Movie)
WHERE NOT (persona)-[:DIRECTED]->(pelicula)
  AND NOT (persona)-[:ACTED_IN]->(pelicula)
RETURN persona, pelicula
    """,

    # ----------------------------------------------------------
    # Pregunta 8:
    # Muestra películas y actores donde uno de los actores también
    # ha dirigido la película. Devuelve nombres de actores, del
    # director-actor y el título de la película.
    # ----------------------------------------------------------
    "pregunta8":
    """
MATCH (director:Person)-[:DIRECTED]->(pelicula:Movie),
      (director)-[:ACTED_IN]->(pelicula),
      (actor:Person)-[:ACTED_IN]->(pelicula)
WHERE actor <> director
RETURN pelicula.title AS titulo,
       director.name AS director_y_actor,
       actor.name AS actor
    """,

    # ----------------------------------------------------------
    # Pregunta 9:
    # Muestra películas estrenadas en 2000, 2004 o 2008,
    # devolviendo título y año de estreno.
    # ----------------------------------------------------------
    "pregunta9":
    """
MATCH (pelicula:Movie)
WHERE pelicula.released IN [2000, 2004, 2008]
RETURN pelicula.title AS titulo, pelicula.released AS anio
    """,

    # ----------------------------------------------------------
    # Pregunta 10:
    # Películas con al menos una review y que tienen director.
    # Muestra el grafo: persona que revisó, película y director.
    # ----------------------------------------------------------
    "pregunta10":
    """
MATCH (revisor:Person)-[:REVIEWED]->(pelicula:Movie)<-[:DIRECTED]-(director:Person)
RETURN revisor, pelicula, director
    """,

    # ----------------------------------------------------------
    # Pregunta 11:
    # Actores que han actuado juntos en una película m, donde el
    # segundo actor ha dirigido otra película distinta a m en la que
    # también actúa el primero. Retorna nodos de actores y películas.
    # ----------------------------------------------------------
    "pregunta11":
    """
MATCH (actor1:Person)-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(actor2:Person),
      (actor2)-[:DIRECTED]->(otraMovie:Movie)<-[:ACTED_IN]-(actor1)
WHERE m <> otraMovie
  AND actor1 <> actor2
RETURN actor1, actor2, m, otraMovie
    """,

    # ----------------------------------------------------------
    # Pregunta 12:
    # Películas en las que actuó Keanu Reeves, sus directores y los
    # demás actores que actuaron en esas películas.
    # ----------------------------------------------------------
    "pregunta12":
    """
MATCH (keanu:Person)-[:ACTED_IN]->(pelicula:Movie)<-[:DIRECTED]-(director:Person),
      (otroActor:Person)-[:ACTED_IN]->(pelicula)
WHERE keanu.name = 'Keanu Reeves'
  AND otroActor <> keanu
RETURN pelicula.title AS pelicula,
       director.name AS director,
       otroActor.name AS actor_compañero
    """,

    # ----------------------------------------------------------
    # Pregunta 13:
    # Películas de Charlize Theron: título, año de estreno, hace
    # cuántos años se estrenó y la edad de Charlize cuando se estrenó.
    # Ordenado por número de años desde el estreno (desc).
    # ----------------------------------------------------------
    "pregunta13":
    """
MATCH (charlize:Person)-[:ACTED_IN]->(pelicula:Movie)
WHERE charlize.name = 'Charlize Theron'
RETURN pelicula.title AS titulo,
       pelicula.released AS anio_estreno,
       (2024 - pelicula.released) AS años_desde_estreno,
       (pelicula.released - charlize.born) AS edad_al_estreno
ORDER BY años_desde_estreno DESC
    """,

    # ----------------------------------------------------------
    # Pregunta 14:
    # Nombre del actor y número de películas en las que ha actuado,
    # solo para actores con al menos 5 películas.
    # ----------------------------------------------------------
    "pregunta14":
    """
MATCH (actor:Person)-[:ACTED_IN]->(pelicula:Movie)
WITH actor, COUNT(pelicula) AS num_peliculas
WHERE num_peliculas >= 5
RETURN actor.name AS actor, num_peliculas
ORDER BY num_peliculas DESC
    """,

    # ----------------------------------------------------------
    # Pregunta 15:
    # Personas que han hecho reseñas y actores de esas películas.
    # Devuelve: nombre del revisor, título, año de estreno,
    # calificación y lista de actores.
    # ----------------------------------------------------------
    "pregunta15":
    """
MATCH (revisor:Person)-[r:REVIEWED]->(pelicula:Movie)
OPTIONAL MATCH (actor:Person)-[:ACTED_IN]->(pelicula)
WITH revisor, pelicula, r, COLLECT(actor.name) AS lista_actores
RETURN revisor.name AS revisor,
       pelicula.title AS titulo,
       pelicula.released AS año_estreno,
       r.rating AS calificacion,
       lista_actores
    """,

    # ----------------------------------------------------------
    # Pregunta 16:
    # Directores ordenados alfabéticamente con la lista (sin
    # repetición) de actores que han actuado en sus películas.
    # ----------------------------------------------------------
    "pregunta16":
    """
MATCH (director:Person)-[:DIRECTED]->(pelicula:Movie)<-[:ACTED_IN]-(actor:Person)
WITH director, COLLECT(DISTINCT actor.name) AS actores
RETURN director.name AS director, actores
ORDER BY director.name ASC
    """,

    # ----------------------------------------------------------
    # Pregunta 17:
    # Películas con al menos una review hecha por alguien que tiene
    # algún seguidor. Muestra película, director y revisor (nodos).
    # ----------------------------------------------------------
    "pregunta17":
    """
MATCH (revisor:Person)-[:REVIEWED]->(pelicula:Movie)<-[:DIRECTED]-(director:Person),
      (seguidor:Person)-[:FOLLOWS]->(revisor)
RETURN revisor, pelicula, director
    """,

    # ----------------------------------------------------------
    # Pregunta 18:
    # Grafo de películas, directores y actores, solo para directores
    # que han dirigido más de dos películas.
    # ----------------------------------------------------------
    "pregunta18":
    """
MATCH (director:Person)-[:DIRECTED]->(pelicula:Movie)
WITH director, COUNT(pelicula) AS num_dirigidas
WHERE num_dirigidas > 2
MATCH (director)-[:DIRECTED]->(p:Movie)<-[:ACTED_IN]-(actor:Person)
RETURN director, p, actor
    """,

    # ----------------------------------------------------------
    # Pregunta 19:
    # Modifica el papel de John Cusack en Stand By Me
    # de 'Denny Lachance' a 'D. Lachance'.
    # ----------------------------------------------------------
    "pregunta19":
    """
MATCH (john:Person)-[r:ACTED_IN]->(pelicula:Movie)
WHERE john.name = 'John Cusack'
  AND pelicula.title = 'Stand By Me'
SET r.roles = ['D. Lachance']
RETURN john.name AS actor, pelicula.title AS pelicula, r.roles AS nuevo_rol
    """,

    # ----------------------------------------------------------
    # Pregunta 20:
    # Crea un nodo con tu nombre y añade una review a una película.
    # (Cambia el nombre y los datos a tu gusto)
    # ----------------------------------------------------------
    "pregunta20":
    """
MATCH (pelicula:Movie {title: 'The Matrix'})
CREATE (yo:Person {name: 'Claudia Maria Lopez Bombin'})
CREATE (yo)-[:REVIEWED {rating: 99, summary: 'Una pelicula que te cambia la perspectiva'}]->(pelicula)
RETURN yo, pelicula
    """,

}


# ============================================================
# Queries opcionales - parte de emails
# ============================================================

queries_opcionales = {

    # ----------------------------------------------------------
    # Opcional 1:
    # Obtén todos los nodos que solo tienen una relación de escritura
    # y esa relación es consigo mismo (bucle).
    # ----------------------------------------------------------
    "opcional1":
    """
MATCH (u:Usuario)-[r:ENVIA_MAIL]->(u)
WHERE NOT EXISTS {
    MATCH (u)-[r2:ENVIA_MAIL]->(otro:Usuario)
    WHERE otro <> u
}
AND NOT EXISTS {
    MATCH (otro2:Usuario)-[r3:ENVIA_MAIL]->(u)
    WHERE otro2 <> u
}
RETURN u
    """,

    # ----------------------------------------------------------
    # Opcional 2:
    # Obtén el número de usuarios pertenecientes a cada departamento.
    # ----------------------------------------------------------
    "opcional2":
    """
MATCH (u:Usuario)-[:PERTENECE_A]->(d:Departamento)
RETURN d.id_departamento AS departamento, COUNT(u) AS num_usuarios
ORDER BY num_usuarios DESC
    """,

    # ----------------------------------------------------------
    # Opcional 3:
    # Obtén el número de mensajes recibidos por cada usuario,
    # ordenado de forma descendente.
    # ----------------------------------------------------------
    "opcional3":
    """
MATCH (emisor:Usuario)-[:ENVIA_MAIL]->(receptor:Usuario)
RETURN receptor.id_usuario AS usuario, COUNT(*) AS mensajes_recibidos
ORDER BY mensajes_recibidos DESC
    """,

}


# ============================================================
# Queries extra (sección 4 del enunciado)
# ============================================================

queries_extra = {

    # ----------------------------------------------------------
    # Extra 1:
    # Actores, productores y directores de cada película.
    # Si no tienen alguno de los tres, la película aparece igual.
    # Sin datos repetidos, ordenado por tamaño de la lista de actores.
    # ----------------------------------------------------------
    "extra1":
    """
MATCH (pelicula:Movie)
OPTIONAL MATCH (actor:Person)-[:ACTED_IN]->(pelicula)
OPTIONAL MATCH (productor:Person)-[:PRODUCED]->(pelicula)
OPTIONAL MATCH (director:Person)-[:DIRECTED]->(pelicula)
WITH pelicula,
     COLLECT(DISTINCT actor.name) AS actores,
     COLLECT(DISTINCT productor.name) AS productores,
     COLLECT(DISTINCT director.name) AS directores
RETURN pelicula.title AS titulo, actores, productores, directores
ORDER BY SIZE(actores) ASC
    """,

    # ----------------------------------------------------------
    # Extra 2:
    # Para Paul Blythe, mostrar si tiene relación FOLLOWS en
    # cualquier dirección con exactamente 3 saltos.
    # ----------------------------------------------------------
    "extra2":
    """
MATCH (paul:Person {name: 'Paul Blythe'})-[:FOLLOWS*3]-(otro:Person)
RETURN paul, otro
    """,

    # ----------------------------------------------------------
    # Extra 3:
    # Películas con al menos 2 directores. Muestra los que la han
    # puntuado (si no hay nadie, muéstrala igual).
    # ----------------------------------------------------------
    "extra3":
    """
MATCH (director:Person)-[:DIRECTED]->(pelicula:Movie)
WITH pelicula, COUNT(director) AS num_directores
WHERE num_directores >= 2
OPTIONAL MATCH (revisor:Person)-[:REVIEWED]->(pelicula)
RETURN pelicula.title AS titulo, revisor.name AS revisor
    """,

    # ----------------------------------------------------------
    # Extra 4:
    # Actores con menos de 4 películas. Muestra nombre y lista
    # de títulos de esas películas.
    # ----------------------------------------------------------
    "extra4":
    """
MATCH (actor:Person)-[:ACTED_IN]->(pelicula:Movie)
WITH actor, COLLECT(pelicula.title) AS peliculas
WHERE SIZE(peliculas) < 4
RETURN actor.name AS actor, peliculas
    """,

    # ----------------------------------------------------------
    # Extra 5:
    # Películas donde al menos 2 personas distintas están
    # relacionadas con ella de al menos 2 formas distintas cada una.
    # ----------------------------------------------------------
    "extra5":
    """
MATCH (persona:Person)-[r]->(pelicula:Movie)
WITH pelicula, persona, COLLECT(DISTINCT TYPE(r)) AS tipos_relacion
WHERE SIZE(tipos_relacion) >= 2
WITH pelicula, COLLECT(DISTINCT persona) AS personas_multiples
WHERE SIZE(personas_multiples) >= 2
RETURN pelicula.title AS titulo, personas_multiples
    """,

}
