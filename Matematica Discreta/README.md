# 🔢 Matemática Discreta

Bienvenido a la carpeta de **Matemática Discreta** del repositorio **iMAT 2**, donde documento mi recorrido por esta asignatura del **Grado en Ingeniería Matemática (iMAT)** en **ICAI**.
Aquí reúno **todas las prácticas, algoritmos y entregables** desarrollados a lo largo del curso, aplicando la teoría matemática discreta a problemas reales de computación.

---

## 🎯 Sobre la Asignatura

La asignatura de **Matemática Discreta** enseña los fundamentos matemáticos que sustentan la **ciencia de la computación y la ingeniería**.
Combina el rigor matemático con aplicaciones prácticas en informática, trabajando aspectos como:

* 🔢 **Aritmética modular** y teoría de números
* 🔐 **Criptografía** y algoritmos de cifrado (RSA)
* 🪢 **Teoría de grafos** y algoritmos de rutas óptimas
* 🔗 **Lógica matemática** y métodos de demostración
* 📊 **Combinatoria** y técnicas de conteo

---

## 📚 Prácticas Incluidas

### 🧮 [P1 - IMATLAB](./P1%20-%20IMATLAB/)
*Sistema interactivo de resolución de ecuaciones en aritmética modular*
- 🔢 Librería `modular.py` con operaciones de aritmética modular (MCD, MCM, inverso modular, primos)
- 🖥️ Interfaz interactiva y por lotes (`imatlab.py`) para resolver ecuaciones modulares
- ⚡ Benchmarks de rendimiento de los algoritmos implementados
- ✅ Suite de tests de validación

### 🔐 [P2 - RSA](./P2%20-%20RSA/)
*Implementación del algoritmo de cifrado RSA y chat cifrado*
- 🔑 Generación de claves pública y privada RSA (`rsa.py`)
- 💬 Sistema de chat cifrado extremo a extremo (`criptochat.py`)
- 👤 Registro y gestión de usuarios (`registrarusuario.py`)
- 📄 Documentación teórica y memoria de la práctica

### 🗺️ [P3 - GPS](./P3%20-%20GPS/)
*Sistema de navegación GPS usando algoritmos de grafos sobre el callejero de Madrid*
- 🏙️ Carga y procesamiento del callejero real de Madrid (`callejero.py`)
- 📍 Cálculo de rutas óptimas con el algoritmo de Dijkstra (`grafo_pesado.py`, `gps.py`)
- 🚶 Variantes especializadas: peatón, coche, metro (`gps_peaton.py`, `gps_metro.py`)
- 🖱️ Versión interactiva con selección de origen y destino
- ✅ Tests completos de validación del sistema

---

## 🏗️ Estructura de la Carpeta

```
Matematica Discreta/
├── P1 - IMATLAB/          # Aritmética modular e IMAT-LAB
│   ├── imatlab.py         # Interfaz interactiva y por lotes
│   ├── modular.py         # Librería de aritmética modular
│   ├── benchmark.py       # Análisis de rendimiento
│   ├── tests/             # Tests de validación
│   └── Memoria P1.pdf     # Memoria de la práctica
├── P2 - RSA/              # Criptografía RSA y chat cifrado
│   ├── rsa.py             # Algoritmo RSA (generación de claves, cifrado)
│   ├── criptochat.py      # Chat con cifrado extremo a extremo
│   ├── registrarusuario.py# Gestión de usuarios
│   ├── modular.py         # Librería de soporte modular
│   ├── tests/             # Tests de validación
│   └── Memoria P2.pdf     # Memoria de la práctica
└── P3 - GPS/              # Sistema GPS con grafos
    ├── gps.py             # Sistema GPS principal
    ├── callejero.py       # Carga del callejero de Madrid
    ├── grafo_pesado.py    # Grafo pesado y algoritmo Dijkstra
    ├── gps_peaton.py      # Variante para peatones
    ├── gps_metro.py       # Variante para metro
    ├── gps_version_interactiva.py  # Interfaz interactiva
    ├── tests/             # Tests de validación
    └── Memoria P3.pdf     # Memoria de la práctica
```

---

## 🚀 Propósito

Más que un archivo de entregas, esta carpeta funciona como un **portfolio práctico de matemática discreta aplicada**.
Cada práctica parte de una base teórica y culmina en una implementación funcional y documentada:

* 🧮 De la aritmética modular a un **intérprete de comandos matemáticos**
* 🔐 De la teoría de números a un **sistema de comunicación segura**
* 🗺️ De la teoría de grafos a un **navegador GPS real**

> "Las matemáticas discretas son las matemáticas de la computación."
> — *Donald Knuth*

---

## 🛠️ Tecnologías y Herramientas

| Área | Tecnologías |
|------|-------------|
| **Lenguaje** | Python 3 |
| **Grafos** | NetworkX, implementación propia (Dijkstra) |
| **Datos** | pandas, OpenStreetMap |
| **Visualización** | Matplotlib |
| **Testing** | pytest |

---

## ⚙️ Requisitos y Uso

1. Instala las dependencias:

   ```bash
   pip install numpy matplotlib networkx pandas
   ```

2. Ejecuta IMATLAB en modo interactivo:

   ```bash
   cd "P1 - IMATLAB"
   python imatlab.py
   ```

3. Lanza el chat cifrado con RSA:

   ```bash
   cd "P2 - RSA"
   python criptochat.py
   ```

4. Inicia el sistema GPS:

   ```bash
   cd "P3 - GPS"
   python gps_version_interactiva.py
   ```

---

## 📬 Contacto

¿Te interesa comentar alguna implementación, compartir ideas sobre algoritmos discretos o colaborar en proyectos de matemática aplicada?

📧 **Contacto**: [claudialbombin@alu.icai.comillas.edu](mailto:claudialbombin@alu.icai.comillas.edu)
🔗 **LinkedIn**: [www.linkedin.com/in/claudia-lopez-bombin](https://www.linkedin.com/in/claudia-lopez-bombin)
🐙 **GitHub**: [github.com/claudialbzz](https://github.com/claudialbzz)

---

> "Las matemáticas no son acerca de números, ecuaciones, computaciones o algoritmos: es acerca del entendimiento."
> — *William Paul Thurston*

🧭 **Keep reasoning. Keep proving. Keep discovering.**
