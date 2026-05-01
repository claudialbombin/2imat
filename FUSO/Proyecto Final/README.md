# Proyecto-FUSO

# 📦 PROYECTO FUNDAMENTOS DE SISTEMAS OPERATIVOS

## 📋 INFORMACIÓN DEL PROYECTO

**Fecha Disponible:** 5 de Noviembre  
**Fecha de Entrega:** 28 de Noviembre  
**Realizado por:** Claudia Maria Lopez Bombin - Gonzalo Velasco Lucas

## 🗂️ ESTRUCTURA DE ARCHIVOS DE ENTREGA

### 📄 DOCUMENTACIÓN
| Archivo | Descripción |
|---------|-------------|
| `memoria.pdf` | Documentación completa del proyecto |
| `poster_proyecto.pdf` | Póster resumen del proyecto |

### 🐧 SCRIPTS ALPINE LINUX
| Archivo | Descripción |
|---------|-------------|
| `apartado1_Claudia_Gonzalo.sh` | Script de instalación de paquetes Alpine Linux |
| `requirements.txt` | Dependencias Python del proyecto |

### 🚀 SCRIPTS DE DESPLIEGUE
| Archivo | Descripción |
|---------|-------------|
| `apartado_despliegue_Bash_Claudia_Gonzalo.sh` | Script de despliegue completo del proyecto Flask |

### 📊 SCRIPTS DE PROCESAMIENTO DE DATOS
| Archivo | Descripción |
|---------|-------------|
| `procesamiento_datos.sh` | Descarga y procesamiento de datasets Gowalla |
| `script_estadisticas_python.py` | Estadísticas de ciudades (comparación Bash vs Python) |
| `topn_selection_Claudia_Gonzalo.py` | Top N usuarios con más visitas |

### ⚡ CÓDIGOS PYTHON ESPECÍFICOS
| Archivo | Descripción |
|---------|-------------|
| `compare_execution_code.py` | Implementación de multiplicación de matrices (secuencial vs paralelo) |
| `peticiones_request.py` | Cliente para peticiones automáticas a la API Flask |

### 🔧 MODIFICACIONES AL PROYECTO ORIGINAL
| Archivo | Descripción |
|---------|-------------|
| `src_model_modifications.py` | Código EXACTO para modificar `src/model.py` del proyecto original |

## 📁 ESTRUCTURA DEL ZIP DE ENTREGA

```
Claudia_Maria_Lopez_Bombin_Gonzalo_Velasco_Lucas_ProyectoDespliegue.zip/
│
├── 📄 memoria.pdf
├── 📄 poster_proyecto.pdf
│
├── 🐧 apartado1_Claudia_Gonzalo.sh
├── 🐧 requirements.txt
│
├── 🚀 apartado_despliegue_Bash_Claudia_Gonzalo.sh
│
├── 📊 procesamiento_datos.sh
├── 📊 script_estadisticas_python.py
├── 📊 topn_selection_Claudia_Gonzalo.py
│
├── ⚡ compare_execution_code.py
├── ⚡ peticiones_request.py
│
└── 🔧 src_model_modifications.py
```

## 🛠️ INSTRUCCIONES DE USO

### 1. Configuración Inicial
```bash
# Ejecutar como root en Alpine Linux
chmod +x apartado1_Claudia_Gonzalo.sh
./apartado1_Claudia_Gonzalo.sh
```

### 2. Despliegue del Proyecto
```bash
# Ejecutar como alumnoimat
chmod +x apartado_despliegue_Bash_Claudia_Gonzalo.sh
./apartado_despliegue_Bash_Claudia_Gonzalo.sh
```

### 3. Procesamiento de Datos
```bash
# Ejecutar para descargar y procesar datasets
chmod +x procesamiento_datos.sh
./procesamiento_datos.sh
```

### 4. Modificación del Proyecto Original
- Copiar el contenido de `src_model_modifications.py` en `src/model.py` del proyecto Flask
- Reemplazar la función `compare_execution()` existente

## 📊 FUNCIONALIDADES IMPLEMENTADAS

### ✅ Servicios Flask Completados
- **Train and Evaluate** - Entrenamiento y evaluación de modelos ML
- **Dataset Statistics** - Estadísticas de datasets
- **Exploratory Data Analysis** - Análisis exploratorio de datos
- **Clean Images** - Limpieza de imágenes generadas
- **Generate Synthetic Dataset** - Generación de datasets sintéticos
- **Compare Execution** - Comparación secuencial vs paralelo
- **Show HTML Files** - Visualización de mapas generados

### ✅ Scripts de Automatización
- Instalación automática de paquetes Alpine
- Despliegue automático del proyecto Flask
- Procesamiento automático de datos Gowalla
- Generación automática de mapas HTML
- Peticiones automáticas a la API

## 🔧 DEPENDENCIAS PRINCIPALES

- **Python 3** + entornos virtuales
- **Flask** - Framework web
- **scikit-learn** - Machine learning
- **pandas + numpy** - Procesamiento de datos
- **matplotlib + seaborn** - Visualizaciones
- **requests** - Peticiones HTTP

## 📝 NOTAS IMPORTANTES

1. **Configurar IP correcta** en `peticiones_request.py`
2. **Seguir instrucciones** en `src_model_modifications.py` para modificar el proyecto original
3. **Todos los scripts** deben tener permisos de ejecución
4. **Verificar conexión de red** antes de ejecutar los scripts

---

**🎓 Proyecto realizado para Fundamentos de Sistemas Operativos**  
**📅 Noviembre 2025**