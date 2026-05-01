# 📦 Proyecto Final — Bases de Datos

**Asignatura:** Bases de Datos — 2.º Curso  
**Grado:** Ingeniería Matemática e Inteligencia Artificial (IMAT)  
**Alumna:** Claudia Maria Lopez Bombin

---

## 📋 Descripción

Sistema de gestión y análisis de más de **474.000 reseñas de productos Amazon** distribuidas en cuatro categorías, implementado con una arquitectura de bases de datos híbrida:

| Base de datos | Rol | Datos almacenados |
|---|---|---|
| **MySQL 8** | Datos relacionales y estructurados | Usuarios, artículos, categorías, notas, fechas, votos |
| **MongoDB 7** | Texto libre | `reviewText`, `summary` |
| **Neo4J 5** | Grafos de similitud | Similitudes Pearson entre usuarios, relaciones usuario–artículo |

### Datasets

| Dataset | Fichero | Reviews |
|---|---|---|
| Toys and Games | `Toys_and_Games_5.json` | 167.597 |
| Video Games | `Video_Games_5.json` | 231.780 |
| Digital Music | `Digital_Music_5.json` | 64.706 |
| Musical Instruments | `Musical_Instruments_5.json` | 10.261 |
| **Total** | | **474.344** |

---

## 🗂️ Estructura del proyecto

```
proyecto_bbdd/
│
├── configuracion.py          # ⚙️  Credenciales, rutas y parámetros (EDITAR ESTO)
├── load_data.py              # 📥  Crea el schema MySQL/MongoDB y carga los datos
├── menu_visualizacion.py     # 📊  Menú interactivo de visualización (7 gráficas)
├── neo4JProyecto.py          # 🕸️  Menú Neo4J (similitudes, artículos, grafos)
├── inserta_dataset.py        # ➕  CLI para insertar datasets adicionales
├── recomendaciones.py        # 🎯  Top 10 artículos no consumidos por un usuario
├── requirements.txt          # 📦  Dependencias Python
│
├── outputs/
│   └── graficas/             # 🖼️  Gráficas generadas automáticamente aquí
│
└── README.md                 # 📖  Este fichero
```

---

## ⚙️ Requisitos previos

### Software necesario
- **Python** 3.10 o superior
- **MySQL** 8.x en ejecución (puerto 3306)
- **MongoDB** 7.x en ejecución (puerto 27017)
- **Neo4J** 5.x en ejecución (puerto 7687, interfaz en http://localhost:7474)

### Instalación de dependencias Python

```bash
pip install -r requirements.txt
```

---

## 🚀 Ejecución paso a paso

### Paso 1 — Configurar credenciales y rutas

Edita **únicamente** el fichero `configuracion.py`:

```python
# Rutas a los ficheros de datos (ajustar según tu sistema)
RUTA_TOYS        = "datos/Toys_and_Games_5.json"
RUTA_VIDEOGAMES  = "datos/Video_Games_5.json"
RUTA_MUSIC       = "datos/Digital_Music_5.json"
RUTA_INSTRUMENTS = "datos/Musical_Instruments_5.json"

# Credenciales MySQL
MYSQL_HOST     = "localhost"
MYSQL_PORT     = 3306
MYSQL_USER     = "root"
MYSQL_PASSWORD = "tu_password"
MYSQL_DATABASE = "amazon_reviews"

# Credenciales MongoDB
MONGO_URI      = "mongodb://localhost:27017/"
MONGO_DATABASE = "amazon_reviews_mongo"

# Credenciales Neo4J
NEO4J_URI      = "bolt://localhost:7687"
NEO4J_USER     = "neo4j"
NEO4J_PASSWORD = "tu_password_neo4j"
```

> ⚠️ **Importante:** No es necesario editar ningún otro fichero. Solo `configuracion.py`.

---

### Paso 2 — Cargar los datos (Primera vez)

```bash
python load_data.py
```

Este script:
1. Crea la base de datos `amazon_reviews` en MySQL con sus 4 tablas
2. Crea la base de datos `amazon_reviews_mongo` en MongoDB con índices
3. Lee los 4 ficheros JSON **línea a línea** (sin cargarlos enteros en memoria)
4. Inserta los datos en MySQL (metadatos) y MongoDB (texto libre) en batches de 500

> ⏱️ Tiempo estimado: 3–10 minutos dependiendo del hardware.

---

### Paso 3 — Menú de visualización

```bash
python menu_visualizacion.py
```

Menú interactivo con las siguientes opciones:

```
1. Evolución de reviews por años         → histograma por categoría o todas
2. Popularidad de artículos              → curva ordenada en escala log
3. Histograma por nota (overall)         → por categoría o artículo individual (ASIN)
4. Evolución acumulada por categoría     → curva acumulada con timestamp unix
5. Histograma de reviews por usuario     → distribución logarítmica
6. Nube de palabras                      → campo 'summary' de MongoDB por categoría
7. Ratio de utilidad helpful [EXTRA]     → helpful_votes/helpful_total por categoría
0. Salir
```

> 🖼️ **Todas las gráficas se guardan automáticamente** en `outputs/graficas/` con nombre descriptivo y timestamp.

---

### Paso 4 — Grafos en Neo4J

```bash
python neo4JProyecto.py
```

Menú con 4 opciones:

```
1. [4.1] Similitudes Pearson entre los 30 usuarios con más reviews
         → Carga en Neo4J nodos :Usuario y relaciones :SIMILAR con similitud
         → Muestra el usuario con más vecinos

2. [4.2] Artículos aleatorios y usuarios que los valoraron
         → Pide categoría y número de artículos
         → Carga :Articulo, :Usuario y relaciones :VALORO (nota + timestamp)

3. [4.3] Usuarios multi-categoría
         → 400 primeros usuarios por nombre que valoraron ≥2 tipos
         → Carga :Usuario, :Categoria y relaciones :CONSUME (num_articulos)

4. [4.4] Artículos populares con <40 reviews
         → 5 más populares con menos de 40 reviews
         → Carga relaciones :EN_COMUN entre usuarios (artículos compartidos)
```

Para visualizar los grafos, abre el **Neo4J Browser** en http://localhost:7474 y ejecuta:
```cypher
MATCH (n) RETURN n LIMIT 100
```

> ⚠️ Cada opción **limpia la base de datos Neo4J** antes de cargar sus datos.

---

### Paso 5 — Insertar un dataset adicional

```bash
python inserta_dataset.py --ruta datos/Sports_and_Outdoors_5.json --categoria "Sports and Outdoors"
```

Argumentos:
- `--ruta` : ruta al fichero JSON del nuevo dataset
- `--categoria` : nombre de la categoría nueva

El script detecta automáticamente usuarios ya existentes y no los duplica.

---

### Paso 6 — Recomendaciones

```bash
python recomendaciones.py
```

Pide por terminal:
1. El `reviewerID` del usuario
2. La categoría de interés

Devuelve los **10 artículos más populares** de esa categoría que el usuario **aún no ha valorado**.

Ejemplo de uso:
```
Introduce el reviewerID del usuario: A3V6Z4RCDGRC44
Categorías: 1. Toys and Games  2. Video Games  3. Digital Music  4. Musical Instruments
Selecciona categoría: 2

Top 10 recomendaciones para 'A3V6Z4RCDGRC44' en 'Video Games':
Pos  ASIN             Reviews
  1. B00002SVKU            892
  2. B000AMGGGU            756
  ...
```

---

## 📊 Gráficas generadas

Las gráficas se guardan en `outputs/graficas/` con el siguiente esquema de nombres:

| Prefijo | Gráfica |
|---|---|
| `01_reviews_por_anio_*` | Evolución anual de reviews |
| `02_popularidad_*` | Curva de popularidad de artículos |
| `03_histograma_nota_*` | Distribución de notas |
| `04_evolucion_temporal_*` | Evolución acumulada en el tiempo |
| `05_reviews_por_usuario_*` | Distribución de reviews por usuario |
| `06_nube_palabras_*` | Nube de palabras del campo summary |
| `07_ratio_utilidad_*` | Ratio de utilidad helpful por categoría |

---

## 🗄️ Schema MySQL

```sql
Usuarios     (reviewerID PK, reviewerName)
Categorias   (id_categoria PK, nombre UNIQUE)
Articulos    (asin PK, id_categoria FK)
Reviews      (id_review PK AUTO_INCREMENT,
              reviewerID FK, asin FK,
              overall FLOAT,
              helpful_votes INT, helpful_total INT,
              unix_review_time BIGINT,
              review_date DATE)
```

---

## 🗃️ Schema MongoDB

```json
{
  "_id": "ObjectId autogenerado",
  "reviewerID": "referencia cruzada con MySQL",
  "asin": "referencia cruzada con MySQL",
  "reviewText": "texto completo de la review",
  "summary": "resumen de la review"
}
```

---

## 🕸️ Grafos Neo4J

| Nodo | Propiedades |
|---|---|
| `:Usuario` | `reviewerID` |
| `:Articulo` | `asin` |
| `:Categoria` | `nombre` |

| Relación | Propiedades |
|---|---|
| `(:Usuario)-[:SIMILAR]-(:Usuario)` | `similitud` (Pearson) |
| `(:Usuario)-[:VALORO]->(:Articulo)` | `nota`, `timestamp` |
| `(:Usuario)-[:CONSUME]->(:Categoria)` | `num_articulos` |
| `(:Usuario)-[:EN_COMUN]-(:Usuario)` | `articulos_comunes` |

---

## 🤖 Modelo de Machine Learning (descripción)

Para recomendaciones más sofisticadas se propone **Filtrado Colaborativo basado en usuarios (User-Based CF)**:

1. Representar cada usuario como un vector de valoraciones `(asin → overall)`
2. Calcular la similitud de Pearson entre usuarios (ya implementada en el apartado 4.1)
3. Identificar los *k* vecinos más cercanos al usuario objetivo
4. Predecir la valoración de artículos no consumidos como media ponderada de los vecinos
5. Recomendar los artículos con mayor valoración predicha

Alternativa escalable: **Matrix Factorization con SVD** (librería `surprise`) o **ALS implícito** (librería `implicit`).

---

## 📦 Dependencias (`requirements.txt`)

```
mysql-connector-python>=8.0.33
pymongo>=4.6.0
neo4j>=5.14.0
matplotlib>=3.8.0
wordcloud>=1.9.3
numpy>=1.26.0
```

---

## 📁 Ficheros de datos (NO incluidos en el ZIP)

Los ficheros de datos originales no se entregan. Deben descargarse del enlace proporcionado en el enunciado y colocarse en la carpeta indicada en `configuracion.py`.

---

*Claudia Maria Lopez Bombin — Proyecto Final Bases de Datos — IMAT 2.º Curso*
