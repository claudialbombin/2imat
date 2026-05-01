# Predicción del Éxito Académico en Educación Superior

## Machine Learning · Clasificación · Regresión · Clustering

---

## Tabla de contenidos

1. [¿Qué es este proyecto?](#qué-es-este-proyecto)
2. [Por qué existe este proyecto](#por-qué-existe-este-proyecto)
3. [Qué aprenderás](#qué-aprenderás)
4. [Contexto matemático](#contexto-matemático)
5. [Estructura del proyecto](#estructura-del-proyecto)
6. [Instalación y configuración](#instalación-y-configuración)
7. [Cómo usar](#cómo-usar)
8. [Entendiendo los resultados](#entendiendo-los-resultados)
9. [Resultados y hallazgos](#resultados-y-hallazgos)
10. [Habilidades demostradas](#habilidades-demostradas)
11. [Referencias y lecturas adicionales](#referencias-y-lecturas-adicionales)

---

## ¿Qué es este proyecto?

Este repositorio contiene un **análisis completo de Machine Learning** aplicado a la predicción del rendimiento académico de estudiantes en educación superior. El proyecto aborda tres tareas distintas sobre el mismo dataset.

### 1. Clasificación del destino académico

**El problema:** Dado el perfil de un estudiante (datos de admisión, situación socioeconómica, rendimiento del primer semestre), ¿cuál será su situación final: abandono, matriculado o graduado?

**La solución:** Se comparan cuatro modelos — Regresión Logística, Árbol de Decisión, Random Forest y Gradient Boosting — mediante validación cruzada estratificada de 5 pliegues. Se gestiona el desbalanceo de clases con `class_weight='balanced'`.

**El resultado:** La Regresión Logística obtiene el mejor F1-macro en validación cruzada:

```
Evaluando Logistic Regression... F1-macro = 0.7175 ± 0.0081
Evaluando Decision Tree...       F1-macro = 0.6723 ± 0.0211
Evaluando Random Forest...       F1-macro = 0.6888 ± 0.0171
Evaluando Gradient Boosting...   F1-macro = 0.7143 ± 0.0121
```

### 2. Regresión de la nota media del 2.º semestre

**El problema:** Predecir la calificación media del segundo semestre de un estudiante sin usar variables del propio semestre (para evitar *data leakage*).

**La solución:** Se aplican Ridge, Lasso, Árbol de Decisión, Random Forest y Gradient Boosting, evaluados con RMSE, MAE y R² mediante validación cruzada de 5 pliegues.

**El resultado:** Gradient Boosting y Random Forest lideran con R² ≈ 0.53:

```
              RMSE    MAE     R²
Ridge         1.055   0.829   0.399
Lasso         1.069   0.838   0.383
Decision Tree 0.998   0.756   0.462
Random Forest 0.931   0.717   0.532
Grad. Boosting 0.930  0.707   0.533  ← mejor
```

### 3. Clustering y análisis no supervisado

**El problema:** ¿Existen perfiles naturales de estudiantes en los datos que no dependan de la etiqueta de destino académico?

**La solución:** PCA para reducción de dimensionalidad, K-Means con selección del número óptimo de clusters (método del codo + silhouette), y clustering jerárquico como contraste.

**El resultado:** Se identifican 4 clusters con distribuciones de situación académica muy diferenciadas:

```
Cluster  Abandono  Graduado  Matriculado  Perfil
   0       42.1%    42.9%      15.1%     Maduros con rendimiento medio
   1       21.3%    54.1%      24.6%     Perfil medio (mayoritario)
   2        9.2%    79.5%      11.3%     Alto rendimiento — muy bajo riesgo
   3       80.0%     9.7%      10.4%     Alto riesgo de abandono
```

---

## Por qué existe este proyecto

### Motivación

El abandono universitario representa un coste humano, social y económico significativo. Identificar tempranamente los estudiantes en riesgo permite a las instituciones actuar de forma preventiva. Este proyecto demuestra cómo el Machine Learning puede extraer patrones accionables de datos académicos.

### Propósito educativo

El proyecto enseña de forma práctica:

- **Aprendizaje supervisado:** Clasificación y regresión con pipelines de scikit-learn
- **Aprendizaje no supervisado:** PCA, K-Means y clustering jerárquico
- **Prevención de data leakage:** Diseño riguroso del conjunto de características
- **Métricas adecuadas al problema:** F1-macro para datos desbalanceados, RMSE/R² para regresión
- **Interpretabilidad:** Importancia de variables (MDI y permutación)
- **Validación estadística:** Validación cruzada, intervalos de confianza, ARI

---

## Qué aprenderás

### Conceptos fundamentales

| Concepto | Cómo lo enseña este proyecto |
|----------|------------------------------|
| **Clasificación multiclase** | Predecir entre 3 clases con métricas F1-macro y matrices de confusión |
| **Regresión supervisada** | Estimación continua con RMSE, MAE y R² |
| **Reducción de dimensionalidad** | PCA para visualización e input a clustering |
| **Clustering** | K-Means con selección de k mediante codo y silhouette |
| **Data leakage** | Exclusión razonada de variables que contaminarían el modelo |
| **Desbalanceo de clases** | `class_weight='balanced'` y su efecto en recall por clase |
| **Validación cruzada** | Estimación robusta del error de generalización |
| **Interpretabilidad** | MDI vs. importancia por permutación |

### Habilidades prácticas

| Habilidad | Aplicación más allá de este proyecto |
|-----------|--------------------------------------|
| **Diseño de pipelines** | Cualquier flujo preprocesado → modelo en producción |
| **Comparativa de modelos** | Selección rigurosa de algoritmos para un dominio |
| **Visualización estadística** | Comunicar resultados cuantitativos con claridad |
| **Gestión de datos reales** | Variables mixtas, desbalanceo, valores extremos |

---

## Contexto matemático

### Validación cruzada k-fold estratificada

Para la clasificación, la métrica principal es el **F1-macro**, calculada como la media no ponderada del F1 por clase:

```
F1_macro = (1/C) × Σ(c=1 to C) F1_c

donde F1_c = 2 × (precision_c × recall_c) / (precision_c + recall_c)
```

Se usa F1-macro (en lugar de accuracy) porque las clases están desbalanceadas:

| Clase | Frecuencia aproximada |
|-------|-----------------------|
| Graduado | 50 % |
| Abandono | 32 % |
| Matriculado | 18 % |

### Error cuadrático medio y R²

Para la regresión, los indicadores clave son:

```
RMSE = sqrt( (1/N) × Σ (y_i - ŷ_i)² )

R² = 1 - SS_res / SS_tot    (0 = modelo nulo, 1 = ajuste perfecto)
```

Un R² de 0.53 significa que el modelo explica el 53 % de la varianza de la nota media del 2.º semestre usando solo información previa al semestre.

### PCA — varianza explicada

```
Varianza acumulada = Σ(i=1 to k) λ_i / Σ(i=1 to p) λ_i
```

| Componentes | Varianza explicada |
|-------------|-------------------|
| 2 (para visualización) | 29.8 % |
| 9 | 80 % |
| 11 | 90 % |

### Silhouette score

Mide la calidad del clustering: qué tan compacto es cada cluster y cuánto se separa de los demás:

```
s(i) = (b(i) - a(i)) / max(a(i), b(i))
```

Donde `a(i)` es la distancia media intra-cluster y `b(i)` la distancia media al cluster vecino más cercano. El rango es [-1, 1]; valores cercanos a 1 indican clusters bien separados.

---

## Estructura del proyecto

```
Proyecto final/
│
├── README.md                          ← Este fichero
├── requirements.txt                   ← Dependencias Python
├── rendimiento_estudiantes.csv        ← Dataset (4 424 estudiantes)
│
├── notebooks/
│   ├── 00_EDA.ipynb                   ← Exploración y análisis descriptivo
│   ├── 01_clasificacion.ipynb         ← Tarea 1: Clasificación multiclase
│   ├── 02_regresion.ipynb             ← Tarea 2: Regresión de nota media
│   └── 03_no_supervisado.ipynb        ← Tarea 3: PCA + K-Means
│
├── src/
│   └── utils.py                       ← Funciones auxiliares compartidas
│
├── outputs/                           ← Figuras y predicciones generadas
│   ├── 00_distribucion_objetivo.png
│   ├── 00_correlacion.png
│   ├── 01_confusion_matrices.png
│   ├── 01_comparativa_cv.png
│   ├── 01_feature_importances_mdi.csv
│   ├── 01_predicciones_clasificacion.csv
│   ├── 01_resultados_test.csv
│   ├── 02_real_vs_predicho.png
│   ├── 02_residuos.png
│   ├── 02_predicciones_regresion.csv
│   ├── 02_resultados_test.csv
│   ├── 03_pca_varianza.png
│   ├── 03_kmeans_seleccion_k.png
│   ├── 03_heatmap_clusters.png
│   ├── 03_pca_clusters_vs_objetivo.png
│   ├── 03_etiquetas_cluster.csv
│   └── ...
│
└── Informe final/                     ← Informes en PDF (ES e EN)
    ├── Informe_es_Claudia_Lopez.pdf
    └── Informe_en_Claudia_Lopez.pdf
```

---

## Instalación y configuración

**Requisitos previos:**
- Python 3.9 o superior
- pip

**Paso 1: Instalar dependencias**

```bash
pip install -r requirements.txt
```

**Qué se instala:**

| Paquete | Versión mínima | Uso |
|---------|---------------|-----|
| `pandas` | ≥ 2.0 | Manipulación del dataset |
| `numpy` | ≥ 1.24 | Operaciones numéricas |
| `matplotlib` | ≥ 3.7 | Visualizaciones |
| `seaborn` | ≥ 0.12 | Gráficos estadísticos |
| `scikit-learn` | ≥ 1.3 | Modelos, pipelines, métricas |
| `xgboost` | ≥ 2.0 | Gradient Boosting avanzado |
| `shap` | ≥ 0.44 | Interpretabilidad de modelos |
| `imbalanced-learn` | ≥ 0.11 | Herramientas para desbalanceo |
| `jupyterlab` | ≥ 4.0 | Entorno de notebooks |

**Paso 2: Verificar instalación**

```bash
python -c "import sklearn; print('scikit-learn', sklearn.__version__)"
```

---

## Cómo usar

**Paso 1: Colocar el dataset**

Asegúrate de que `rendimiento_estudiantes.csv` está en la carpeta `Proyecto final/`.

**Paso 2: Abrir JupyterLab**

```bash
jupyter lab
```

**Paso 3: Ejecutar los notebooks en orden**

```
00_EDA.ipynb           → análisis exploratorio, no genera modelos
01_clasificacion.ipynb → entrena y evalúa modelos de clasificación
02_regresion.ipynb     → entrena y evalúa modelos de regresión
03_no_supervisado.ipynb → PCA, K-Means, caracterización de clusters
```

> **Semilla aleatoria global:** `RANDOM_STATE = 42` en todos los notebooks y en `src/utils.py`. Garantiza reproducibilidad completa.

**Todos los resultados** (figuras PNG y tablas CSV) se guardan automáticamente en `outputs/`.

---

## Entendiendo los resultados

### Notebook 00 — Análisis exploratorio

Explora la distribución de la variable objetivo, correlaciones entre variables, valores perdidos y relación de cada predictor con el destino académico. Los gráficos generados orientan las decisiones de preprocesado de los siguientes notebooks.

### Notebook 01 — Clasificación

El pipeline estándar es:

```
Datos crudos
    ↓
ColumnTransformer
  ├── StandardScaler (variables numéricas)
  └── OneHotEncoder (variables categóricas)
    ↓
Clasificador (LR / DT / RF / GB)
    ↓
Predicciones + métricas
```

**Cómo leer la tabla de resultados:**

```
                     Accuracy  F1-macro  F1-weighted
Logistic Regression    0.738     0.691       0.747   ← mejor F1-macro
Decision Tree          0.673     0.636       0.690
Random Forest          0.777     0.682       0.754
Gradient Boosting      0.764     0.684       0.754
```

- **F1-macro:** media no ponderada del F1 por clase → penaliza por igual fallos en clases minoritarias
- **F1-weighted:** media ponderada por soporte → favorece a las clases mayoritarias
- **Accuracy:** porcentaje de aciertos totales

**Informe de clasificación del mejor modelo (Logistic Regression):**

```
              precision  recall  f1-score  support
abandono        0.80     0.71     0.75      284
graduado        0.86     0.82     0.84      442
matriculado     0.42     0.56     0.48      159

accuracy                          0.74      885
macro avg       0.69     0.70     0.69      885
```

La clase `matriculado` es la más difícil de predecir (F1 = 0.48) por ser la menos representada y la de perfil más ambiguo.

### Notebook 02 — Regresión

**Variables excluidas por data leakage:**

| Variable excluida | Razón |
|-------------------|-------|
| `asignaturas_2sem_matriculadas` | Describe el 2.º semestre simultáneamente al target |
| `asignaturas_2sem_evaluadas` | Ídem |
| `asignaturas_2sem_aprobadas` | Correlación casi perfecta con la nota |
| `asignaturas_2sem_sin_evaluacion` | Ídem |
| `asignaturas_2sem_convalidadas` | Ídem |
| `objetivo` | Situación final determinada parcialmente por el 2.º semestre |

**Cómo leer los resultados de regresión:**

```
               RMSE    MAE     R²
Ridge          1.055   0.829   0.399
Lasso          1.069   0.838   0.383
Decision Tree  0.998   0.756   0.462
Random Forest  0.931   0.717   0.532
Grad. Boosting 0.930   0.707   0.533
```

- **RMSE:** error típico en la misma escala que la nota (escala 0–20 aprox.)
- **MAE:** error absoluto medio, más robusto a outliers
- **R²:** proporción de varianza explicada (cuanto más alto, mejor)

### Notebook 03 — Aprendizaje no supervisado

**Selección de k (número de clusters):**

```
k= 2: silhouette=0.2150
k= 3: silhouette=0.2206
k= 4: silhouette=0.2244  ← óptimo
k= 5: silhouette=0.1279
```

**Distribución de situación académica por cluster:**

```
Cluster  Abandono  Graduado  Matriculado  Interpretación
   0       42.1%    42.9%      15.1%     Perfil maduro, riesgo moderado
   1       21.3%    54.1%      24.6%     Perfil medio (2 120 estudiantes)
   2        9.2%    79.5%      11.3%     Alto rendimiento, muy bajo riesgo
   3       80.0%     9.7%      10.4%     Muy alto riesgo de abandono
```

**Estabilidad del clustering:**

```
ARI entre semillas de K-Means: 0.48–0.84  (moderado-alto)
ARI K-Means vs Jerárquico:     0.44       (estructura moderada)
```

---

## Resultados y hallazgos

### Hallazgos clave

| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| **F1-macro clasificación** | 0.691 (LR) | Buen equilibrio entre las 3 clases |
| **Accuracy clasificación** | 0.738 | 74 de cada 100 estudiantes clasificados correctamente |
| **R² regresión** | 0.533 (GB) | El modelo explica el 53 % de la varianza de la nota |
| **RMSE regresión** | 0.930 | Error típico de ~0.93 puntos en la nota media |
| **Clusters identificados** | 4 | Perfiles diferenciados con distinta tasa de abandono |
| **Varianza PCA (2 comp.)** | 29.8 % | Estructura parcialmente visible en 2D |
| **Cluster de alto riesgo** | 18.8 % del total | 1 de cada 5 estudiantes en el cluster con 80 % de abandono |

### Predictores más importantes (clasificación)

Las variables con mayor importancia por permutación en la tarea de clasificación son variables del rendimiento del 1.er semestre (`nota_media_1sem`, `asignaturas_1sem_aprobadas`) y variables socioeconómicas (`matricula_al_dia`, `deudor`, `becado`). Esto indica que el rendimiento temprano y la situación financiera son los mejores indicadores del destino académico.

### Rendimiento comparativo de modelos

| Tarea | Mejor modelo | Métrica principal |
|-------|-------------|-------------------|
| Clasificación | Logistic Regression | F1-macro = 0.691 |
| Regresión | Gradient Boosting | R² = 0.533 |
| Clustering | K-Means k=4 | Silhouette = 0.224 |

---

## Habilidades demostradas

### Técnicas de ML

| Categoría | Habilidades | Localización |
|-----------|-------------|-------------|
| **Preprocesado** | ColumnTransformer, StandardScaler, OneHotEncoder | Todos los notebooks |
| **Clasificación** | LR, DT, RF, Gradient Boosting, class_weight | `01_clasificacion.ipynb` |
| **Regresión** | Ridge, Lasso, RF Regressor, GB Regressor | `02_regresion.ipynb` |
| **No supervisado** | PCA, K-Means, Agglomerative Clustering | `03_no_supervisado.ipynb` |
| **Evaluación** | CV estratificada, F1-macro, RMSE, R², ARI | Todos los notebooks |
| **Interpretabilidad** | Importancia MDI, importancia por permutación | `01`, `02` |
| **Data leakage** | Justificación y exclusión de variables | `02_regresion.ipynb` |

### Buenas prácticas

| Práctica | Cómo se demuestra |
|----------|--------------------|
| **Reproducibilidad** | `RANDOM_STATE = 42` global en todos los notebooks |
| **Reutilización de código** | `src/utils.py` compartido por los 4 notebooks |
| **Pipelines robustos** | `sklearn.Pipeline` evita fugas de información en CV |
| **Documentación** | Markdown detallado en cada notebook, README completo |
| **Organización** | Salidas separadas en `outputs/`, notebooks numerados |

---

## Referencias y lecturas adicionales

### Dataset

- **Realinho, V., Vieira Martins, M., Machado, J., & Baptista, L. (2022).** *Predicting Student Dropout and Academic Success.* Data, 7(11), 146. [https://doi.org/10.3390/data7110146](https://doi.org/10.3390/data7110146)

- Dataset disponible en UCI Machine Learning Repository: [Predict students' dropout and academic success](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success)

### Machine Learning y scikit-learn

- **Géron, A. (2022).** *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow* (3.ª ed.). O'Reilly.
- **Pedregosa, F. et al. (2011).** Scikit-learn: Machine Learning in Python. *JMLR*, 12, 2825–2830.

### Métodos de clustering y PCA

- **Jolliffe, I.T. (2002).** *Principal Component Analysis* (2.ª ed.). Springer.
- **Rousseeuw, P.J. (1987).** Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. *Journal of Computational and Applied Mathematics*, 20, 53–65.

### Interpretabilidad

- **Breiman, L. (2001).** Random Forests. *Machine Learning*, 45, 5–32.
- **Molnar, C. (2022).** *Interpretable Machine Learning* (2.ª ed.). [https://christophm.github.io/interpretable-ml-book/](https://christophm.github.io/interpretable-ml-book/)
