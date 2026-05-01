-- ============================================
-- PRÁCTICA SQL + LAST.FM
-- CONSULTAS REQUERIDAS (PARTE 2)
-- ALUMNA: Claudia Maria Lopez Bombin
-- ============================================

USE Lastfm;

-- ============================================
-- CONSULTA 1: Media de edad de los usuarios que han escuchado a "Coldplay"
-- ============================================
SELECT 
    ROUND(AVG(u.edad), 2) AS media_edad_coldplay
FROM usuarios u
WHERE u.edad > 0 
AND u.id_usuario IN (
    SELECT DISTINCT e.id_usuario
    FROM escuchas e
    JOIN canciones c ON e.id_cancion = c.id_cancion
    JOIN artistas a ON c.id_artista = a.id_artista
    WHERE a.nombre_artista LIKE '%Coldplay%'
);

-- ============================================
-- CONSULTA 2: Número total de hombres que han escuchado a "Janet Jackson" o "The Clash"
-- ============================================
SELECT 
    COUNT(DISTINCT u.id_usuario) AS total_hombres
FROM usuarios u
WHERE u.genero = 'm'
AND u.id_usuario IN (
    SELECT DISTINCT e.id_usuario
    FROM escuchas e
    JOIN canciones c ON e.id_cancion = c.id_cancion
    JOIN artistas a ON c.id_artista = a.id_artista
    WHERE a.nombre_artista IN ('Janet Jackson', 'The Clash')
);

-- ============================================
-- CONSULTA 3: Número total de usuarios que o bien son de España (Spain) 
-- o bien han escuchado a 'Red Hot Chili Peppers'
-- ============================================
SELECT COUNT(*) AS total_usuarios
FROM (
    SELECT DISTINCT u.id_usuario
    FROM usuarios u
    WHERE u.pais = 'Spain'
    
    UNION
    
    SELECT DISTINCT e.id_usuario
    FROM escuchas e
    JOIN canciones c ON e.id_cancion = c.id_cancion
    JOIN artistas a ON c.id_artista = a.id_artista
    WHERE a.nombre_artista LIKE '%Red Hot Chili Peppers%'
) AS usuarios_combinados;

-- ============================================
-- CONSULTA 4: Promedio de escuchas por usuario para aquellos que tienen entre 19 y 21 años
-- (Incluyendo usuarios sin escuchas)
-- ============================================
SELECT 
    ROUND(AVG(COALESCE(escuchas_por_usuario, 0)), 2) AS promedio_escuchas
FROM (
    SELECT 
        u.id_usuario,
        COUNT(e.id_escucha) AS escuchas_por_usuario
    FROM usuarios u
    LEFT JOIN escuchas e ON u.id_usuario = e.id_usuario
    WHERE u.edad BETWEEN 19 AND 21
    GROUP BY u.id_usuario
) AS subconsulta;

-- ============================================
-- CONSULTA 5: Usuarios cuyo número total de escuchas supera la media del total de escuchas
-- ============================================
WITH media_escuchas AS (
    SELECT AVG(total) AS media
    FROM (
        SELECT COUNT(*) AS total
        FROM escuchas
        GROUP BY id_usuario
    ) AS totales
)
SELECT 
    u.id_usuario,
    u.id_lastfm_usuario,
    COUNT(e.id_escucha) AS total_escuchas,
    ROUND(m.media, 2) AS media_global
FROM usuarios u
JOIN escuchas e ON u.id_usuario = e.id_usuario
CROSS JOIN media_escuchas m
GROUP BY u.id_usuario, u.id_lastfm_usuario, m.media
HAVING total_escuchas > m.media
ORDER BY total_escuchas DESC;

-- ============================================
-- CONSULTA 6: Número total de escuchas por país
-- ============================================
SELECT 
    COALESCE(u.pais, 'Desconocido') AS pais,
    COUNT(e.id_escucha) AS total_escuchas,
    ROUND(COUNT(e.id_escucha) * 100.0 / SUM(COUNT(e.id_escucha)) OVER(), 2) AS porcentaje
FROM usuarios u
LEFT JOIN escuchas e ON u.id_usuario = e.id_usuario
GROUP BY u.pais
ORDER BY total_escuchas DESC;

-- ============================================
-- CONSULTA 7: Top 15 canciones con mayor número de usuarios distintos
-- ============================================
SELECT 
    c.nombre_cancion,
    a.nombre_artista,
    COUNT(DISTINCT e.id_usuario) AS usuarios_distintos,
    COUNT(e.id_escucha) AS total_escuchas
FROM canciones c
JOIN artistas a ON c.id_artista = a.id_artista
JOIN escuchas e ON c.id_cancion = e.id_cancion
GROUP BY c.id_cancion, c.nombre_cancion, a.nombre_artista
ORDER BY usuarios_distintos DESC
LIMIT 15;

-- ============================================
-- CONSULTA 8: Porcentaje de escuchas del total realizadas por usuarios 
-- cuya edad supera la media de edad (ignorando edad 0 o nula)
-- ============================================
WITH estadisticas AS (
    SELECT 
        AVG(edad) AS edad_media,
        SUM(CASE WHEN edad > (SELECT AVG(edad) FROM usuarios WHERE edad > 0) THEN 1 ELSE 0 END) AS escuchas_mayores,
        COUNT(*) AS total_escuchas
    FROM escuchas e
    JOIN usuarios u ON e.id_usuario = u.id_usuario
    WHERE u.edad > 0 AND u.edad IS NOT NULL
)
SELECT 
    ROUND(escuchas_mayores * 100.0 / total_escuchas, 2) AS porcentaje_escuchas_mayores_edad
FROM estadisticas;

