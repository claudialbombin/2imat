queries = {
    "pregunta1": 
"""
SELECT trayectos.PRECIO
FROM trayectos
ORDER BY trayectos.PRECIO DESC
LIMIT 1;
""",

    "pregunta2": 
"""
SELECT trayectos.CODTRAY
FROM trayectos
ORDER BY trayectos.PRECIO ASC
LIMIT 1;
""",

    "pregunta3": 
"""
SELECT CBILL
FROM billetes
LEFT JOIN trayectos on trayectos.CODTRAY = billetes.CODTRAY
WHERE PRECIO = (SELECT MAX(PRECIO)
				FROM trayectos);

""",

    "pregunta4": 
"""
SELECT CBILL
FROM billetes
LEFT JOIN trayectos ON trayectos.CODTRAY = billetes.CODTRAY
WHERE PRECIO > (SELECT AVG(PRECIO) FROM trayectos);
""",

    "pregunta5": 
"""
SELECT
	UPPER(SUBSTRING(ORIG, 1, 4)) AS orig_4,
    UPPER(SUBSTRING(DEST, 1, 4)) AS dest_4
FROM trayectos
WHERE LENGTH(ORIG) BETWEEN 4 AND 12
""",
    "pregunta6": 
"""
SELECT 
    t.CODTRAY,
    t.ORIG,
    t.DEST,
    COUNT(b.CBILL) AS cantidad_billetes
FROM trayectos t
LEFT JOIN billetes b ON t.CODTRAY = b.CODTRAY
GROUP BY t.CODTRAY, t.ORIG, t.DEST
HAVING COUNT(b.CBILL) = (
    SELECT MAX(ventas)
    FROM (SELECT COUNT(CBILL) AS ventas
        FROM billetes
        GROUP BY CODTRAY) 
        AS conteo_ventas);
""",
    "pregunta7": 
"""
SELECT 
    p.NOMBRE, 
    p.TLFN
FROM pasajeros p
INNER JOIN (SELECT 
        DNI,
        CODTRAY,
        COUNT(CBILL) AS cantidad_billetes
    FROM billetes
    GROUP BY DNI, CODTRAY) AS t ON p.DNI = t.DNI
WHERE t.cantidad_billetes = (
    SELECT MAX(cantidad)
    FROM (
        SELECT COUNT(CBILL) AS cantidad
        FROM billetes
        GROUP BY DNI, CODTRAY
    ) AS conteo
);
""",
    "pregunta8": 
"""
SELECT 
    a.MATRIC,
    COUNT(b.CBILL) AS total_billetes_vendidos
FROM autobuses a
LEFT JOIN billetes b ON a.MATRIC = b.MATRIC
WHERE b.CODTRAY IN (
    SELECT CODTRAY
    FROM trayectos
    WHERE PRECIO = (
        SELECT MIN(PRECIO)
        FROM trayectos
    )
)
GROUP BY a.MATRIC;
""",
    "pregunta9": 
"""
SELECT 
    p.DNI,
    p.NOMBRE,
    p.TLFN,
    COUNT(b.CBILL) AS total_billetes_comprados,
    COUNT(DISTINCT b.CODTRAY) AS trayectos_distintos_realizados
FROM pasajeros p
LEFT JOIN billetes b ON p.DNI = b.DNI
WHERE p.TLFN LIKE '63%'
GROUP BY p.DNI, p.NOMBRE, p.TLFN;
""",
    "pregunta10": 
"""
SELECT 
    p.*,
    COUNT(b.CBILL) AS total_billetes_comprados
FROM pasajeros p
LEFT JOIN billetes b ON p.DNI = b.DNI
GROUP BY p.DNI
HAVING COUNT(b.CBILL) = (
    SELECT MAX(total_billetes)
    FROM (
        SELECT COUNT(CBILL) AS total_billetes
        FROM billetes
        GROUP BY DNI
    ) AS conteos
);
""",
    "pregunta11": 
"""
SELECT 
    p.DNI,
    p.NOMBRE,
    b.CBILL
FROM pasajeros p
INNER JOIN billetes b ON p.DNI = b.DNI
INNER JOIN trayectos t ON b.CODTRAY = t.CODTRAY
WHERE t.PRECIO = (
    SELECT MAX(PRECIO)
    FROM trayectos
)
ORDER BY p.NOMBRE, b.CBILL;
""",
    "pregunta12": 
"""
SELECT 
    b.CBILL AS codigo_billete,
    b.CODTRAY AS codigo_trayecto,
    a.MATRIC AS matricula_autobus,
    a.NASIENTOS AS numero_asientos
FROM autobuses a
INNER JOIN billetes b ON a.MATRIC = b.MATRIC
WHERE a.ITV = '2007-02-05'  
  AND DATE(b.FECHA) = '2007-02-05' 
ORDER BY a.MATRIC, b.CBILL;
""",
    "pregunta13": 
"""
SELECT 
    t1.CODTRAY,
    t1.ORIGEN,
    t1.DESTINO,
    t1.PRECIO,
    (SELECT AVG(t2.PRECIO) 
     FROM trayectos t2 
     WHERE t2.ORIGEN = t1.ORIGEN) AS precio_medio_origen
FROM trayectos t1
WHERE t1.PRECIO < (
    SELECT AVG(t2.PRECIO)
    FROM trayectos t2
    WHERE t2.ORIGEN = t1.ORIGEN
)
ORDER BY t1.ORIGEN, t1.PRECIO;
""",
    "pregunta14": 
"""
SELECT 
    SUM(t.PRECIO) AS total_recaudado
FROM billetes b
INNER JOIN trayectos t ON b.CODTRAY = t.CODTRAY;
""",
    "pregunta15": 
"""
SELECT 
    b.CBILL AS codigo_billete,
    t.PRECIO AS precio
FROM billetes b
INNER JOIN trayectos t ON b.CODTRAY = t.CODTRAY
ORDER BY t.PRECIO ASC, b.CBILL DESC;
""",
    "pregunta16": 
"""
SELECT DISTINCT
    p.NOMBRE AS nombre_pasajero,
    p.TLFN AS telefono
FROM pasajeros p
INNER JOIN billetes b ON p.DNI = b.DNI
INNER JOIN trayectos t ON b.CODTRAY = t.CODTRAY
INNER JOIN autobuses a ON b.MATRIC = a.MATRIC
WHERE t.CODTRAY = 'CT-408'
  AND DATE(b.FECHA) = '2007-03-16'
  AND a.NASIENTOS > 50
ORDER BY p.NOMBRE;
""",
    "pregunta17": 
"""
SELECT 
    t.ORIG,
    COUNT(b.CBILL) AS total_billetes_vendidos
FROM trayectos t
INNER JOIN billetes b ON t.CODTRAY = b.CODTRAY
WHERE t.PRECIO > 30
GROUP BY t.ORIG
ORDER BY total_billetes_vendidos DESC;
""",
    "pregunta18": 
"""
SELECT 
    t.CODTRAY,
    t.ORIG,
    t.DEST,
    t.PRECIO AS "Precio",
    b.CBILL AS "Código Billete"
FROM 
    trayectos t
LEFT JOIN 
    billetes b ON t.CODTRAY = b.CODTRAY
ORDER BY 
    t.CODTRAY,
    b.CBILL;
""",
    "pregunta19": 
"""
SELECT 
    a.MATRIC AS "Matrícula",
    (a.NASIENTOS - COUNT(b.CBILL)) AS "Asientos Libres"
FROM 
    autobuses a
LEFT JOIN 
    billetes b ON a.MATRIC = b.MATRIC
               AND b.FECHA = '2024-12-25'  -- FECHA ESPECÍFICA
               AND b.HORA = '08:00:00'     -- HORA ESPECÍFICA
GROUP BY 
    a.MATRIC, a.NASIENTOS
ORDER BY 
    "Asientos Libres" DESC;
""",
    "pregunta20": 
"""
SELECT 
    t.CODTRAY,
    t.ORIG,
    t.DEST,
    b.FECHA AS DIA_MAX_VENTAS,
    COUNT(*) AS BILLETES_VENDIDOS
FROM trayectos t
JOIN billetes b ON t.CODTRAY = b.CODTRAY
GROUP BY t.CODTRAY, t.ORIG, t.DEST, b.FECHA
HAVING COUNT(*) = (
    SELECT MAX(ventas_dia)
    FROM (
        SELECT COUNT(*) AS ventas_dia
        FROM billetes b2
        WHERE b2.CODTRAY = t.CODTRAY
        GROUP BY b2.FECHA
    ) ventas_por_dia
)
ORDER BY BILLETES_VENDIDOS DESC;

""",
}

adicionales = {
    "adicional1":   
"""
SELECT 
    p.DNI,
    p.NOMBRE,
    b.FECHA,
    COUNT(DISTINCT b.CODTRAY) AS trayectos_diferentes,
    COUNT(b.CBILL) AS billetes_totales
FROM pasajeros p
JOIN billetes b ON p.DNI = b.DNI
GROUP BY p.DNI, p.NOMBRE, b.FECHA
ORDER BY b.FECHA DESC, trayectos_diferentes DESC;
""",
    "adicional2":
""" 
SELECT 
    t.CODTRAY,
    t.ORIG,
    t.DEST,
    b.FECHA,
    COUNT(*) AS total_billetes
FROM trayectos t
JOIN billetes b ON t.CODTRAY = b.CODTRAY
GROUP BY t.CODTRAY, t.ORIG, t.DEST, b.FECHA
HAVING COUNT(*) = (
    SELECT MAX(ventas)
    FROM (
        SELECT COUNT(*) AS ventas
        FROM billetes
        GROUP BY CODTRAY, FECHA
    ) AS max_ventas
)
ORDER BY total_billetes DESC, b.FECHA DESC;
""",
    "adicional3":
"""
SELECT 
    t.CODTRAY,
    b.FECHA,
    t.KM,
    COUNT(b.CBILL) AS billetes,
    COUNT(DISTINCT b.DNI) AS personas,
    ROUND(COUNT(b.CBILL) / GREATEST(COUNT(DISTINCT b.DNI), 1), 2) AS promedio
FROM trayectos t, billetes b
WHERE t.CODTRAY = b.CODTRAY
  AND t.KM > 400
GROUP BY t.CODTRAY, b.FECHA, t.KM
ORDER BY t.KM DESC, promedio DESC;
""",
    "adicional4":
"""
SELECT 
    ORIG,
    DEST,
    COUNT(DISTINCT CODTRAY) AS numero_trayectos,
    ROUND(AVG(PRECIO), 2) AS precio_medio,
    MAX(PRECIO) AS precio_maximo,
    MIN(PRECIO) AS precio_minimo,
    ROUND(MAX(PRECIO) - MIN(PRECIO), 2) AS diferencia_precios
FROM trayectos
WHERE KM <= 400
    AND ORIG != DEST 
GROUP BY ORIG, DEST
HAVING COUNT(DISTINCT CODTRAY) > 1  
ORDER BY numero_trayectos DESC, diferencia_precios DESC;
""",
    "adicional5":
"""
SELECT 
    t.CODTRAY,
    t.ORIG,
    t.DEST,
    b.FECHA,
    COUNT(b.CBILL) AS billetes_vendidos,
    SUM(t.PRECIO) AS ingresos_totales
FROM trayectos t
JOIN billetes b ON t.CODTRAY = b.CODTRAY
WHERE b.FECHA >= CURRENT_DATE - INTERVAL 2000 DAY
GROUP BY t.CODTRAY, t.ORIG, t.DEST, b.FECHA
ORDER BY b.FECHA DESC, billetes_vendidos DESC;
""",
    "adicional6":
"""
SELECT 
    t.CODTRAY,
    CONCAT(t.ORIG, ' - ', t.DEST) AS trayecto,
    DATE(b.FECHA) AS fecha,
    COUNT(b.CBILL) AS billetes_totales,
    COUNT(DISTINCT b.DNI) AS personas_unicas,
    ROUND(COUNT(b.CBILL) / COUNT(DISTINCT b.DNI), 2) AS media_billetes_por_persona
FROM trayectos t
JOIN billetes b ON t.CODTRAY = b.CODTRAY
GROUP BY t.CODTRAY, t.ORIG, t.DEST, DATE(b.FECHA)
HAVING media_billetes_por_persona > 3
ORDER BY media_billetes_por_persona DESC, fecha DESC;
"""
}