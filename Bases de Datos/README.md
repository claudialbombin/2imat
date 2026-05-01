# 🗄️ Bases de Datos — Recopilación de Prácticas y Proyectos

Bienvenida a la carpeta de **Bases de Datos**, asignatura del **Grado en Ingeniería Matemática (iMAT)** en **ICAI**. Aquí se recogen todas las prácticas, retos y el proyecto final, cubriendo desde SQL básico hasta arquitecturas híbridas con tres motores de bases de datos distintos.

---

## 🎯 Sobre la Asignatura

**Bases de Datos** proporciona los fundamentos teóricos y prácticos del diseño, implementación y optimización de sistemas de gestión de datos. A lo largo del curso se trabaja con bases de datos relacionales (MySQL), documentales (MongoDB) y de grafos (Neo4J), aprendiendo cuándo y cómo aprovechar cada paradigma.

---

## 📁 Contenido del Directorio

### 🟡 [P1 - SQL Básico](./P1%20-%20SQL%20Basico/)
*Introducción al diseño relacional y consultas SQL fundamentales*
- 🗺️ Diseño de diagrama entidad-relación
- 📝 Creación de tablas, inserciones y consultas SELECT básicas
- 🐍 Script Python para interacción con la base de datos
- 📄 Enunciado de la práctica (PDF)

### 🟠 [P2 - SQL Avanzado](./P2%20-%20SQL%20Avanzado/)
*Consultas complejas y optimización en SQL*
- 🔗 JOINs, subconsultas y vistas
- ⚡ Funciones de agregación y cláusulas avanzadas (GROUP BY, HAVING, WITH)
- 🐍 Script Python con consultas avanzadas
- 📄 Enunciado de la práctica (PDF)

### 🟢 [P3 - SQL + Python](./P3%20-%20SQL%20%2B%20Python/)
*Integración de SQL con Python aplicada a datos reales de Last.fm*
- 🎵 Dataset de Last.fm obtenido mediante Web Scraping
- 🗺️ Diagrama relacional del modelo de datos
- 🔄 Script de web scraping y script de carga en MySQL
- 🔍 Consultas SQL sobre datos reales de música

### 🔵 [P4 - SQL + Python + Benchmarking](./P4%20-%20SQL%20%2B%20Python%20%2B%20Benchmarking/)
*Análisis comparativo de rendimiento en bases de datos relacionales*
- ⏱️ Benchmarking de consultas SQL con diferentes volúmenes de datos
- 📊 Gráfica comparativa de tiempos de ejecución
- 🐍 Script Python para automatizar las pruebas de rendimiento

### 🟣 [P5 - MongoDB Básico](./P5%20-%20MongoDB%20Basico/)
*Introducción a las bases de datos documentales con MongoDB*
- 📦 Operaciones CRUD en MongoDB
- 🔍 Consultas con filtros, proyecciones y agregaciones
- 🐍 Script Python con PyMongo
- 📄 Enunciado de la práctica (PDF)

### 🔴 [P6 - MongoDB + Python + Benchmarking](./P6%20-%20MongoDB%20%2B%20Python%20%2B%20Benchmarking/)
*Comparativa de rendimiento entre MongoDB y MySQL*
- ⚖️ Benchmarking MySQL vs MongoDB sobre las mismas operaciones
- 📥 Script de carga de datos en ambos motores
- 📊 Análisis de rendimiento comparativo

### ⚫ [P7 - Neo4J](./P7%20-%20Neo4J%20/)
*Bases de datos de grafos con Neo4J y Cypher*
- 🕸️ Modelado de datos como grafos (nodos y relaciones)
- 🔍 Consultas Cypher básicas y traversal de grafos
- 📧 Script de carga de dataset de emails
- 🐍 Script Python con el driver oficial de Neo4J

### 🏆 [Proyecto Final](./Proyecto%20Final/)
*Sistema híbrido de análisis de reseñas de productos Amazon (474.000 reseñas)*
- 🗄️ Arquitectura multi-motor: **MySQL** (relacional) + **MongoDB** (documental) + **Neo4J** (grafos)
- 📊 Dashboard interactivo con 7 visualizaciones distintas
- 🎯 Sistema de recomendaciones basado en filtrado colaborativo (similitud de Pearson)
- 🕸️ Grafos de similitud entre usuarios y relaciones artículo-usuario
- 📈 Análisis sobre 4 categorías: Toys & Games, Video Games, Digital Music, Musical Instruments

### 🕵️ [Reto Colaborativo - Asesinato SQL](./Reto%20Colaborativo%20-%20Asesinato%20SQL/)
*SQL Murder Mystery — resolución de un asesinato usando solo SQL*
- 🔍 Investigación forense mediante consultas SQL
- 🧩 Reto colaborativo de lógica y SQL aplicado

---

## 🏗️ Estructura del Directorio

```
Bases de Datos/
├── P1 - SQL Basico/                         # Diseño relacional y SQL básico
├── P2 - SQL Avanzado/                       # Consultas complejas y optimización
├── P3 - SQL + Python/                       # SQL + Python + datos Last.fm
├── P4 - SQL + Python + Benchmarking/        # Benchmarking SQL
├── P5 - MongoDB Basico/                     # Introducción a MongoDB
├── P6 - MongoDB + Python + Benchmarking/    # Comparativa MySQL vs MongoDB
├── P7 - Neo4J/                              # Grafos con Neo4J y Cypher
├── Proyecto Final/                          # Sistema híbrido Amazon Reviews
├── Reto Colaborativo - Asesinato SQL/       # SQL Murder Mystery
└── README.md                                # Este fichero
```

---

## 🛠️ Tecnologías y Herramientas

| Área | Tecnologías |
|------|-------------|
| **Bases de datos relacionales** | MySQL 8, SQL |
| **Bases de datos documentales** | MongoDB 7, PyMongo |
| **Bases de datos de grafos** | Neo4J 5, Cypher |
| **Programación** | Python 3, Jupyter Notebooks |
| **Librerías Python** | mysql-connector-python, pymongo, neo4j, pandas, matplotlib |
| **Otras herramientas** | Web Scraping, benchmarking, diagrams E-R |

---

## 🌟 Proyecto Destacado

El **[Proyecto Final](./Proyecto%20Final/)** integra los tres paradigmas de bases de datos estudiados durante el curso para construir un sistema completo de análisis y recomendación sobre **474.344 reseñas de productos Amazon**:

- **MySQL** almacena los metadatos estructurados (usuarios, artículos, notas, fechas)
- **MongoDB** guarda el texto libre de las reseñas y los resúmenes
- **Neo4J** modela las relaciones entre usuarios y artículos como un grafo de similitud

---

> "Sin datos, solo eres otra persona con una opinión."
> — *W. Edwards Deming*

🧭 **Keep learning. Keep building. Keep exploring.**
