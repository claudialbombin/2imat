"""
Práctica 4 - Benchmarking SQL
Análisis de rendimiento de consultas SQL optimizadas vs no optimizadas
"""

import pymysql
import time
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la conexión - CAMBIA ESTOS DATOS
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Carlota.22',
    'database': 'employees',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_connection():
    """Establece y devuelve una conexión a la base de datos"""
    return pymysql.connect(**DB_CONFIG)

def obtener_usuarios():
    """
    Obtiene los 200 primeros nombres propios distintos de la tabla employees
    ordenados alfabéticamente.
    
    Returns:
        list: Lista con los 200 primeros nombres distintos ordenados
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    # Consulta para obtener nombres distintos, ordenados y limitados a 200
    query = """
        SELECT DISTINCT first_name 
        FROM employees 
        ORDER BY first_name 
        LIMIT 200
    """
    
    cursor.execute(query)
    resultados = cursor.fetchall()
    
    # Extraer los nombres en una lista
    usuarios = [row['first_name'] for row in resultados]
    
    cursor.close()
    connection.close()
    
    return usuarios

def benchmark_salarios():
    """
    Mide el tiempo de ejecución de consultas de salarios para cada uno de los 
    200 usuarios obtenidos de la tabla employees.
    
    Compara:
        - Versión sin optimizar (SELECT * con JOIN implícito)
        - Versión optimizada (solo campos necesarios, JOIN explícito)
    """
    # Obtener los 200 usuarios (esto NO se mide)
    print("Obteniendo lista de usuarios...")
    usuarios = obtener_usuarios()
    print(f"Se han obtenido {len(usuarios)} usuarios para el benchmark\n")
    
    # Conexión a la base de datos
    connection = get_connection()
    
    # CONSULTA SIN OPTIMIZAR
    # Versión original: SELECT * con JOIN implícito en WHERE
    query_no_optimizada = """
        SELECT * 
        FROM employees, salaries 
        WHERE employees.emp_no = salaries.emp_no 
        AND employees.first_name = %s
    """
    
    print("Ejecutando consulta sin optimizar para 200 usuarios...")
    inicio_tiempo = time.time()
    
    cursor = connection.cursor()
    for usuario in usuarios:
        cursor.execute(query_no_optimizada, (usuario,))
        # Consumimos todos los resultados para asegurar que la consulta se ejecuta completamente
        # resultados = cursor.fetchall()
    cursor.close()
    
    tiempo_no_optimizado = time.time() - inicio_tiempo
    
    # CONSULTA OPTIMIZADA (sin índices)
    # Versión optimizada:
    # - Selecciona solo las columnas necesarias (emp_no, salary, from_date, to_date)
    # - Usa INNER JOIN explícito (más legible y optimizable por el motor)
    # - Mantiene la misma funcionalidad pero con menos datos transferidos
    query_optimizada = """
        SELECT employees.emp_no, salary, salaries.from_date, salaries.to_date
        FROM employees 
        INNER JOIN salaries ON employees.emp_no = salaries.emp_no 
        WHERE employees.first_name = %s
    """
    
    print("Ejecutando consulta optimizada para 200 usuarios...")
    inicio_tiempo = time.time()
    
    cursor = connection.cursor()
    for usuario in usuarios:
        cursor.execute(query_optimizada, (usuario,))
        # Consumimos resultados
        # resultados = cursor.fetchall()
    cursor.close()
    
    tiempo_optimizado = time.time() - inicio_tiempo
    
    # Cerrar conexión
    connection.close()
    


    print("RESULTADOS BENCHMARK SALARIOS - APARTADO 2.1")

    print(f"Tiempo empleado en la query sin optimizar (salarios): {tiempo_no_optimizado:.6f} segundos")
    print(f"Tiempo empleado en la query optimizando (salarios): {tiempo_optimizado:.6f} segundos")
    
    # Calcular mejora
    mejora = ((tiempo_no_optimizado - tiempo_optimizado) / tiempo_no_optimizado) * 100
    print(f"Mejora: {mejora:.2f}%")

    
    return {
        'sin_optimizar': tiempo_no_optimizado,
        'optimizado': tiempo_optimizado
    }

def benchmark_departamentos():
    """
    Consulta empleados de departamentos específicos:
    'Development', 'Marketing', 'Sales', 'Customer Service'
    
    Version sin optimizar: Solo operadores basicos (SELECT, WHERE, FROM, OR/AND, =)
    Version optimizada: Usa IN, JOINs explicitos y selecciona solo campos necesarios
    
    Ejecuta cada version 5 veces y muestra el tiempo promedio.
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    print("APARTADO 2.2 - Benchmark Departamentos")
    
    # VERSION SIN OPTIMIZAR
    query_no_optimizada = """
        SELECT * 
        FROM employees, dept_emp, departments 
        WHERE employees.emp_no = dept_emp.emp_no 
        AND dept_emp.dept_no = departments.dept_no
        AND (
            departments.dept_name = 'Development' 
            OR departments.dept_name = 'Marketing' 
            OR departments.dept_name = 'Sales' 
            OR departments.dept_name = 'Customer Service'
        )
    """
    
    print("\nEjecutando consulta SIN OPTIMIZAR (5 veces)...")
    tiempos_no_opt = []
    
    for i in range(5):
        print(f"  Ejecucion {i+1}/5...", end=" ", flush=True)
        inicio = time.time()
        cursor.execute(query_no_optimizada)
        tiempo_ejecucion = time.time() - inicio
        tiempos_no_opt.append(tiempo_ejecucion)
        print(f"{tiempo_ejecucion:.6f} segundos")
    
    tiempo_promedio_no_opt = sum(tiempos_no_opt) / len(tiempos_no_opt)
    
    # VERSION OPTIMIZADA
    """
    Optimizaciones aplicadas:
    - IN en lugar de OR: Simplifica la condicion y mejora la eficiencia
    - JOIN explicitos: Mejor planificacion de la ejecucion por el optimizador
    - Seleccion de columnas especificas: Reduce datos transferidos
    """
    query_optimizada = """
        SELECT e.first_name, e.last_name, e.hire_date
        FROM employees e
        INNER JOIN dept_emp de ON e.emp_no = de.emp_no
        INNER JOIN departments d ON de.dept_no = d.dept_no
        WHERE d.dept_name IN ('Development', 'Marketing', 'Sales', 'Customer Service')
    """
    
    print("\nEjecutando consulta OPTIMIZADA (5 veces)...")
    tiempos_opt = []
    
    for i in range(5):
        print(f"  Ejecucion {i+1}/5...", end=" ", flush=True)
        inicio = time.time()
        cursor.execute(query_optimizada)

        tiempo_ejecucion = time.time() - inicio
        tiempos_opt.append(tiempo_ejecucion)
        print(f"{tiempo_ejecucion:.6f} segundos")
    
    tiempo_promedio_opt = sum(tiempos_opt) / len(tiempos_opt)
    
    cursor.close()
    connection.close()
    
    # MOSTRAR RESULTADOS
    print("RESULTADOS BENCHMARK DEPARTAMENTOS")
    print(f"Tiempo sin optimizar (promedio 5 ejecuciones): {tiempo_promedio_no_opt:.6f} segundos")
    print(f"Tiempo optimizado (promedio 5 ejecuciones):    {tiempo_promedio_opt:.6f} segundos")
    
    mejora = ((tiempo_promedio_no_opt - tiempo_promedio_opt) / tiempo_promedio_no_opt) * 100
    print(f"Mejora: {mejora:.2f}%")
    
    return {
        'sin_optimizar': tiempo_promedio_no_opt,
        'optimizado': tiempo_promedio_opt
    }

def benchmarking_fecha_contratacion():
    """
    Consulta empleados por departamentos especificos y rangos de fechas (1990-1999).
    Departamentos: 'Development', 'Marketing', 'Sales', 'Customer Service', 'Quality Management'
    
    Version sin optimizar: Usa HAVING para filtrar fechas y solo operadores basicos
    Version optimizada: Usa WHERE con BETWEEN y NOT HAVING, JOINs explicitos
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    print("APARTADO 2.3 - Benchmark Fecha Contratacion")
    
    # Definir los departamentos a consultar
    departamentos = ['Development', 'Marketing', 'Sales', 'Customer Service', 'Quality Management']
    
    # Definir los rangos de años (1990-1991, 1991-1992, ..., 1998-1999)
    rangos = []
    for año in range(1990, 1999):
        rangos.append((f"{año}-01-01", f"{año+1}-12-31"))
    
    # VERSION SIN OPTIMIZAR
    # Solo usando SELECT, WHERE, FROM, OR/AND y el operador = con HAVING
    query_no_optimizada = """
        SELECT e.first_name, e.last_name, e.hire_date
        FROM employees e, dept_emp de, departments d
        WHERE e.emp_no = de.emp_no 
        AND de.dept_no = d.dept_no
        AND (
            d.dept_name = 'Development' 
            OR d.dept_name = 'Marketing' 
            OR d.dept_name = 'Sales' 
            OR d.dept_name = 'Customer Service'
            OR d.dept_name = 'Quality Management'
        )
        HAVING YEAR(e.hire_date) = %s OR YEAR(e.hire_date) = %s
    """
    
    print("\nEjecutando consulta SIN OPTIMIZAR (con HAVING)...")
    inicio_total_no_opt = time.time()
    
    for i, (fecha_inicio, fecha_fin) in enumerate(rangos, 1):
        año_inicio = fecha_inicio[:4]
        año_fin = fecha_fin[:4]
        print(f"  Rango {i}: {año_inicio}-{año_fin}...", end=" ", flush=True)
        
        inicio = time.time()
        cursor.execute(query_no_optimizada, (año_inicio, año_fin))
        resultados = cursor.fetchall()
        fin = time.time()
        
        print(f"{len(resultados)} resultados - {fin-inicio:.4f} segundos")
    
    tiempo_total_no_opt = time.time() - inicio_total_no_opt
    
    # VERSION OPTIMIZADA
    """
    Optimizaciones aplicadas en la version optimizada:
    
    - BETWEEN en lugar de HAVING: Filtrar fechas en WHERE es mas eficiente que usar HAVING,
      ya que HAVING evalua el filtro despues de recuperar los datos, mientras que WHERE
      lo hace antes, reduciendo el conjunto de resultados temprano.
    
    - IN en lugar de multiples OR: Simplifica la condicion y permite busqueda optimizada.
    
    - JOINs explicitos: Mejor control sobre como se realizan las combinaciones.
    
    - Parametrizacion directa de fechas: Usar BETWEEN con fechas completas en lugar de
      YEAR() permite utilizar indices si existieran (aunque no se usan indices en este caso).
    """
    query_optimizada = """
        SELECT e.first_name, e.last_name, e.hire_date
        FROM employees e
        INNER JOIN dept_emp de ON e.emp_no = de.emp_no
        INNER JOIN departments d ON de.dept_no = d.dept_no
        WHERE d.dept_name IN ('Development', 'Marketing', 'Sales', 
                             'Customer Service', 'Quality Management')
        AND e.hire_date BETWEEN %s AND %s
    """
    
    print("\nEjecutando consulta OPTIMIZADA (con WHERE y BETWEEN)...")
    inicio_total_opt = time.time()
    
    for i, (fecha_inicio, fecha_fin) in enumerate(rangos, 1):
        año_inicio = fecha_inicio[:4]
        año_fin = fecha_fin[:4]
        print(f"  Rango {i}: {año_inicio}-{año_fin}...", end=" ", flush=True)
        
        inicio = time.time()
        cursor.execute(query_optimizada, (fecha_inicio, fecha_fin))
        resultados = cursor.fetchall()
        fin = time.time()
        
        print(f"{len(resultados)} resultados - {fin-inicio:.4f} segundos")
    
    tiempo_total_opt = time.time() - inicio_total_opt
    
    cursor.close()
    connection.close()
    
    # MOSTRAR RESULTADOS
    print("RESULTADOS BENCHMARK FECHA CONTRATACION")
    print(f"Tiempo empleado en la query sin optimizar (fecha contratacion): {tiempo_total_no_opt:.6f} segundos")
    print(f"Tiempo empleado en la query optimizando (fecha contratacion): {tiempo_total_opt:.6f} segundos")
    
    mejora = ((tiempo_total_no_opt - tiempo_total_opt) / tiempo_total_no_opt) * 100
    print(f"Mejora: {mejora:.2f}%")
    
    return {
        'sin_optimizar': tiempo_total_no_opt,
        'optimizado': tiempo_total_opt
    }

def benchmarking_titulos_usuarios_indice():
    """
    Obtiene los titulos de cada uno de los 200 usuarios junto con nombre,
    apellido, from_date y to_date.
    
    Primero ejecuta sin indices, luego crea indices, ejecuta con indices,
    elimina indices y compara tiempos incluyendo la creacion y eliminacion.
    """
    # Obtener los 200 usuarios (esto no se mide)
    print("\nObteniendo lista de usuarios...")
    usuarios = obtener_usuarios()
    print(f"Se han obtenido {len(usuarios)} usuarios")
    
    connection = get_connection()
    cursor = connection.cursor()

    print("APARTADO 2.4 - Benchmark Titulos con Indices")

    # VERSION SIN INDICES
    """
    Consulta sin indices:
    - Realiza JOIN entre employees y titles por emp_no
    - Sin indices, realiza scans completos de tablas
    """
    query = """
        SELECT e.first_name, e.last_name, t.title, t.from_date, t.to_date
        FROM employees e
        INNER JOIN titles t ON e.emp_no = t.emp_no
        WHERE e.first_name = %s
    """
    
    print("\nEjecutando consulta SIN INDICES para 200 usuarios...")
    inicio_sin_indices = time.time()
    
    for i, usuario in enumerate(usuarios, 1):
        cursor.execute(query, (usuario,))
        resultados = cursor.fetchall()
        if i % 50 == 0:
            print(f"  Progreso: {i}/200 usuarios")
    
    tiempo_sin_indices = time.time() - inicio_sin_indices
    print(f"Tiempo sin indices: {tiempo_sin_indices:.6f} segundos")
    
    # VERSION OPTIMIZADA
    """
    Indices creados para optimizar:
    
    - Indice en employees(first_name): Acelera la busqueda de empleados por nombre,
      que es la condicion principal del WHERE. Reduce drásticamente las filas a examinar.
    
    - Indice en titles(emp_no): Optimiza el JOIN con employees al permitir acceso directo
      a los titulos de cada empleado sin recorrer toda la tabla.
    
    - Indice compuesto en titles(emp_no, from_date): Mejora la ordenacion y recuperacion
      de los periodos de titulos para cada empleado.
    
    Se mide el tiempo TOTAL incluyendo: creacion de indices + ejecucion de consultas +
    eliminacion de indices para evaluar el beneficio real considerando el overhead.
    """
    
    print("\nCreando indices y ejecutando consultas CON INDICES...")
    inicio_con_indices = time.time()
    
    # Crear indices
    print("  Creando indices...", end=" ", flush=True)
    try:
        # Indice para busqueda por nombre
        cursor.execute("CREATE INDEX idx_employees_first_name ON employees(first_name)")
        
        # Indice para JOIN con titles
        cursor.execute("CREATE INDEX idx_titles_emp_no ON titles(emp_no)")
        
        # Indice compuesto adicional para mejorar rendimiento
        cursor.execute("CREATE INDEX idx_titles_emp_no_dates ON titles(emp_no, from_date, to_date)")
        
        connection.commit()
        print("OK")
    except Exception as e:
        print(f"Error creando indices: {e}")
    
    # Ejecutar consultas con indices
    print("  Ejecutando consultas para 200 usuarios...")
    for i, usuario in enumerate(usuarios, 1):
        cursor.execute(query, (usuario,))
        resultados = cursor.fetchall()
        if i % 50 == 0:
            print(f"    Progreso: {i}/200 usuarios")
    
    # Eliminar indices
    print("  Eliminando indices...", end=" ", flush=True)
    try:
        cursor.execute("DROP INDEX idx_employees_first_name ON employees")
        cursor.execute("DROP INDEX idx_titles_emp_no ON titles")
        cursor.execute("DROP INDEX idx_titles_emp_no_dates ON titles")
        connection.commit()
        print("OK")
    except Exception as e:
        print(f"Error eliminando indices: {e}")
    
    tiempo_con_indices = time.time() - inicio_con_indices
    
    cursor.close()
    connection.close()

    # MOSTRAR RESULTADOS
    print("RESULTADOS BENCHMARK TITULOS")
    print(f"Tiempo empleado en la query sin indices (titulos usuarios): {tiempo_sin_indices:.6f} segundos")
    print(f"Tiempo empleado en la query con indices (titulos usuarios): {tiempo_con_indices:.6f} segundos")
    
    mejora = ((tiempo_sin_indices - tiempo_con_indices) / tiempo_sin_indices) * 100
    print(f"Mejora: {mejora:.2f}%")
    
    return {
        'sin_optimizar': tiempo_sin_indices,
        'optimizado': tiempo_con_indices
    }

def benchmark_salarios_superiores_media():
    """
    Obtiene empleados con salario actual (to_date = '9999-01-01') que:
    - Tienen salario entre dos años determinados (por from_date)
    - El salario es superior a la media de todos los salarios actuales
    
    Ejecuta para rangos: 1990-1991, 1991-1992, ..., 2002-2003
    
    Version sin optimizar: Sin indices ni vistas
    Version optimizada: Con indices y vista para calcular la media
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    print("APARTADO 2.5 - Benchmark Salarios Superiores a Media")
    
    # Definir rangos de años (1990-1991 hasta 2002-2003)
    rangos = []
    for año in range(1990, 2003):
        rangos.append((f"{año}-01-01", f"{año+1}-01-01"))
    
    # VERSION SIN OPTIMIZAR
    """
    Version sin optimizar:
    - Calcula la subconsulta de media para cada fila
    - Sin indices, realiza scans completos
    - JOIN implicito en WHERE
    """
    query_no_optimizada = """
        SELECT e.emp_no, e.first_name, e.last_name, s.from_date
        FROM employees e, salaries s
        WHERE e.emp_no = s.emp_no
        AND s.to_date = '9999-01-01'
        AND s.from_date BETWEEN %s AND %s
        AND s.salary > (
            SELECT AVG(salary)
            FROM salaries
            WHERE to_date = '9999-01-01'
        )
    """
    
    print("\nEjecutando consulta SIN OPTIMIZAR (sin indices ni vistas)...")
    inicio_total_no_opt = time.time()
    
    for i, (fecha_inicio, fecha_fin) in enumerate(rangos, 1):
        año_inicio = fecha_inicio[:4]
        año_fin = fecha_fin[:4]
        print(f"  Rango {i}: {año_inicio}-{año_fin}...", end=" ", flush=True)
        
        inicio = time.time()
        cursor.execute(query_no_optimizada, (fecha_inicio, fecha_fin))
        resultados = cursor.fetchall()
        fin = time.time()
        
        print(f"{len(resultados)} resultados - {fin-inicio:.4f} segundos")
    
    tiempo_total_no_opt = time.time() - inicio_total_no_opt
    print(f"Tiempo total sin optimizar: {tiempo_total_no_opt:.6f} segundos")
    
    # VERSION OPTIMIZADA
    """
    Optimizaciones aplicadas:
    
    - Vista current_salaries: Materializa los salarios actuales para no repetir
      el filtro to_date='9999-01-01' en cada consulta y subconsulta.
    
    - Indice en salaries(to_date): Acelera la creacion de la vista al filtrar
      rapidamente los salarios actuales.
    
    - Indice en salaries(emp_no, from_date, salary): Optimiza las busquedas por
      rango de fechas y la comparacion de salario.
    
    - Indice en employees(emp_no): Acelera el JOIN final.
    
    - JOIN explicito y calculo de media una sola vez (no por cada fila).
    
    Se incluye el tiempo de creacion y eliminacion de todos los elementos auxiliares.
    """
    
    print("VERSION OPTIMIZADA (con indices y vista)")
    
    inicio_total_opt = time.time()
    
    # 1. Crear indices para optimizar la creacion de la vista y consultas posteriores
    print("\n1. Creando indices...")
    try:
        inicio = time.time()
        cursor.execute("CREATE INDEX idx_salaries_to_date ON salaries(to_date)")
        cursor.execute("CREATE INDEX idx_salaries_emp_no_dates ON salaries(emp_no, from_date, salary)")
        cursor.execute("CREATE INDEX idx_employees_emp_no ON employees(emp_no)")
        connection.commit()
        print(f"   Indices creados en {time.time() - inicio:.4f} segundos")
    except Exception as e:
        print(f"   Error creando indices: {e}")
    
    # 2. Crear vista de salarios actuales
    print("\n2. Creando vista current_salaries...")
    try:
        inicio = time.time()
        cursor.execute("""
            CREATE VIEW current_salaries AS
            SELECT emp_no, salary, from_date
            FROM salaries
            WHERE to_date = '9999-01-01'
        """)
        connection.commit()
        print(f"   Vista creada en {time.time() - inicio:.4f} segundos")
    except Exception as e:
        print(f"   Error creando vista: {e}")
    
    # 3. Consulta optimizada usando la vista
    print("\n3. Ejecutando consultas optimizadas para 14 rangos...")
    
    # Pre-calcular la media una sola vez
    cursor.execute("SELECT AVG(salary) as media FROM current_salaries")
    media_salarios = cursor.fetchone()['media']
    print(f"   Media de salarios actuales calculada: {media_salarios:.2f}")
    
    query_optimizada = """
        SELECT e.emp_no, e.first_name, e.last_name, cs.from_date
        FROM employees e
        INNER JOIN current_salaries cs ON e.emp_no = cs.emp_no
        WHERE cs.from_date BETWEEN %s AND %s
        AND cs.salary > %s
    """
    
    for i, (fecha_inicio, fecha_fin) in enumerate(rangos, 1):
        año_inicio = fecha_inicio[:4]
        año_fin = fecha_fin[:4]
        print(f"  Rango {i}: {año_inicio}-{año_fin}...", end=" ", flush=True)
        
        inicio = time.time()
        cursor.execute(query_optimizada, (fecha_inicio, fecha_fin, media_salarios))
        resultados = cursor.fetchall()
        fin = time.time()
        
        print(f"{len(resultados)} resultados - {fin-inicio:.4f} segundos")
    
    # 4. Limpiar: eliminar vista e indices
    print("\n4. Limpiando elementos auxiliares...")
    try:
        inicio = time.time()
        cursor.execute("DROP VIEW IF EXISTS current_salaries")
        cursor.execute("DROP INDEX idx_salaries_to_date ON salaries")
        cursor.execute("DROP INDEX idx_salaries_emp_no_dates ON salaries")
        cursor.execute("DROP INDEX idx_employees_emp_no ON employees")
        connection.commit()
        print(f"   Elementos eliminados en {time.time() - inicio:.4f} segundos")
    except Exception as e:
        print(f"   Error eliminando elementos: {e}")
    
    tiempo_total_opt = time.time() - inicio_total_opt
    
    cursor.close()
    connection.close()

    # MOSTRAR RESULTADOS
    print("RESULTADOS BENCHMARK SALARIOS SUPERIORES A MEDIA")
    print(f"Tiempo empleado en la query sin optimizar (media salarios): {tiempo_total_no_opt:.6f} segundos")
    print(f"Tiempo empleado en la query optimizada (media salarios): {tiempo_total_opt:.6f} segundos")
    
    mejora = ((tiempo_total_no_opt - tiempo_total_opt) / tiempo_total_no_opt) * 100
    print(f"Mejora: {mejora:.2f}%")
    
    return {
        'sin_optimizar': tiempo_total_no_opt,
        'optimizado': tiempo_total_opt
    }

def substr_vs_like():
    """
    Compara dos enfoques para buscar usuarios cuyos dos primeros caracteres
    del nombre coincidan con los de cada usuario de la lista de 200.
    
    Version sin optimizar: Usa SUBSTR (no puede usar indices)
    Version optimizada: Usa LIKE con indices en columna generada
    """
    # Obtener los 200 usuarios (esto no se mide)
    print("\nObteniendo lista de usuarios...")
    usuarios = obtener_usuarios()
    print(f"Se han obtenido {len(usuarios)} usuarios")
    
    connection = get_connection()
    cursor = connection.cursor()
    
    print("APARTADO 2.6 - SUBSTR vs LIKE")
    
    # ============================================
    # VERSION SIN OPTIMIZAR (SUBSTR)
    # ============================================
    """
    Version con SUBSTR:
    - Usa la funcion SUBSTR para extraer los dos primeros caracteres
    - No puede usar indices aunque existan porque aplica funcion sobre la columna
    - Realiza scan completo de la tabla para cada consulta
    """
    query_substr = """
        SELECT first_name, birth_date, gender
        FROM employees
        WHERE SUBSTR(first_name, 1, 2) = SUBSTR(%s, 1, 2)
    """
    
    print("\nEjecutando consulta con SUBSTR (sin indices)...")
    inicio_substr = time.time()
    
    for i, usuario in enumerate(usuarios, 1):
        cursor.execute(query_substr, (usuario,))
        resultados = cursor.fetchall()
        if i % 50 == 0:
            print(f"  Progreso: {i}/200 usuarios")
    
    tiempo_substr = time.time() - inicio_substr
    print(f"Tiempo con SUBSTR: {tiempo_substr:.6f} segundos")
    
    # ============================================
    # VERSION OPTIMIZADA (LIKE con indices)
    # ============================================
    """
    Optimizaciones aplicadas:
    
    - Columna generada first_name_prefix: Almacena el prefijo de 2 caracteres
      de cada nombre. Al ser STORED, se persiste en disco y se puede indexar.
    
    - Indice en la columna generada: Permite busqueda directa por prefijo sin
      recorrer toda la tabla.
    
    - Consulta con LIKE: Aprovecha el indice en first_name_prefix cuando
      el comodin esta al final.
    
    - Se incluye el tiempo de creacion de la columna generada, el indice,
    y su posterior eliminacion en la medicion total.
    """
    
    print("VERSION OPTIMIZADA (LIKE con indices)")
    
    inicio_like = time.time()
    
    # 1. Anadir columna generada para el prefijo
    print("\n1. Anadiendo columna generada first_name_prefix...")
    try:
        cursor.execute("""
            ALTER TABLE employees 
            ADD COLUMN first_name_prefix VARCHAR(2) 
            GENERATED ALWAYS AS (LEFT(first_name, 2)) STORED
        """)
        connection.commit()
        print("   Columna generada creada")
    except Exception as e:
        print(f"   Error creando columna generada: {e}")
    
    # 2. Crear indice en la columna generada
    print("\n2. Creando indice en first_name_prefix...")
    try:
        cursor.execute("CREATE INDEX idx_first_name_prefix ON employees(first_name_prefix)")
        connection.commit()
        print("   Indice creado")
    except Exception as e:
        print(f"   Error creando indice: {e}")
    
    # 3. Consulta con LIKE (aprovecha el indice)
    print("\n3. Ejecutando consultas con LIKE para 200 usuarios...")
    
    # CORREGIDO: Usamos parametro con el prefijo ya calculado en Python
    query_like = """
        SELECT first_name, birth_date, gender
        FROM employees
        WHERE first_name LIKE %s
    """
    
    for i, usuario in enumerate(usuarios, 1):
        # Calcular el prefijo en Python y anadir el %
        prefijo = usuario[:2] + '%'
        cursor.execute(query_like, (prefijo,))
        resultados = cursor.fetchall()
        if i % 50 == 0:
            print(f"  Progreso: {i}/200 usuarios")
    
    # 4. Limpiar: eliminar indice y columna generada
    print("\n4. Limpiando elementos auxiliares...")
    try:
        cursor.execute("DROP INDEX idx_first_name_prefix ON employees")
        cursor.execute("ALTER TABLE employees DROP COLUMN first_name_prefix")
        connection.commit()
        print("   Elementos eliminados")
    except Exception as e:
        print(f"   Error eliminando elementos: {e}")
    
    tiempo_like = time.time() - inicio_like
    
    cursor.close()
    connection.close()
    
    # ============================================
    # MOSTRAR RESULTADOS
    # ============================================
    print("RESULTADOS SUBSTR vs LIKE")
    print(f"Tiempo empleado en la query sin optimizar (SUBSTR): {tiempo_substr:.6f} segundos")
    print(f"Tiempo empleado en la query optimizando (LIKE + indices): {tiempo_like:.6f} segundos")
    
    mejora = ((tiempo_substr - tiempo_like) / tiempo_substr) * 100
    print(f"Mejora: {mejora:.2f}%")
    
    return {
        'sin_optimizar': tiempo_substr,
        'optimizado': tiempo_like
    }

def consulta_adicional():
    """
    Consulta adicional para la parte opcional.
    Encuentra empleados que han tenido mas de un titulo en la empresa
    y que actualmente siguen trabajando (to_date = '9999-01-01' en salaries)
    """
    connection = get_connection()
    cursor = connection.cursor()

    print("CONSULTA ADICIONAL - Empleados con multiples titulos")
    
    # ============================================
    # VERSION SIN OPTIMIZAR
    # ============================================
    """
    Version sin optimizar:
    - Subconsultas multiples
    - JOINs implicitos
    - Calculo repetido
    """
    query_no_optimizada = """
        SELECT e.emp_no, e.first_name, e.last_name, 
               COUNT(DISTINCT t.title) as num_titulos,
               MIN(t.from_date) as primer_titulo,
               MAX(t.to_date) as ultimo_titulo
        FROM employees e, titles t, salaries s
        WHERE e.emp_no = t.emp_no 
        AND e.emp_no = s.emp_no
        AND s.to_date = '9999-01-01'
        GROUP BY e.emp_no
        HAVING COUNT(DISTINCT t.title) > 1
        ORDER BY num_titulos DESC
        LIMIT 50
    """
    
    print("\nEjecutando consulta SIN OPTIMIZAR...")
    inicio = time.time()
    cursor.execute(query_no_optimizada)
    resultados = cursor.fetchall()
    tiempo_no_opt = time.time() - inicio
    print(f"  {len(resultados)} resultados obtenidos")
    print(f"  Tiempo: {tiempo_no_opt:.6f} segundos")
    
    # ============================================
    # VERSION OPTIMIZADA
    # ============================================
    """
    Optimizaciones aplicadas:
    
    - CTE (WITH) para empleados actuales: Aísla los empleados que trabajan actualmente
    - JOINs explicitos: Mejor plan de ejecucion
    - Indices temporales: Acelera joins y agrupaciones
    - Subconsulta correlacionada optimizada
    """
    
    inicio_opt = time.time()
    
    # Crear indices temporales
    print("\nCreando indices temporales...")
    try:
        cursor.execute("CREATE INDEX idx_salaries_current ON salaries(to_date, emp_no)")
        cursor.execute("CREATE INDEX idx_titles_emp_no_dates ON titles(emp_no, from_date, to_date)")
        cursor.execute("CREATE INDEX idx_employees_emp_no ON employees(emp_no)")
        connection.commit()
        print("  Indices creados")
    except Exception as e:
        print(f"  Error creando indices: {e}")
    
    # Consulta optimizada con CTE
    query_optimizada = """
        WITH empleados_actuales AS (
            SELECT DISTINCT emp_no
            FROM salaries
            WHERE to_date = '9999-01-01'
        ),
        titulos_empleado AS (
            SELECT t.emp_no, 
                   COUNT(DISTINCT t.title) as num_titulos,
                   MIN(t.from_date) as primer_titulo,
                   MAX(t.to_date) as ultimo_titulo
            FROM titles t
            INNER JOIN empleados_actuales ea ON t.emp_no = ea.emp_no
            GROUP BY t.emp_no
            HAVING COUNT(DISTINCT t.title) > 1
        )
        SELECT e.emp_no, e.first_name, e.last_name,
               te.num_titulos, te.primer_titulo, te.ultimo_titulo
        FROM employees e
        INNER JOIN titulos_empleado te ON e.emp_no = te.emp_no
        ORDER BY te.num_titulos DESC
        LIMIT 50
    """
    
    print("\nEjecutando consulta OPTIMIZADA...")
    inicio_query = time.time()
    cursor.execute(query_optimizada)
    resultados_opt = cursor.fetchall()
    tiempo_query = time.time() - inicio_query
    print(f"  {len(resultados_opt)} resultados obtenidos")
    print(f"  Tiempo consulta: {tiempo_query:.4f} segundos")
    
    # Limpiar indices
    print("\nLimpiando indices temporales...")
    try:
        cursor.execute("DROP INDEX idx_salaries_current ON salaries")
        cursor.execute("DROP INDEX idx_titles_emp_no_dates ON titles")
        cursor.execute("DROP INDEX idx_employees_emp_no ON employees")
        connection.commit()
        print("  Indices eliminados")
    except Exception as e:
        print(f"  Error eliminando indices: {e}")
    
    tiempo_opt = time.time() - inicio_opt
    
    cursor.close()
    connection.close()
    
    print(f"Tiempo sin optimizar: {tiempo_no_opt:.6f} segundos")
    print(f"Tiempo optimizado (con indices): {tiempo_opt:.6f} segundos")
    mejora = ((tiempo_no_opt - tiempo_opt) / tiempo_no_opt) * 100
    print(f"Mejora: {mejora:.2f}%")
    
    return {
        'sin_optimizar': tiempo_no_opt,
        'optimizado': tiempo_opt
    }

def opcional_grafica():
    """
    Genera una grafica comparativa de todas las consultas de la practica
    incluyendo una consulta adicional.
    Requiere: matplotlib
    """
    try:
        print("PARTE OPCIONAL - GRAFICA COMPARATIVA")
        
        # Ejecutar todas las funciones de benchmarking para obtener los tiempos
        print("\nEjecutando todos los benchmarks para la grafica...")
        
        resultados = {
            'Salarios': benchmark_salarios(),
            'Departamentos': benchmark_departamentos(),
            'Fecha Contratacion': benchmarking_fecha_contratacion(),
            'Titulos': benchmarking_titulos_usuarios_indice(),
            'Media Salarios': benchmark_salarios_superiores_media(),
            'SUBSTR vs LIKE': substr_vs_like(),
            'Adicional': consulta_adicional()
        }
        
        # Preparar datos para la grafica
        consultas = list(resultados.keys())
        tiempos_no_opt = [resultados[c]['sin_optimizar'] for c in consultas]
        tiempos_opt = [resultados[c]['optimizado'] for c in consultas]
        
        # Crear grafica
        x = np.arange(len(consultas))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # Barras
        barras_no_opt = ax.bar(x - width/2, tiempos_no_opt, width, 
                                label='Sin Optimizar', color='red', alpha=0.7)
        barras_opt = ax.bar(x + width/2, tiempos_opt, width, 
                            label='Optimizado', color='green', alpha=0.7)
        
        # Personalizacion
        ax.set_xlabel('Consultas', fontsize=12)
        ax.set_ylabel('Tiempo (segundos)', fontsize=12)
        ax.set_title('Comparativa de Rendimiento: Consultas Optimizadas vs No Optimizadas', 
                    fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(consultas, rotation=45, ha='right', fontsize=10)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Anadir valores en las barras
        for barras in [barras_no_opt, barras_opt]:
            for barra in barras:
                altura = barra.get_height()
                if altura > 0:
                    ax.annotate(f'{altura:.2f}s',
                               xy=(barra.get_x() + barra.get_width()/2, altura),
                               xytext=(0, 3),
                               textcoords="offset points",
                               ha='center', va='bottom', fontsize=8)
        
        # Calcular y mostrar mejora promedio
        mejora_promedio = np.mean([(no_opt - opt) / no_opt * 100 
                                   for no_opt, opt in zip(tiempos_no_opt, tiempos_opt)])
        ax.text(0.02, 0.98, f'Mejora promedio: {mejora_promedio:.1f}%', 
                transform=ax.transAxes, fontsize=11, 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        # Guardar grafica
        plt.savefig('benchmark_comparativa.png', dpi=300, bbox_inches='tight')
        print(f"\nGrafica guardada como 'benchmark_comparativa.png'")
        
        # Mostrar grafica (si es posible)
        plt.show()
        
        print("TABLA RESUMEN DE TIEMPOS")
        print(f"{'Consulta':<25} {'Sin Optimizar':>15} {'Optimizado':>15} {'Mejora':>12}")
        
        for i, consulta in enumerate(consultas):
            no_opt = tiempos_no_opt[i]
            opt = tiempos_opt[i]
            mejora = ((no_opt - opt) / no_opt) * 100
            print(f"{consulta:<25} {no_opt:>15.6f} {opt:>15.6f} {mejora:>11.2f}%")
        
    except ImportError:
        print("\nError: matplotlib no esta instalado.")
        print("Instalalo con: pip install matplotlib")
    except Exception as e:
        print(f"\nError generando grafica: {e}")

opcional_grafica()