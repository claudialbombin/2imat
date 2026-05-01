# %% [markdown]
# # Notebook 03 – Tarea 3: Aprendizaje No Supervisado
#
# **Objetivo:** Identificar perfiles de estudiantes mediante técnicas no supervisadas.
#
# **Contenido:**
# 1. Selección y preprocesado del subconjunto de variables
# 2. PCA – reducción dimensional y análisis de varianza explicada
# 3. K-Means – selección de k (codo + silhouette)
# 4. Caracterización de los clusters
# 5. Visualización en 2D (PCA)
# 6. Estabilidad de los clusters
# 7. Relación de los clusters con la variable objetivo

# %% [markdown]
# ## 0. Imports y configuración

# %%
import sys, os, warnings
sys.path.append("../src")
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.pipeline import Pipeline

from utils import load_data, set_plot_style, encode_binary_cols, RANDOM_STATE

os.makedirs("../outputs", exist_ok=True)
set_plot_style()

# %% [markdown]
# ## 1. Selección de variables para clustering
#
# Criterio: variables que describen al estudiante en el momento de acceso y su
# desempeño en el primer semestre. Excluimos variables del 2º semestre para no
# contaminar el análisis con resultados finales, y excluimos la variable objetivo.
# También excluimos variables con muy alta cardinalidad categórica (nacionalidad,
# ocupación detallada) que dificultarían la interpretación de los clusters.

# %%
df = load_data("../rendimiento_estudiantes.csv")
df = encode_binary_cols(df)

# Subconjunto razonado de variables para clustering
VARS_CLUSTER = [
    # Perfil de entrada
    "nota_admision", "nota_cualificacion_previa", "edad_al_matricularse",
    # Situación socioeconómica
    "becado", "deudor", "matricula_al_dia", "desplazado",
    # Género y tipo de asistencia
    "genero", "asistencia_diurna_vespertina",
    # Rendimiento 1er semestre
    "asignaturas_1sem_matriculadas", "asignaturas_1sem_aprobadas",
    "nota_media_1sem", "asignaturas_1sem_sin_evaluacion",
    # Contexto macroeconómico
    "tasa_desempleo", "pib",
]

print(f"Variables seleccionadas para clustering ({len(VARS_CLUSTER)}):")
print(VARS_CLUSTER)

X_cl = df[VARS_CLUSTER].copy()
objetivo = df["objetivo"]  # guardamos para análisis posterior (no usada en clustering)

# %%
# Identificar tipo de cada variable en el subconjunto
cat_cols_cl = X_cl.select_dtypes(include="object").columns.tolist()
num_cols_cl = X_cl.select_dtypes(exclude="object").columns.tolist()
print(f"\nNuméricas: {num_cols_cl}")
print(f"Categóricas: {cat_cols_cl}")

# Preprocesado
prep_cl = ColumnTransformer([
    ("num", StandardScaler(), num_cols_cl),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols_cl),
])
X_prep = prep_cl.fit_transform(X_cl)
print(f"\nMatriz preprocesada: {X_prep.shape}")

# %% [markdown]
# ## 2. PCA – Reducción dimensional

# %%
pca = PCA(random_state=RANDOM_STATE)
pca.fit(X_prep)

varianza_acumulada = np.cumsum(pca.explained_variance_ratio_)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Varianza por componente
axes[0].bar(range(1, 21), pca.explained_variance_ratio_[:20],
            color="steelblue", edgecolor="white")
axes[0].set_title("Varianza explicada por componente")
axes[0].set_xlabel("Componente principal")
axes[0].set_ylabel("Proporción de varianza")

# Varianza acumulada
axes[1].plot(range(1, len(varianza_acumulada) + 1), varianza_acumulada,
             marker=".", color="steelblue")
axes[1].axhline(0.80, color="red", linestyle="--", label="80%")
axes[1].axhline(0.90, color="orange", linestyle="--", label="90%")
axes[1].set_title("Varianza acumulada explicada")
axes[1].set_xlabel("Nº de componentes")
axes[1].set_ylabel("Varianza acumulada")
axes[1].legend()

plt.suptitle("PCA – Análisis de varianza explicada", fontsize=12)
plt.tight_layout()
plt.savefig("../outputs/03_pca_varianza.png", bbox_inches="tight")
plt.show()

n_comp_80 = np.argmax(varianza_acumulada >= 0.80) + 1
n_comp_90 = np.argmax(varianza_acumulada >= 0.90) + 1
print(f"Componentes para explicar 80% de varianza: {n_comp_80}")
print(f"Componentes para explicar 90% de varianza: {n_comp_90}")

# %%
# Proyección en 2 componentes para visualización
pca2 = PCA(n_components=2, random_state=RANDOM_STATE)
X_2d = pca2.fit_transform(X_prep)
print(f"Varianza explicada por PC1+PC2: {pca2.explained_variance_ratio_.sum():.2%}")

# %%
# Biplot: cargas de las variables originales en los 2 primeros PCs
ohe_cl = prep_cl.named_transformers_["cat"]
cat_names_cl = ohe_cl.get_feature_names_out(cat_cols_cl).tolist()
feature_names_cl = num_cols_cl + cat_names_cl

loadings = pd.DataFrame(
    pca2.components_.T,
    index=feature_names_cl,
    columns=["PC1", "PC2"]
)

# Top variables por magnitud en PC1 y PC2
top_pc1 = loadings["PC1"].abs().nlargest(8).index
top_pc2 = loadings["PC2"].abs().nlargest(8).index
top_vars = list(set(top_pc1) | set(top_pc2))

fig, ax = plt.subplots(figsize=(8, 7))
for feat in top_vars:
    ax.arrow(0, 0, loadings.loc[feat, "PC1"] * 3,
             loadings.loc[feat, "PC2"] * 3,
             head_width=0.05, color="tomato", alpha=0.7)
    ax.text(loadings.loc[feat, "PC1"] * 3.2,
            loadings.loc[feat, "PC2"] * 3.2,
            feat, fontsize=7, ha="center")
ax.set_xlabel(f"PC1 ({pca2.explained_variance_ratio_[0]:.1%})")
ax.set_ylabel(f"PC2 ({pca2.explained_variance_ratio_[1]:.1%})")
ax.set_title("Biplot PCA – cargas de variables principales")
ax.axhline(0, color="gray", linewidth=0.5)
ax.axvline(0, color="gray", linewidth=0.5)
plt.tight_layout()
plt.savefig("../outputs/03_pca_biplot.png", bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 3. K-Means – Selección del número de clusters

# %%
# Usamos los datos preprocesados completos (no solo 2D) para el clustering
inertias = []
silhouettes = []
K_range = range(2, 11)

for k in K_range:
    km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
    labels = km.fit_predict(X_prep)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_prep, labels, sample_size=1000,
                                        random_state=RANDOM_STATE))
    print(f"k={k}: inertia={km.inertia_:.0f} | silhouette={silhouettes[-1]:.4f}")

# %%
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].plot(list(K_range), inertias, marker="o", color="steelblue")
axes[0].set_title("Método del codo – Inercia")
axes[0].set_xlabel("Número de clusters k")
axes[0].set_ylabel("Inercia (WCSS)")

axes[1].plot(list(K_range), silhouettes, marker="o", color="tomato")
axes[1].set_title("Coeficiente de Silhouette")
axes[1].set_xlabel("Número de clusters k")
axes[1].set_ylabel("Silhouette score")

plt.suptitle("Selección del número óptimo de clusters", fontsize=12)
plt.tight_layout()
plt.savefig("../outputs/03_kmeans_seleccion_k.png", bbox_inches="tight")
plt.show()

# Seleccionar k óptimo
k_optimo = list(K_range)[np.argmax(silhouettes)]
print(f"\nK óptimo por Silhouette: {k_optimo}")

# %% [markdown]
# ## 4. K-Means con k óptimo y caracterización de clusters

# %%
km_final = KMeans(n_clusters=k_optimo, random_state=RANDOM_STATE, n_init=20)
cluster_labels = km_final.fit_predict(X_prep)
df["cluster"] = cluster_labels

print(f"Distribución de clusters (k={k_optimo}):")
print(df["cluster"].value_counts().sort_index())

# %%
# Caracterización: estadísticos por cluster para variables numéricas clave
vars_desc = [
    "nota_admision", "nota_cualificacion_previa", "edad_al_matricularse",
    "nota_media_1sem", "asignaturas_1sem_aprobadas",
    "becado", "deudor", "matricula_al_dia",
]
perfil_clusters = df.groupby("cluster")[vars_desc].mean().round(3)
print("\nPerfil medio de cada cluster:")
print(perfil_clusters.to_string())
perfil_clusters.to_csv("../outputs/03_perfil_clusters.csv")

# %%
# Heatmap del perfil de clusters (valores estandarizados)
scaler_viz = StandardScaler()
perfil_scaled = pd.DataFrame(
    scaler_viz.fit_transform(perfil_clusters),
    index=perfil_clusters.index,
    columns=perfil_clusters.columns
)

fig, ax = plt.subplots(figsize=(10, 4))
sns.heatmap(perfil_scaled, annot=True, fmt=".2f", cmap="RdYlGn",
            center=0, linewidths=0.5, ax=ax)
ax.set_title(f"Perfil estandarizado de clusters (k={k_optimo})")
ax.set_xlabel("Variable")
ax.set_ylabel("Cluster")
plt.tight_layout()
plt.savefig("../outputs/03_heatmap_clusters.png", bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 5. Visualización en 2D (espacio PCA)

# %%
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Coloreado por cluster
scatter = axes[0].scatter(X_2d[:, 0], X_2d[:, 1], c=cluster_labels,
                           cmap="Set2", alpha=0.5, s=8)
axes[0].set_title(f"K-Means (k={k_optimo}) – espacio PCA")
axes[0].set_xlabel(f"PC1 ({pca2.explained_variance_ratio_[0]:.1%})")
axes[0].set_ylabel(f"PC2 ({pca2.explained_variance_ratio_[1]:.1%})")
plt.colorbar(scatter, ax=axes[0], label="Cluster")

# Coloreado por objetivo real
le = LabelEncoder()
objetivo_enc = le.fit_transform(objetivo)
scatter2 = axes[1].scatter(X_2d[:, 0], X_2d[:, 1], c=objetivo_enc,
                            cmap="tab10", alpha=0.5, s=8)
handles = [plt.Line2D([0], [0], marker="o", color="w",
                       markerfacecolor=plt.cm.tab10(i / 3), markersize=8,
                       label=cls)
           for i, cls in enumerate(le.classes_)]
axes[1].legend(handles=handles, title="Situación")
axes[1].set_title("Situación académica real – espacio PCA")
axes[1].set_xlabel(f"PC1 ({pca2.explained_variance_ratio_[0]:.1%})")
axes[1].set_ylabel(f"PC2 ({pca2.explained_variance_ratio_[1]:.1%})")

plt.tight_layout()
plt.savefig("../outputs/03_pca_clusters_vs_objetivo.png", bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 6. Relación clusters vs situación académica

# %%
cross = pd.crosstab(df["cluster"], df["objetivo"], normalize="index").round(3) * 100
print("Distribución de situación académica por cluster (%):")
print(cross.to_string())
cross.to_csv("../outputs/03_clusters_vs_objetivo.csv")

# %%
fig, ax = plt.subplots(figsize=(8, 5))
cross.plot(kind="bar", ax=ax, edgecolor="white", width=0.7, colormap="Set2")
ax.set_title("Distribución de situación académica por cluster")
ax.set_ylabel("Porcentaje (%)")
ax.set_xlabel("Cluster")
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
ax.legend(title="Situación")
plt.tight_layout()
plt.savefig("../outputs/03_clusters_objetivo_barras.png", bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 7. Estabilidad de los clusters

# %%
# Comparamos K-Means con inicializaciones distintas usando ARI
# y con clustering jerárquico (AgglomerativeClustering)

print("Evaluación de estabilidad – ARI entre métodos:")

# K-Means con distintas semillas
labels_km1 = KMeans(n_clusters=k_optimo, random_state=0, n_init=10).fit_predict(X_prep)
labels_km2 = KMeans(n_clusters=k_optimo, random_state=99, n_init=10).fit_predict(X_prep)
labels_km3 = KMeans(n_clusters=k_optimo, random_state=42, n_init=10).fit_predict(X_prep)

ari_12 = adjusted_rand_score(labels_km1, labels_km2)
ari_13 = adjusted_rand_score(labels_km1, labels_km3)
ari_23 = adjusted_rand_score(labels_km2, labels_km3)
print(f"  ARI entre semilla 0 y 99: {ari_12:.4f}")
print(f"  ARI entre semilla 0 y 42: {ari_13:.4f}")
print(f"  ARI entre semilla 99 y 42: {ari_23:.4f}")

# Comparación con clustering jerárquico
labels_hc = AgglomerativeClustering(n_clusters=k_optimo).fit_predict(X_prep)
ari_km_hc = adjusted_rand_score(cluster_labels, labels_hc)
print(f"  ARI K-Means vs Jerárquico: {ari_km_hc:.4f}")

print("""
Interpretación: ARI > 0.8 indica alta estabilidad. Si ARI K-Means vs Jerárquico
es moderado (~0.5–0.7), los clusters capturan estructura real pero no perfectamente
recuperable por todos los métodos.
""")

# %% [markdown]
# ## 8. Descripción narrativa de los perfiles de clusters

# %%
print("""
INTERPRETACIÓN DE LOS CLUSTERS (a completar tras ver los resultados numéricos)
================================================================================
Ejemplo orientativo para k=3:

Cluster 0 – "Estudiante en riesgo":
  · Nota de acceso baja, baja tasa de aprobados en 1er semestre.
  · Alta presencia de deudores y baja tasa de matrícula al día.
  · Predominantemente clasificados como Abandono.

Cluster 1 – "Estudiante medio-alto":
  · Notas de acceso y calificación previa medias-altas.
  · Buen rendimiento en 1er semestre. Becados con frecuencia.
  · Alta proporción de Graduados.

Cluster 2 – "Estudiante en transición":
  · Perfil intermedio; buen acceso pero rendimiento moderado en 1er semestre.
  · Mezcla de Matriculados y Graduados. Representan trayectorias aún abiertas.

Nota: los nombres y descripciones exactos deben ajustarse a los valores numéricos
obtenidos en la sección 4 (perfil_clusters).
""")

# %%
# Guardar etiquetas de cluster para uso en el informe
df[["cluster", "objetivo"]].to_csv("../outputs/03_etiquetas_cluster.csv", index=True)
print("Etiquetas de cluster guardadas.")
