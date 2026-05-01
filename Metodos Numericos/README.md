# 🔢 Métodos Numéricos

Bienvenido a la carpeta de **Métodos Numéricos**, asignatura del **Grado en Ingeniería Matemática (iMAT)** en **ICAI**. Aquí se recopilan todas las prácticas, hojas de ejercicios y el proyecto final, orientados al diseño e implementación de algoritmos computacionales para resolver problemas matemáticos complejos.

---

## 🎯 Sobre la Asignatura

**Métodos Numéricos** estudia técnicas algorítmicas que permiten obtener soluciones aproximadas (y cuantificar su error) para problemas que no tienen solución analítica cerrada o cuya resolución exacta resulta computacionalmente inviable. Se trabaja tanto en Python como en MATLAB.

---

## 📂 Contenido de la Carpeta

### 🚀 [P1 - Arianne 5](./P1%20-%20Arianne%205/)
*Análisis de errores numéricos en sistemas críticos*
- 🛰️ Estudio del error de aritmética en coma flotante como causa de fallos reales
- 📉 Simulación del error acumulado en cálculo de tiempo y su impacto en la posición
- 🔍 Visualización gráfica de la divergencia entre trayectoria real y calculada
- ⚠️ Análisis cuantitativo del error relativo en el instante de intercepción

### 📐 [P2 - Interpolación de Newton](./P2%20-%20Interpolacion%20de%20Newton/)
*Construcción y evaluación de polinomios interpoladores*
- 🧮 Implementación de la interpolación polinómica de Newton (diferencias divididas)
- 📊 Evaluación del polinomio interpolador en puntos arbitrarios
- 📈 Visualización de la curva interpolante y los nodos de interpolación
- 🔬 Análisis del error de interpolación

### 〰️ [P3 - Splines Cúbicos](./P3%20-%20Splines%20cubicos/)
*Interpolación suave por tramos mediante splines*
- 🔗 Construcción de splines cúbicos naturales y sujetos
- 📐 Resolución del sistema lineal de condiciones de continuidad y suavidad
- 📊 Comparación entre interpolación polinómica global y splines
- 🌊 Visualización de la curva resultante por tramos (ejercicios 4, 5 y 6)

### ∫ [P4 - Derivación e Integración Numérica](./P4%20-%20Derivacion%20e%20Integracion%20Numerica/)
*Aproximación numérica de derivadas e integrales*
- 📏 Fórmulas de diferencias finitas (hacia adelante, hacia atrás y centradas)
- ∫ Métodos de integración: regla del trapecio, Simpson y cuadratura de Gauss
- 📉 Estimación y control del error de truncamiento
- 🧮 Aplicaciones a funciones reales (ejercicios 1 a 3)

### 🖼️ [P6 - Esteganografía de Imágenes con Factorización LU](./P6/)
*Ocultación de información en imágenes mediante álgebra lineal numérica*
- 🔐 Cifrado de imágenes secretas dentro de imágenes de cobertura usando factorización LU
- 🖤 Procesamiento de imágenes en escala de grises y en color (RGB)
- 🧩 Implementación de la mezcla y recuperación mediante operaciones matriciales (L, U)
- 📓 Cuaderno Jupyter completo con experimentos y visualizaciones (`todo.ipynb`)
- 🌈 Scripts especializados: `grises.py` (escala de grises) y `rgb.py` (color)

### 📋 [Hojas B](./Hojas%20B/)
*Ejercicios complementarios en MATLAB*
- 🔵 `Hoja1B.mlx` — Ejercicios de la hoja práctica 1B en MATLAB Live Script
- 🔵 `Hoja2B.mlx` — Ejercicios de la hoja práctica 2B en MATLAB Live Script
- ⚙️ Implementación de algoritmos numéricos en entorno MATLAB

### 🏆 [Proyecto Final — Simulación Yard Sale](./Proyecto%20Final/)
*Modelado estocástico de distribución de riqueza*
- 💰 Implementación del modelo económico *Yard Sale* (intercambio aleatorio de riqueza)
- 📊 Estudio de la concentración de riqueza y emergencia de la desigualdad
- 🎲 Simulación Monte Carlo de transacciones entre agentes
- 📈 Análisis estadístico de la distribución de riqueza a lo largo del tiempo
- 📓 Notebook Jupyter con visualizaciones y resultados (`proyecto_yard_sale_3.ipynb`)

---

## 🗂️ Estructura de la Carpeta

```
Metodos Numericos/
├── P1 - Arianne 5/                        # Análisis de errores en coma flotante
│   ├── prueba.py                          # Simulación del error de intercepción
│   └── extra1.py                          # Ejercicio adicional
├── P2 - Interpolacion de Newton/          # Interpolación polinómica
│   └── main.py                            # Implementación completa
├── P3 - Splines cubicos/                  # Interpolación por splines
│   └── ejercicio456.py                    # Ejercicios 4, 5 y 6
├── P4 - Derivacion e Integracion Numerica/ # Diferenciación e integración
│   └── ejercicio1_3.py                    # Ejercicios 1 a 3
├── P6/                                    # Esteganografía con factorización LU
│   ├── grises.py                          # Procesamiento en escala de grises
│   ├── rgb.py                             # Procesamiento en color RGB
│   ├── todo.ipynb                         # Cuaderno Jupyter completo
│   └── [imágenes de prueba]
├── Hojas B/                               # Ejercicios en MATLAB
│   ├── Hoja1B.mlx
│   └── Hoja2B.mlx
└── Proyecto Final/                        # Proyecto integrador
    └── proyecto_yard_sale_3.ipynb
```

---

## 🛠️ Tecnologías y Herramientas

| Área | Tecnologías |
|------|-------------|
| **Lenguajes** | Python, MATLAB |
| **Librerías Python** | NumPy, SciPy, Matplotlib, Pillow, Jupyter |
| **Entornos** | Jupyter Notebook, MATLAB Live Script |
| **Técnicas** | Interpolación, integración numérica, factorización LU, simulación Monte Carlo |

---

## 📖 Cómo Navegar Esta Carpeta

1. **Por práctica**: Cada carpeta `Pn` corresponde a una práctica numerada de la asignatura
2. **Hojas B**: Ejercicios complementarios realizados en MATLAB
3. **Proyecto Final**: Trabajo integrador que aplica múltiples técnicas de la asignatura

```bash
# Ejemplo: ejecutar una práctica de Python
cd "P2 - Interpolacion de Newton"
python main.py

# Ejemplo: abrir el proyecto final en Jupyter
cd "Proyecto Final"
jupyter notebook proyecto_yard_sale_3.ipynb
```

---

## 🌟 Proyecto Destacado

- **Simulación Yard Sale** — Proyecto final que modela matemáticamente cómo la riqueza se concentra en pocas manos mediante intercambios aleatorios, usando simulación Monte Carlo y análisis estadístico de distribuciones.

---

> "En matemáticas no entiendes las cosas, simplemente te acostumbras a ellas."
> — *John von Neumann*

🧭 **Keep learning. Keep building. Keep exploring.**