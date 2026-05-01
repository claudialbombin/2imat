queries = {
    "pregunta1": 
"""
SELECT ORIG, DEST, KM
FROM trayectos
WHERE KM > 150
ORDER BY KM ASC;
""",

    "pregunta2": 
"""
SELECT DISTINCT PRECIO
FROM trayectos
ORDER BY PRECIO DESC;
""",

    "pregunta3": 
"""
SELECT 
    autobuses.MATRIC,
    billetes.CBILL AS codigo_billete,
    billetes.FECHA,
    billetes.HORA
FROM autobuses
INNER JOIN billetes ON autobuses.MATRIC = billetes.MATRIC
ORDER BY 
    autobuses.MATRIC DESC,
    billetes.CBILL DESC,
    billetes.FECHA ASC,
    billetes.HORA ASC;
""",

    "pregunta4": 
"""
SELECT
		CBILL,
        FECHA,
        HORA
FROM billetes
WHERE billetes.MATRIC = '1234GKH' AND billetes.FECHA > '2007-01-02' AND billetes.FECHA < '2017-12-31'
ORDER BY CBILL ASC;
""",

    "pregunta5": 
"""
SELECT *
FROM pasajeros
ORDER BY pasajeros.NOMBRE ASC;
""",
    "pregunta6": 
"""
SELECT trayectos.CODTRAY
FROM trayectos 
LEFT JOIN billetes ON trayectos.CODTRAY = billetes.CODTRAY
WHERE billetes.CODTRAY IS NULL;
""",
    "pregunta7": 
"""
SELECT 
	autobuses.MATRIC,
    billetes.CBILL
FROM autobuses
JOIN billetes ON autobuses.MATRIC = billetes.MATRIC
WHERE autobuses.ITV = '2007-02-05' AND billetes.FECHA = '2007-02-05'
ORDER BY autobuses.MATRIC, billetes.CBILL;
""",
    "pregunta8": 
"""
SELECT DISTINCT pasajeros.NOMBRE
FROM pasajeros
LEFT JOIN billetes ON pasajeros.DNI = billetes.DNI
WHERE billetes.FECHA > '2017-11-11' AND billetes.FECHA < '2017-12-03' AND billetes.HORA = '09:00';
""",
    "pregunta9": 
"""
SELECT CODTRAY
FROM trayectos
ORDER BY trayectos.KM. DESC
LIMIT 1;
""",
    "pregunta10": 
"""
SELECT 
	pasajeros.DNI,
    billetes.CBILL
FROM pasajeros
LEFT JOIN billetes ON pasajeros.DNI = billetes.DNI
WHERE pasajeros.nombre LIKE '%PEREZ%';
""",
    "pregunta11": 
"""
SELECT *
FROM trayectos 
WHERE trayectos.CODTRAY = 'CT-403'
    AND EXISTS (
        SELECT 1 
        FROM billetes  
        WHERE billetes.CODTRAY = trayectos.CODTRAY
    );
""",
    "pregunta12": 
"""
SELECT *
FROM trayectos 
WHERE trayectos.CODTRAY = 'CT-403'
    AND EXISTS (
        SELECT 1 
        FROM billetes  
        WHERE billetes.CODTRAY = 'CT-405'
    );
""",
    "pregunta13": 
"""
SELECT DISTINCT NOMBRE, pasajeros.DNI
FROM pasajeros
LEFT JOIN billetes ON pasajeros.DNI = billetes.DNI
WHERE billetes.MATRIC = '5482FDH' AND billetes.FECHA <> '2007-03-16';
""",
    "pregunta14": 
"""
SELECT COUNT(*) AS total_billetes
FROM billetes;
""",
    "pregunta15": 
"""
SELECT 
    MAX(precio) AS precio_mas_caro,
    MIN(precio) AS precio_mas_barato,
    AVG(precio) AS precio_medio
FROM trayectos;
""",
}

queries_opcionales={
    'extra1':
'''
SELECT 
    billetes.CBILL,
    YEAR(billetes.FECHA) AS año_compra
FROM billetes 
INNER JOIN pasajeros ON billetes.DNI = pasajeros.DNI
WHERE pasajeros.NOMBRE LIKE '%PEREZ%' AND (billetes.MATRIC LIKE '1___%G%' OR billetes.MATRIC LIKE '1___%D%')
ORDER BY YEAR(billetes.FECHA) DESC;
''',
    'extra2':
'''
SELECT DISTINCT NOMBRE
FROM pasajeros
LEFT JOIN billetes ON pasajeros.DNI = billetes.DNI
WHERE pasajeros.TLFN LIKE '91%' AND billetes.FECHA > '2017-08-02' AND billetes.FECHA < '2017-08-15';
''',
    'extra3':
'''
SELECT *
FROM trayectos
WHERE trayectos.ORIG LIKE 'MAD%'
ORDER BY trayectos.PRECIO ASC
LIMIT 1;
''',
    'extra4':
'''
SELECT DISTINCT
	pasajeros.DNI,
    pasajeros.NOMBRE
FROM pasajeros
LEFT JOIN billetes ON billetes.DNI = pasajeros.DNI
LEFT JOIN trayectos ON billetes.CODTRAY = trayectos.CODTRAY
WHERE trayectos.DEST LIKE 'ZARAGOZA';
''',
    'extra5':
'''
SELECT 
	trayectos.ORIG,
    trayectos.DEST
FROM trayectos
LEFT JOIN billetes ON billetes.CODTRAY = trayectos.CODTRAY
WHERE billetes.MATRIC LIKE '1%' AND YEAR(billetes.FECHA) LIKE '2017';
''',
}