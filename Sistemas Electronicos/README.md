# ⚡ Sistemas Electrónicos

Bienvenido al directorio de **Sistemas Electrónicos**, asignatura del **Grado en Ingeniería Matemática (iMAT)** en **ICAI**. Aquí se recogen todas las prácticas de laboratorio, trabajos previos, el proyecto final y los materiales de examen desarrollados a lo largo del curso.

La asignatura se centra en el **control de hardware mediante programación en Python** sobre una **Raspberry Pi**, abarcando desde la soldadura básica y la comunicación serie hasta el manejo de GPIO, temporizadores, PWM, conversores analógico-digital y el desarrollo de aplicaciones integradas.

---

## 🎯 Contenidos de la Asignatura

- 🔌 Programación de **entradas/salidas digitales** (GPIO)
- ⏱️ **Temporizadores**, scheduling y control de tiempo
- 🌀 Modulación por anchura de pulso (**PWM**) y control de motores/servos
- 📈 **Conversores analógico-digital (ADC)** y lectura de sensores
- 🔔 Manejo de **eventos y callbacks** (detección de flancos, niveles)
- 🔵 Comunicación **Bluetooth** y desarrollo de dashboards
- 🧠 Máquinas de estados y patrones de programación embebida

---

## 📂 Estructura del Directorio

```
Sistemas Electronicos/
├── Lab01/                    # Soldadura y primeros pasos con el sistema de desarrollo
├── Lab02/                    # Introducción al laboratorio
├── Lab03/                    # Entradas y salidas digitales (GPIO)
│   └── Trabajo previo/       # Scripts de preparación (apartados 1–5)
├── Lab04/                    # Temporizadores y PWM
│   └── Trabajo Previo/       # Scripts de preparación (partes 1–2 + opcionales)
├── Lab05/                    # Sesiones avanzadas con sensores y ADC
│   ├── Sesion 1/             # Curvas y caracterización
│   └── Sesion 2/             # Aplicaciones multi-parte
├── Proyecto Final/           # Aplicación integrada con Bluetooth y dashboard
└── Examen Laboratorio/       # Materiales de examen ordinario, repesca y cachitos
```

---

## 🧪 Prácticas de Laboratorio

### 🔧 Lab01 — Soldadura y Primeros Pasos
*Introducción al entorno de desarrollo y al trabajo con hardware físico*
- 🪛 Técnicas básicas de soldadura
- 🍓 Primer contacto con la Raspberry Pi como sistema de desarrollo
- 📄 [`Práctica 01. Soldadura y primeros pasos con el sistema de desarrollo.pdf`]

### 🔬 Lab02 — Introducción al Laboratorio
*Familiarización con los instrumentos y herramientas del laboratorio*
- 🔭 Uso del osciloscopio, fuente de alimentación y multímetro
- 📄 [`Práctica 02. Introducción al laboratorio.pdf`]

### 🔌 Lab03 — Entradas y Salidas Digitales (GPIO)
*Control de pines de propósito general como entradas y salidas digitales*
- 💡 Configuración de LEDs, botones y señales digitales con `RPi.GPIO`
- 🧮 Trabajo previo con scripts Python para cada apartado (1–5)
- 📄 [`Práctica 3. Entradas y salidas digitales (GPIO).pdf`]

### ⏱️ Lab04 — Temporizadores y PWM
*Generación de señales periódicas y control de dispositivos mediante PWM*
- 🌀 Hardware PWM para control de motores y servomotores
- 🕰️ Uso de timers y señales de temporización
- 📄 [`Práctica 4. Temporizadores y PWM.pdf`]

### 📡 Lab05 — Sesiones Avanzadas
*Profundización en ADC, sensores analógicos y aplicaciones integradas*
- 📈 **Sesión 1**: Caracterización de curvas y conversión analógico-digital
- 🔗 **Sesión 2**: Aplicaciones multi-parte con integración de sensores

---

## 🚀 Proyecto Final

Aplicación integrada desarrollada en Python que combina varias tecnologías de la asignatura:

| Fichero | Descripción |
|---------|-------------|
| `basico.py` | Control básico de GPIO y lógica principal |
| `bluetooth.py` | Comunicación inalámbrica vía Bluetooth |
| `dashboard.py` | Interfaz de monitorización en tiempo real |
| `grabacion.py` | Módulo de captura y almacenamiento de datos |

---

## 📝 Examen de Laboratorio

Materiales de preparación y resolución de exámenes prácticos:

- 🗂️ **Examen Laboratorio**: Ejercicios resueltos del examen ordinario (ordinario 2024, extraordinario 2024, cerradura, morse, etc.)
- 🔁 **Examen Repesca**: Ejercicios del examen de recuperación (3 ejercicios + examen c)
- 🍪 **Cachitos**: Colección amplia de snippets y patrones reutilizables

  *Ejemplos de scripts en los cachitos*: `rpigpio_basico.py`, `detectar_flanco.py`, `hardware_pwm_motor.py`, `servomotor.py`, `conversor_ad_basico.py`, `threading.py`, `maquinas_estados.py`, `interpolacion.py`, `sched.py`, entre otros.

---

## 🛠️ Tecnologías y Herramientas

| Área | Tecnologías |
|------|-------------|
| **Lenguaje** | Python 3 |
| **Hardware** | Raspberry Pi, GPIO, ADC, motores, servos |
| **Librerías** | `RPi.GPIO`, `threading`, `sched`, `time` |
| **Comunicación** | Bluetooth, señales digitales/analógicas |
| **Entorno** | Linux (Raspberry Pi OS), SSH |
| **Documentación** | PDF, Jupyter Notebooks |

---

## 📖 Cómo Navegar Este Directorio

1. **Por práctica**: Accede a cada `LabXX/` para el guion en PDF y los scripts asociados
2. **Por tema**: Consulta los *cachitos* para ejemplos listos para usar de cada concepto
3. **Por proyecto**: Explora `Proyecto Final/` para ver la integración de todas las piezas

```bash
# Ejemplo: ejecutar un script básico de GPIO
cd "Lab03/Trabajo previo"
python3 apartado1.py

# Ejemplo: explorar los cachitos de examen
cd "Examen Laboratorio/cachitos"
ls *.py
```

---

> "La electrónica es la ciencia de hacer que los electrones trabajen para ti."

🧭 **Keep learning. Keep building. Keep exploring.**