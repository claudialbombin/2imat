# 📊 Adquisición de Datos

Bienvenido a mi repositorio , un espacio donde documento mi recorrido por la asignatura de **Adquisición de Datos** del **Grado en Ingeniería Matemática (iMAT)** en **ICAI**.
Aquí reúno **todas las prácticas, materiales, datasets, cuadernos de trabajo y entregables** que he desarrollado a lo largo del curso.

Este repositorio refleja tanto mi **progreso técnico** en la obtención y procesamiento de datos como mi **crecimiento personal y metodológico** al aprender a trabajar con datos desde su fuente original hasta su preparación para análisis.

---

## 🎯 Sobre la Asignatura

La asignatura de **Adquisición de Datos** tiene como objetivo principal enseñar las técnicas y metodologías para **obtener, limpiar y preparar datos** desde múltiples fuentes para su posterior análisis.
En el marco del grado iMAT, combina los fundamentos matemáticos y estadísticos con la programación y el procesamiento de datos, fomentando una mirada crítica hacia la calidad y procedencia de la información.

Durante el curso se trabajan aspectos como:

* 🐼 **Manejo avanzado de pandas** para manipulación de DataFrames
* 🤖 **Implementación de autómatas** (AFD) para búsqueda y procesamiento de texto
* 🎵 **Procesamiento de datos complejos** como datasets de Spotify y Airbnb
* 📊 **Limpieza y transformación de datos** reales
* 🔍 **Técnicas de exploración inicial** de datasets
* 🌐 **Desarrollo web con Flask** para presentación de datos (CV interactivo)
* 🕷️ **Web scraping con Scrapy** para adquisición automatizada de datos desde la web

Cada práctica busca desarrollar una habilidad concreta —desde dominar la sintaxis de pandas hasta construir pipelines completos de procesamiento de datos.

---

## 💻 Estructura del Repositorio

```
Adquisicion de datos/
├── Guiadas/                      # Ejercicios guiados por temática
│   ├── Color/                    #   → Autómata para detectar colores en cadenas de texto
│   ├── Pandas/                   #   → Introducción a pandas: notebooks con ejercicios y soluciones
│   └── Spotify/                  #   → Análisis exploratorio de datos de Spotify (dataset real)
│
├── P1 - Automatas/               # Práctica 1: Autómatas Finitos Deterministas (AFD) en Python
│   ├── automata_main.py          #   → AFD que detecta si una cadena contiene el patrón "ajo"
│   └── search_main.py            #   → AFD genérico: busca cualquier patrón introducido por el usuario y cuenta ocurrencias
│
├── P2 - Intro_Pandas/            # Práctica 2: Análisis de datos con pandas
│   ├── airbnb_main.py            #   → Limpieza, transformación y análisis del dataset de Airbnb
│   ├── airbnb.csv                #   → Dataset de listados de Airbnb
│   ├── population.csv            #   → Dataset de población por barrio
│   └── Práctica 2 - Introducción a pandas.pdf  # Enunciado de la práctica
│
├── P3 - CV html/                 # Práctica 3: Curriculum Vitae web con Flask
│   ├── app.py                    #   → Aplicación Flask con rutas: página principal, CV y formulario de contacto
│   ├── static/                   #   → Recursos estáticos (CSS, imágenes)
│   └── templates/                #   → Plantillas HTML (index, cv, contact)
│
└── Proyecto Final/               # Proyecto Final: scraping y análisis de datos de Fórmula 1
    ├── f1spiders.py              #   → Spider con Scrapy que extrae resultados de carrera de Wikipedia (2012–2024)
    ├── funciones_api.py          #   → Funciones auxiliares para consumo de API
    ├── merge_data.py             #   → Script de fusión de datasets
    ├── merge_limpio.py           #   → Versión limpia del merge
    └── data/                     #   → CSVs generados por el spider (un archivo por carrera y año)
```

Cada práctica incluye:

* Código fuente (scripts o notebooks en Python)
* Datasets utilizados o su referencia
* Documentación explicativa del proceso y decisiones técnicas

---

## 🚀 Propósito del Repositorio

Más que un simple archivo de entregas, este repositorio funciona como un **diario de aprendizaje**.
Cada carpeta refleja la evolución de mis habilidades: desde los primeros scripts básicos hasta pipelines complejos de procesamiento de datos.

Aquí se documentan:

* 🧩 **Ejercicios iniciales** para asimilar los fundamentos
* ⚙️ **Prácticas aplicadas** con datos reales
* 📚 **Material de referencia** empleado durante el curso
* 🧠 **Reflexiones personales** sobre las decisiones técnicas y su impacto en la calidad de los datos
* 💬 **Entregables finales**, con código cuidadosamente documentado

> "Los datos son como la materia prima: su valor depende de cómo los extraigas y refines."
> — *Adaptado para Adquisición de Datos*

---

## 🧠 Aprendizajes Clave

Durante el curso aprendemos que **adquirir datos no consiste solo en descargarlos**, sino en **pensar en su procedencia y calidad**: entender de dónde vienen, cómo se generaron y qué transformaciones necesitan para ser útiles.

Algunos aprendizajes esenciales que nos llevamos son:

* La importancia de la **calidad y procedencia** de los datos
* La **relación entre estructura y utilidad** de los datasets
* El valor de la **automatización** en los procesos de adquisición
* La necesidad de **validar y verificar** los datos en cada paso del proceso
* Y, sobre todo, que cada dataset imperfecto es una oportunidad para aprender a limpiar y transformar datos de manera efectiva

---

## ⚙️ Requisitos y Uso

Para ejecutar los notebooks o scripts de este repositorio:

1. Clona el repositorio:

   ```bash
   git clone https://github.com/tuusuario/adquisicion-datos-imat.git
   cd adquisicion-datos-imat
   ```

2. Instala las dependencias:

   ```bash
   pip install pandas numpy jupyter flask scrapy
   ```

3. Abre cualquier práctica en Jupyter Notebook o ejecuta los scripts directamente:

   ```bash
   # Ejemplo: Práctica 1 – Autómatas
   python "P1 - Automatas/automata_main.py"

   # Ejemplo: Proyecto Final – Spider de F1
   python "Proyecto Final/f1spiders.py"

   # Ejemplo: Práctica 3 – CV web con Flask
   python "P3 - CV html/app.py"
   ```

---

## 🔗 Más Sobre Mí

Además de este proyecto académico, también desarrollo otros trabajos relacionados con **ingeniería matemática, análisis de datos, programación y procesamiento de información**.
Puedes encontrar más sobre mis proyectos personales y académicos en mi **portfolio**.

---

## 📬 Contacto

¿Te interesa comentar alguna práctica, compartir ideas o colaborar en un proyecto de adquisición y procesamiento de datos?
📩 Puedes escribirme si te apasiona hablar de **datos, pipelines, automatización o ingeniería matemática**.

---

🧭 **Keep acquiring. Keep processing. Keep learning.**

> "Los datos no son la respuesta, son las preguntas."
> — *Carla Gentry*
