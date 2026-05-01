# 💻 Fundamentos de los Sistemas Operativos

Bienvenido a mi repositorio, un espacio donde documento mi recorrido por la asignatura de **Fundamentos de los Sistemas Operativos (FUSO)** del **Grado en Ingeniería Matemática (iMAT)** en **ICAI**.
Aquí reúno **todas las prácticas, materiales, scripts, ejercicios y entregables** que he desarrollado a lo largo del curso.

Este repositorio refleja tanto mi **progreso técnico** en el entendimiento de los sistemas operativos como mi **crecimiento personal y metodológico** al aprender a interactuar con el núcleo de los sistemas computacionales.

---

## 🎯 Sobre la Asignatura

La asignatura de **Fundamentos de los Sistemas Operativos** tiene como objetivo principal enseñar los conceptos fundamentales y la arquitectura interna de los **sistemas operativos modernos**.
En el marco del grado iMAT, combina los fundamentos matemáticos con la ingeniería de software y la arquitectura de computadores, fomentando una comprensión profunda de cómo interactúan el hardware y el software.

Durante el curso se trabajan aspectos como:

* 🐧 **Comandos Unix/Linux** y programación en shell
* 📜 **Scripting en Bash** para automatización y procesamiento de datos
* 📦 **Gestión de dependencias** y entornos virtuales en Python
* ⚙️ **Procesos e hilos**: creación, comunicación y sincronización
* 📊 **Benchmarking y rendimiento**: evaluación de algoritmos paralelos
* 🔒 **Exclusión mutua y semáforos**: sincronización entre procesos
* 💾 **Gestión de memoria**: análisis de consumo y optimización
* 🚀 **Despliegue de aplicaciones** en entornos Linux (Flask + Alpine)

Cada práctica busca desarrollar una habilidad concreta —desde dominar la línea de comandos hasta implementar algoritmos de sincronización y gestión de memoria con Python.

---

## 📚 Prácticas Incluidas

### 🐧 [P1 — Comandos Linux](./P1/)
*Introducción a la línea de comandos Unix/Linux*
- 📂 Navegación y gestión del sistema de archivos
- 🔍 Búsqueda, filtrado y manipulación de texto con comandos estándar
- 🐍 Script Python opcional para conteo y análisis de ficheros de texto
- 📄 Guía de estilo de programación de referencia

### 📜 [P2 — Scripting en Bash](./P2/)
*Automatización y procesamiento de datos con Bash*
- 🧹 Scripts para limpieza y transformación de datasets (Iris, Wine, MovieLens)
- 💬 Procesamiento de texto: extracción y filtrado de citas (Obama quotes)
- 🤖 Código Python de apoyo para las operaciones equivalentes en cada apartado
- 📊 Salidas de ejecución incluidas para comparación de resultados

### 📦 [P3 — Gestión de Dependencias](./P3/)
*Entornos virtuales y gestión de paquetes Python*
- 🔧 Scripts Bash para crear y gestionar entornos con `venv`
- 📋 Ficheros `requirements.txt` con dependencias exactas para reproducibilidad
- 🤖 Código Python para entrenamiento de modelos de ML (scikit-learn)
- 🎨 Scripts de visualización: cuantización de color y reconocimiento facial
- 📄 Memoria en PDF con el proceso y las decisiones tomadas

### ⚙️ [P4 — Procesos e Hilos](./P4/)
*Creación y gestión de procesos e hilos en Python*
- 🔀 Ejercicios con `multiprocessing` y `threading`
- 📡 Comunicación entre procesos: pipes, colas y señales
- 📸 Captura de ejecución de comandos del sistema
- 🧩 Ejercicios extra de concurrencia avanzada

### 📊 [P5 — Benchmarking y Rendimiento](./P5/)
*Evaluación del rendimiento de algoritmos paralelos*
- ➕ Suma de números: comparación secuencial vs paralela (versión eficiente incluida)
- 🧮 Multiplicación de matrices: versión básica e implementación con hilos
- ⚡ Versión eficiente de multiplicación matricial con análisis de speedup
- 🔢 Análisis de errores numéricos en operaciones de punto flotante
- 📁 Ejercicio extra de la asignatura incluido

### 🔒 [P6 — Semáforos y Exclusión Mutua](./P6%20-%20Semaforos/)
*Sincronización de procesos con semáforos*
- 🚦 Implementación de secciones críticas con semáforos (apartados 1 y 2)
- 🔄 Problema productor-consumidor y variantes
- 🍝 Problema de los filósofos cenando
- 🏆 Ejercicio opcional de concurrencia avanzada

### 💾 [P7 — Gestión de Memoria](./P7%20-%20Gestion%20memoria/)
*Análisis y optimización del uso de memoria*
- 🗺️ Procesamiento de datos geoespaciales (500 POIs de Nueva York, ciudades del mundo)
- 📐 Implementación del algoritmo Haversine para distancias geográficas
- 📈 Comparativa de consumo de memoria entre distintas implementaciones
- 🧪 Ejercicio extra con medición de rendimiento y memoria

### 🚀 [Proyecto Final — Despliegue de Aplicaciones](./Proyecto%20Final/)
*Despliegue completo de una aplicación Flask en Alpine Linux*
- 🐧 Scripts de instalación y configuración en Alpine Linux
- 🌐 Aplicación Flask con múltiples endpoints: entrenamiento ML, estadísticas, EDA, mapas
- 📊 Procesamiento de datasets Gowalla (7 ciudades: Nueva York, San Francisco, Londres, Glasgow, Manchester, Washington DC, El Paso)
- ⚡ Comparación de ejecución secuencial vs paralela (multiplicación de matrices)
- 🗺️ Generación automática de mapas HTML con visualización de POIs
- 📄 Memoria técnica completa y póster del proyecto

---

## 🏗️ Estructura del Repositorio

```
Fundamentos de los Sistemas Operativos/
│
├── P1/                            # Comandos Linux
│   ├── Obligatorio/               # Comandos básicos y ficheros de práctica
│   └── Opcional/                  # Script Python y shell para análisis de texto
│
├── P2/                            # Scripting en Bash
│   ├── quotes/                    # Dataset de citas (Obama)
│   └── ml-1m/                     # Dataset MovieLens 1M
│
├── P3/                            # Gestión de Dependencias
│   ├── material_alumnos/          # Código base proporcionado
│   └── Claudia_Maria_Lopez_Bombin_Gestion_Dependencias/  # Entrega
│
├── P4/                            # Procesos e Hilos
│
├── P5/                            # Benchmarking y Rendimiento
│   └── Apartado extra/            # Ejercicio extra
│
├── P6 - Semaforos/                # Exclusión Mutua y Semáforos
│
├── P7 - Gestion memoria/          # Gestión de Memoria
│   └── Material_alumnos/          # Código base proporcionado
│
├── Proyecto Final/                # Proyecto Integrador de Despliegue
│   └── DatasetsGowalla/           # Datasets de check-ins por ciudad
│
└── Guia estilo programacion.pdf   # Guía de estilo oficial de la asignatura
```

Cada práctica incluye:

* ✅ **Código fuente** de la solución (Python y/o Bash)
* 📁 **Datasets y materiales** utilizados en los ejercicios
* 📄 **PDFs** con el enunciado de la práctica
* 🎯 **Entregables** finales (ficheros `.zip` con la entrega oficial)
* 📊 **Salidas y resultados** de ejecución cuando procede

---

## 🛠️ Tecnologías y Herramientas

| Área | Tecnologías |
|------|-------------|
| **Scripting** | Bash, Shell Unix |
| **Programación** | Python 3 |
| **Concurrencia** | `multiprocessing`, `threading` |
| **ML / Datos** | scikit-learn, pandas, NumPy |
| **Visualización** | Matplotlib, Seaborn, Folium |
| **Web** | Flask |
| **Sistema** | Alpine Linux, entornos virtuales (`venv`) |

---

## 🚀 Propósito del Repositorio

Más que un simple archivo de entregas, este repositorio funciona como un **diario de aprendizaje**.
Cada carpeta refleja la evolución de mis habilidades: desde los comandos básicos de shell hasta el despliegue de una aplicación completa con procesamiento paralelo de datos.

Aquí se documentan:

* 🧩 **Ejercicios iniciales** para asimilar los fundamentos de Unix/Linux
* ⚙️ **Prácticas aplicadas** con datasets y problemas reales
* 📚 **Material de referencia** empleado durante el curso
* 🧠 **Reflexiones** sobre las decisiones técnicas y su impacto en el rendimiento
* 💬 **Entregables finales** con código documentado y memorias en PDF

---

## 🧠 Aprendizajes Clave

Durante el curso he aprendido que **los sistemas operativos no son solo interfaces gráficas**, sino **sistemas complejos que gestionan recursos limitados** de forma eficiente y justa.

Algunos aprendizajes esenciales que me llevo son:

* El poder del **scripting en Bash** para automatizar tareas repetitivas
* La importancia de la **gestión de dependencias** para la reproducibilidad
* El valor de la **concurrencia y el paralelismo** para mejorar el rendimiento
* La necesidad de **semáforos y exclusión mutua** para evitar condiciones de carrera
* La conexión directa entre **uso de memoria** y eficiencia algorítmica
* Y, sobre todo, que cada problema de sincronización es una oportunidad para entender mejor cómo cooperan los procesos

---

## ⚙️ Requisitos y Uso

Para ejecutar los scripts y programas de este repositorio:

1. Clona el repositorio:

   ```bash
   git clone https://github.com/claudialbzz/FUSO.git
   cd FUSO
   ```

2. Instala las dependencias de Python (ejemplo para P3):

   ```bash
   pip install -r "P3/Claudia_Maria_Lopez_Bombin_Gestion_Dependencias/requirements4_1.txt"
   ```

3. Ejecuta un script Bash (ejemplo para P2):

   ```bash
   chmod +x "P2/Claudia_Maria_Lopez_Bombin_ap1.sh"
   ./"P2/Claudia_Maria_Lopez_Bombin_ap1.sh"
   ```

4. Ejecuta un script Python (ejemplo para P4):

   ```bash
   python "P4/Ejercicio1_Claudia.py"
   ```

---

## 🔗 Más Sobre Mí

Además de este proyecto académico, también desarrollo otros trabajos relacionados con **ingeniería matemática, sistemas distribuidos, programación de sistemas y arquitectura de software**.
Puedes encontrar más sobre mis proyectos personales y académicos en mi **portfolio**.

---

## 📬 Contacto

¿Te interesa comentar alguna práctica, compartir ideas o colaborar en proyectos de sistemas operativos o programación de bajo nivel?

📧 **Contacto**: [claudialbombin@alu.icai.comillas.edu](mailto:claudialbombin@alu.icai.comillas.edu)  
🔗 **LinkedIn**: [www.linkedin.com/in/claudia-lopez-bombin](https://www.linkedin.com/in/claudia-lopez-bombin)  
🐙 **GitHub**: [github.com/claudialbzz](https://github.com/claudialbzz)

---

🧭 **Keep coding. Keep learning. Keep exploring.**

> "Los sistemas operativos son como el aire acondicionado: solo los notas cuando no funcionan."
> — *Linus Torvalds*
