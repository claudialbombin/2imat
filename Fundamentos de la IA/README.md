# 🧠 Fundamentos de la Inteligencia Artificial

Bienvenido a la carpeta de **Fundamentos de la Inteligencia Artificial (FIA)** del **Grado en Ingeniería Matemática (iMAT)** en **ICAI**.
Aquí reúno **todas las prácticas, algoritmos y entregables** que he desarrollado a lo largo del curso, desde agentes reflejos básicos hasta sistemas de inferencia bayesiana y proyectos integradores.

---

## 🎯 Sobre la Asignatura

La asignatura de **Fundamentos de la Inteligencia Artificial** tiene como objetivo enseñar los conceptos y técnicas esenciales de la **IA moderna**, combinando fundamentos matemáticos con programación algorítmica.

Durante el curso se trabajan aspectos como:

- 🤖 **Agentes inteligentes** y entornos de tarea
- 🔍 **Algoritmos de búsqueda** informada y no informada
- ♟️ **Búsqueda adversarial** (MinMax) para juegos
- 🧩 **Lógica proposicional** y resolución de puzzles
- 📊 **Inferencia bayesiana** y razonamiento probabilístico
- 🧠 **Procesos de decisión de Markov (MDP)** y aprendizaje por refuerzo

---

## 📚 Prácticas y Contenidos

### 🤖 P1 – Introducción a los Agentes Inteligentes
*Implementación de agentes reflejos simples en entornos de tarea*
- **E1 – Cruce del río** (`Rivercrossing Reflex.ipynb`): agente reflejo que resuelve el problema clásico del cruce del río
- **E2 – Aspiradora** (`FIA 25 26 Agentes Reflex.ipynb`): agente reflejo para el entorno de la aspiradora, con tests de validación

### 🔍 P2 – Algoritmos de Búsqueda
*Estrategias de búsqueda para resolución de problemas*
- Documentación y enunciado en `P2.pdf`
- Algoritmos de búsqueda no informada (BFS, DFS) e informada (A*)

### ♟️ P3 – MinMax
*Algoritmo de búsqueda adversarial para juegos de dos jugadores*
- `MinMax.py`: implementación del algoritmo MinMax con poda alfa-beta

### 🧩 P4 – Lógica
*Representación del conocimiento y razonamiento lógico*
- `einstein_puzzle_(FIA24).ipynb`: resolución del famoso puzzle de Einstein mediante lógica proposicional y satisfacibilidad (SAT)
- Enunciado en `Practice Logica.pdf`

### 📊 P5 – Inferencia Bayesiana
*Razonamiento probabilístico y redes bayesianas*
- `problema1.py`: modelado e inferencia en una red bayesiana (problema 1)
- `problema2.py`: modelado e inferencia en una red bayesiana (problema 2)
- Enunciado en `practica inferencia.pdf`

### 🏆 Proyecto Final
*Proyecto integrador que combina MDP, inferencia bayesiana y agentes autónomos*
- `river_mdp.py`: resolución de un MDP de cruce de río mediante value iteration
- `palacio_bayesiano.py`: agente que razona con incertidumbre en el Palacio Bayesiano
- `kurtz.py` + `funciones_kurtz.py`: agente para el escenario Kurtz
- `funciones_comunes.py`: utilidades compartidas entre los distintos agentes
- Memoria completa en `Proyecto final FIA.pdf`

---

## 🏗️ Estructura de la Carpeta

```
Fundamentos de la IA/
├── P1 - Introduccion/
│   ├── E1-rio/                        # Agente reflejo: cruce del río
│   │   ├── Rivercrossing Reflex.ipynb
│   │   └── Ejercicio 1.pdf
│   └── E2-aspiradora/                 # Agente reflejo: aspiradora
│       ├── FIA 25 26 Agentes Reflex.ipynb
│       ├── Ejercicio 2.pdf
│       └── Tests aspiradora/
├── P2 - Algoritmos_Busqueda/
│   └── P2.pdf                         # Enunciado y documentación
├── P3 - MinMax/
│   └── MinMax.py                      # Algoritmo MinMax con poda alfa-beta
├── P4 - Logica/
│   ├── einstein_puzzle_(FIA24).ipynb  # Puzzle de Einstein con lógica SAT
│   └── Practice Logica.pdf
├── P5 - Inferencia Bayesiana/
│   ├── problema1.py                   # Red bayesiana problema 1
│   ├── problema2.py                   # Red bayesiana problema 2
│   └── practica inferencia.pdf
└── Proyecto final/
    ├── river_mdp.py                   # MDP cruce del río
    ├── palacio_bayesiano.py           # Agente Palacio Bayesiano
    ├── kurtz.py                       # Agente Kurtz
    ├── funciones_kurtz.py
    ├── funciones_comunes.py
    └── Proyecto final FIA.pdf
```

---

## 🛠️ Tecnologías y Herramientas

| Área | Tecnologías |
|------|-------------|
| **Lenguaje** | Python 3 |
| **Notebooks** | Jupyter Notebook |
| **Lógica / SAT** | `python-sat`, lógica proposicional |
| **Probabilidad** | `pgmpy`, redes bayesianas |
| **MDP / RL** | Implementación desde cero con NumPy |
| **Visualización** | Matplotlib |

---

## ⚙️ Requisitos y Uso

1. Instala las dependencias:

   ```bash
   pip install numpy pandas matplotlib jupyter pgmpy python-sat
   ```

2. Ejecuta un script Python:

   ```bash
   python "P3 - MinMax/MinMax.py"
   python "P5 - Inferencia Bayesiana/problema1.py"
   python "Proyecto final/river_mdp.py"
   ```

3. O abre los notebooks de Jupyter:

   ```bash
   jupyter notebook
   ```

---

## 📬 Contacto

¿Interesado en discutir alguna práctica o colaborar?

📧 **Contacto**: [claudialbombin@alu.icai.comillas.edu](mailto:claudialbombin@alu.icai.comillas.edu)
🔗 **LinkedIn**: [www.linkedin.com/in/claudia-lopez-bombin](https://www.linkedin.com/in/claudia-lopez-bombin)
🐙 **GitHub**: [github.com/claudialbzz](https://github.com/claudialbzz)

---

> "La inteligencia artificial es la nueva electricidad."
> — *Andrew Ng*

🧭 **Keep learning. Keep building. Keep evolving.**
