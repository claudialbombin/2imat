# 📘 Ecuaciones Diferenciales

Bienvenido a este directorio, donde documento mi recorrido por la asignatura de **Ecuaciones Diferenciales** del **Grado en Ingeniería Matemática (iMAT)** en **ICAI**.
Aquí reúno **todas las prácticas, implementaciones numéricas y el proyecto final** que he desarrollado a lo largo del curso.

Este espacio refleja tanto mi **progreso técnico** en el análisis y resolución de ecuaciones diferenciales como mi **crecimiento metodológico** al aprender a modelizar fenómenos continuos y aplicar herramientas matemáticas a problemas reales.

---

## 🎯 Sobre la Asignatura

La asignatura de **Ecuaciones Diferenciales** tiene como objetivo principal enseñar a **modelizar, analizar y resolver** sistemas que describen la evolución de magnitudes continuas en el tiempo o el espacio.
En el marco del grado iMAT, combina el rigor teórico de las matemáticas con la **aplicación práctica en ingeniería, física y computación científica**.

Durante el curso se trabajan aspectos como:

* 📈 **Ecuaciones diferenciales ordinarias (EDO)** de primer y segundo orden
* ⚙️ **Sistemas de ecuaciones diferenciales** y análisis de estabilidad
* 🔢 **Métodos numéricos**: Euler, Runge–Kutta (`ode45`) y aproximaciones multietapa
* 🌀 **Sistemas caóticos**: las Ecuaciones de Lorenz como caso de estudio
* 🧮 **Transformada de Laplace** y resolución de sistemas lineales

---

## 💻 Estructura del Repositorio

```
Ecuaciones Diferenciales/
│
├── P1/                               # Práctica 1
│   ├── P1.mlx                        # Script principal de la práctica (MATLAB Live Script)
│   ├── P1A.mat                       # Datos de la práctica
│   ├── ode45sisA.mlx                 # Resolución de sistema de EDOs con ode45
│   ├── ode45sisA.pdf                 # Versión PDF del script anterior
│   ├── h.m                           # Función auxiliar MATLAB
│   ├── vdp1.m                        # Modelo del oscilador de Van der Pol
│   ├── Ecuaciones_de_Lorenz.pdf      # Documento sobre el sistema de Lorenz
│   └── Prácticas__EDO_IMAT 25_26.pdf # Guión oficial de prácticas
│
├── Proyecto final/                   # Proyecto final de la asignatura
│   ├── ProyectoEDO.mlx               # Script principal del proyecto (MATLAB Live Script)
│   ├── caso5.mlx                     # Caso de estudio 5
│   └── vdp5.m                        # Variante del oscilador de Van der Pol
│
├── diagrama_fases.py                 # Script Python para generación de diagramas de fases
└── untitled2.mlx                     # Script MATLAB adicional de experimentación
```

Cada entregable incluye:

* ✅ **Código fuente** en MATLAB Live Scripts (`.mlx`) o Python
* 📁 **Datos** de simulación en formato `.mat`
* 📄 **Documentación** en PDF con análisis y resultados
* 🎯 **Entregables finales** presentados con rigor analítico

---

## 📂 Contenido Detallado

### 🔬 [P1 — Práctica 1](./P1/)
*Introducción a la resolución numérica de EDOs y sistemas dinámicos*
- 🌀 Estudio y simulación de las **Ecuaciones de Lorenz** (caos determinista)
- ⚙️ Resolución de **sistemas de EDOs** mediante `ode45` de MATLAB
- 📉 Modelización del **oscilador de Van der Pol** (`vdp1.m`)
- 📊 Análisis de trayectorias y atractores en el espacio de fases

### 🏁 [Proyecto Final](./Proyecto%20final/)
*Modelización avanzada y análisis de un sistema dinámico complejo*
- 🎯 Aplicación integradora de los contenidos del curso
- 🔄 Estudio del **caso 5** con análisis cualitativo y numérico
- 📈 Variante extendida del oscilador de Van der Pol (`vdp5.m`)
- 📝 Entregable final con código documentado en MATLAB Live Script

### 🐍 [diagrama_fases.py](./diagrama_fases.py)
*Visualización de diagramas de fases con Python*
- Generación de **campos vectoriales** y trayectorias en el plano de fases
- Uso de `matplotlib` y `scipy` para representar la dinámica de sistemas

---

## 🛠️ Tecnologías y Herramientas

| Área | Tecnologías |
|------|-------------|
| **Cálculo numérico** | MATLAB, `ode45`, Live Scripts (`.mlx`) |
| **Visualización** | Python, Matplotlib, diagramas de fases |
| **Modelización** | Sistema de Lorenz, oscilador de Van der Pol |
| **Documentación** | PDF, MATLAB Live Scripts exportados |

---

## ⚙️ Requisitos y Uso

### MATLAB
Abre cualquier `.mlx` directamente en MATLAB (R2021a o superior recomendado):

```matlab
% Ejemplo: ejecutar la práctica 1
open('P1/P1.mlx')

% Ejemplo: resolver el sistema con ode45
open('P1/ode45sisA.mlx')
```

### Python
Para el diagrama de fases, instala las dependencias y ejecuta:

```bash
pip install numpy matplotlib scipy
python diagrama_fases.py
```

---

## 🚀 Propósito de Este Directorio

Más que un simple archivo de entregas, este directorio funciona como un **diario de aprendizaje**.
Cada práctica refleja la evolución de mis habilidades: desde la resolución numérica de sistemas básicos hasta la simulación de comportamientos caóticos como el atractor de Lorenz.

Aquí se documentan:

* 🌀 **Sistemas caóticos** y su sensibilidad a las condiciones iniciales
* ⚙️ **Implementaciones numéricas** con `ode45` de MATLAB
* 🐍 **Visualizaciones en Python** de campos vectoriales y diagramas de fases
* 💬 **Entregables finales** con rigor analítico y código documentado

> "Las ecuaciones diferenciales no solo describen el cambio: lo explican."
> — *Ian Stewart*

---

## 🧠 Aprendizajes Clave

Durante el curso he aprendido que **las ecuaciones diferenciales son el lenguaje de la naturaleza**: una forma universal de expresar leyes físicas, procesos biológicos y dinámicas de sistemas complejos.

Algunos aprendizajes esenciales:

* La importancia del **análisis cualitativo** más allá de la solución exacta
* La conexión entre **modelo matemático y fenómeno real** (Van der Pol, Lorenz)
* El valor de los **métodos numéricos** para problemas sin solución cerrada
* Que pequeños cambios en las condiciones iniciales pueden generar comportamientos **radicalmente distintos** (caos)
* Y, sobre todo, que resolver ecuaciones diferenciales es aprender a **pensar en cambio y dinámica**

---

## 📬 Contacto

¿Te interesa comentar alguna demostración, compartir ideas sobre modelización matemática o colaborar en proyectos de ecuaciones diferenciales aplicadas?

📧 **Contacto**: [claudialbombin@alu.icai.comillas.edu](mailto:claudialbombin@alu.icai.comillas.edu)
🔗 **LinkedIn**: [www.linkedin.com/in/claudia-lopez-bombin](https://www.linkedin.com/in/claudia-lopez-bombin)
🐙 **GitHub**: [github.com/claudialbzz](https://github.com/claudialbzz)

---

🧭 **Keep modeling. Keep solving. Keep understanding.**

> "Resolver una ecuación diferencial es comprender cómo el cambio construye el mundo."
> — *Anónimo*
