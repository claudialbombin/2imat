# %% [markdown]
# # Notebook 00 – Exploración y Análisis Descriptivo (EDA)
#
# **Proyecto Final Machine Learning · Comillas ICAI · 2025/2026**
#
# Este notebook realiza un análisis exploratorio completo del dataset de rendimiento
# académico, incluyendo:
# - Dimensiones, tipos de variable y valores perdidos
# - Distribución de la variable objetivo
# - Estadísticos descriptivos de variables numéricas
# - Distribución de variables categóricas clave
# - Correlaciones y relaciones entre variables

# %% [markdown]
# ## 0. Imports y configuración

# %%
import sys, os
sys.path.append("../src")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import load_data, set_plot_style, plot_class_distribution, RANDOM_STATE

os.makedirs("../outputs", exist_ok=True)
set_plot_style()

# %% [markdown]
# ## 1. Carga del dataset

# %%
df = load_data("../rendimiento_estudiantes.csv")
print(f"Dimensiones: {df.shape[0]} filas × {df.shape[1]} columnas")
df.head(3)

# %% [markdown]
# ## 2. Tipos de variables y valores perdidos

# %%
info = pd.DataFrame({
    "dtype": df.dtypes,
    "n_unicos": df.nunique(),
    "n_nulos": df.isnull().sum(),
    "pct_nulos": (df.isnull().mean() * 100).round(2),
})
print(info.to_string())

# %%
# Comprobación: ¿hay alguna columna con nulos?
print("\nColumnas con valores nulos:")
nulos = df.isnull().sum()
print(nulos[nulos > 0] if nulos.any() else "  → Ninguna. Dataset completo.")

# %% [markdown]
# ## 3. Distribución de la variable objetivo

# %%
fig, ax = plt.subplots(figsize=(6, 4))
plot_class_distribution(df, col="objetivo", ax=ax)
counts = df["objetivo"].value_counts()
total = len(df)
for i, (cls, cnt) in enumerate(counts.items()):
    print(f"  {cls:>15}: {cnt:>5}  ({cnt/total*100:.1f}%)")
plt.tight_layout()
plt.savefig("../outputs/00_distribucion_objetivo.png", bbox_inches="tight")
plt.show()

# %% [markdown]
# > **Observación:** Las clases están desbalanceadas. `Graduado` representa ~50 %,
# > `Abandono` ~32 % y `Matriculado` ~18 %. Esto debe tenerse en cuenta en la tarea de
# > clasificación (uso de `class_weight='balanced'` o técnicas de resampling).

# %% [markdown]
# ## 4. Estadísticos descriptivos – Variables numéricas

# %%
num_cols = df.select_dtypes(include="number").columns.tolist()
desc = df[num_cols].describe().T
desc["cv"] = (desc["std"] / desc["mean"]).round(3)   # coef. de variación
print(desc.round(3).to_string())

# %% [markdown]
# ## 5. Distribución de variables numéricas

# %%
fig, axes = plt.subplots(4, 4, figsize=(18, 14))
axes = axes.flatten()
for i, col in enumerate(num_cols[:16]):
    axes[i].hist(df[col].dropna(), bins=30, color="steelblue", edgecolor="white")
    axes[i].set_title(col, fontsize=9)
    axes[i].set_xlabel("")
for j in range(i + 1, len(axes)):
    axes[j].set_visible(False)
plt.suptitle("Distribución de variables numéricas", fontsize=13, y=1.01)
plt.tight_layout()
plt.savefig("../outputs/00_histogramas_numericas.png", bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 6. Variables numéricas por clase objetivo (boxplots)

# %%
vars_interes = [
    "nota_admision", "nota_cualificacion_previa", "edad_al_matricularse",
    "nota_media_1sem", "nota_media_2sem",
    "asignaturas_1sem_aprobadas", "asignaturas_2sem_aprobadas",
]

fig, axes = plt.subplots(2, 4, figsize=(18, 9))
axes = axes.flatten()
for i, col in enumerate(vars_interes):
    sns.boxplot(data=df, x="objetivo", y=col, ax=axes[i], palette="Set2")
    axes[i].set_title(col, fontsize=9)
    axes[i].set_xlabel("")
for j in range(i + 1, len(axes)):
    axes[j].set_visible(False)
plt.suptitle("Variables numéricas por situación académica", fontsize=13, y=1.01)
plt.tight_layout()
plt.savefig("../outputs/00_boxplots_por_objetivo.png", bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 7. Variables categóricas clave

# %%
cat_cols = df.select_dtypes(include="object").columns.drop("objetivo").tolist()
# Mostrar las de menor cardinalidad (más informativas visualmente)
low_card = [c for c in cat_cols if df[c].nunique() <= 10]

fig, axes = plt.subplots(3, 3, figsize=(16, 12))
axes = axes.flatten()
for i, col in enumerate(low_card[:9]):
    order = df[col].value_counts().index
    sns.countplot(data=df, y=col, hue="objetivo", order=order,
                  ax=axes[i], palette="Set2")
    axes[i].set_title(col, fontsize=9)
    axes[i].set_xlabel("Frecuencia")
    axes[i].legend(fontsize=7, title="objetivo", title_fontsize=7)
for j in range(i + 1, len(axes)):
    axes[j].set_visible(False)
plt.suptitle("Variables categóricas vs. situación académica", fontsize=13, y=1.01)
plt.tight_layout()
plt.savefig("../outputs/00_categoricas_vs_objetivo.png", bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 8. Matriz de correlación (variables numéricas)

# %%
corr = df[num_cols].corr()

fig, ax = plt.subplots(figsize=(14, 12))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=False, cmap="coolwarm",
            center=0, linewidths=0.4, ax=ax)
ax.set_title("Matriz de correlación – variables numéricas", fontsize=13)
plt.tight_layout()
plt.savefig("../outputs/00_correlacion.png", bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 9. Correlación con la nota media del 2º semestre (objetivo regresión)

# %%
corr_target = df[num_cols].corr()["nota_media_2sem"].drop("nota_media_2sem").sort_values()

fig, ax = plt.subplots(figsize=(7, 7))
colors = ["tomato" if v < 0 else "steelblue" for v in corr_target]
corr_target.plot(kind="barh", ax=ax, color=colors)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_title("Correlación de Pearson con nota_media_2sem")
ax.set_xlabel("Correlación")
plt.tight_layout()
plt.savefig("../outputs/00_correlacion_target_regresion.png", bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 10. Resumen de hallazgos del EDA

# %%
print("""
RESUMEN EDA
===========
1. Dataset sin valores nulos → no es necesario imputar.
2. Variable objetivo desbalanceada (Graduado ~50%, Abandono ~32%, Matriculado ~18%).
3. Variables más discriminantes para clasificación:
   - nota_media_1sem, asignaturas_1sem_aprobadas (rendimiento inicial)
   - nota_media_2sem, asignaturas_2sem_aprobadas (rendimiento posterior — CUIDADO: data leakage en regresión)
   - nota_admision, nota_cualificacion_previa (perfil de entrada)
   - becado, deudor, matricula_al_dia (situación económica)
4. Para la regresión (nota_media_2sem): las variables del 2º semestre
   (asignaturas matriculadas, evaluadas, aprobadas, sin evaluación) son leakage y
   NO deben incluirse como predictores.
5. Alta correlación entre variables del 1er y 2º semestre → riesgo de multicolinealidad.
""")
