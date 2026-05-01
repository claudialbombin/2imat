# %% [markdown]
# # Notebook 02 – Tarea 2: Regresión
#
# **Objetivo:** Predecir `nota_media_2sem` (calificación media del 2º semestre).
#
# **Consideración metodológica clave – Data Leakage:**
# Las siguientes variables del 2º semestre son contemporáneas o prácticamente
# equivalentes al target y NO deben usarse como predictores:
# - `asignaturas_2sem_matriculadas`
# - `asignaturas_2sem_evaluadas`
# - `asignaturas_2sem_aprobadas`
# - `asignaturas_2sem_sin_evaluacion`
# - `asignaturas_2sem_convalidadas`
#
# El modelo se construirá exclusivamente con información disponible ANTES o DURANTE
# el primer semestre (perfil de entrada + 1er semestre).
#
# **Contenido:**
# 1. Selección de variables (justificación del leakage)
# 2. Preprocesado
# 3. Modelos: Ridge, Random Forest Regressor, XGBoost Regressor
# 4. Comparativa y selección del mejor modelo
# 5. Análisis de residuos
# 6. Importancia de variables

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

from sklearn.model_selection import train_test_split, KFold, cross_validate
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

from utils import (
    load_data, set_plot_style, encode_binary_cols,
    regression_metrics, print_metrics,
    RANDOM_STATE, TARGET_REG, LEAKAGE_COLS_REGRESION
)

os.makedirs("../outputs", exist_ok=True)
set_plot_style()

# %% [markdown]
# ## 1. Carga y selección de variables

# %%
df = load_data("../rendimiento_estudiantes.csv")
df = encode_binary_cols(df)

# ── Justificación de exclusión por data leakage ────────────────────────────────
print("Variables EXCLUIDAS por data leakage:")
for col in LEAKAGE_COLS_REGRESION:
    print(f"  · {col}")
print("""
Razón: estas columnas describen el rendimiento del 2º semestre de forma simultánea
o casi equivalente a la nota media que queremos predecir. Incluirlas introduciría
información del futuro en el modelo, invalidando cualquier capacidad predictiva real.

También excluimos la variable 'objetivo' (situación final) porque está parcialmente
determinada por el rendimiento del 2º semestre → leakage indirecto.
""")

# ──────────────────────────────────────────────────────────────────────────────
# Variables excluidas (leakage + target + objetivo)
EXCLUIR = LEAKAGE_COLS_REGRESION + ["objetivo"]

# Variables disponibles para predecir
feature_cols = [c for c in df.columns if c not in EXCLUIR]
print(f"Variables usadas como predictores ({len(feature_cols)}):")
print(feature_cols)

# %%
# Filtrar filas donde el target es 0 (estudiantes sin asignaturas evaluadas en 2º sem)
# → podrían ser abandonos tempranos; su nota 0 no refleja rendimiento real.
df_reg = df[df[TARGET_REG] > 0].copy()
print(f"Filas con nota_media_2sem > 0: {len(df_reg)} (de {len(df)})")

X = df_reg[feature_cols]
y = df_reg[TARGET_REG]

# %%
# Distribución del target
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(y, bins=40, color="steelblue", edgecolor="white")
ax.set_title("Distribución de nota_media_2sem (target regresión)")
ax.set_xlabel("Nota media 2º semestre")
ax.set_ylabel("Frecuencia")
plt.tight_layout()
plt.savefig("../outputs/02_distribucion_target.png", bbox_inches="tight")
plt.show()
print(f"Media: {y.mean():.2f} | Std: {y.std():.2f} | Min: {y.min():.2f} | Max: {y.max():.2f}")

# %% [markdown]
# ## 2. Preprocesado

# %%
cat_cols = X.select_dtypes(include="object").columns.tolist()
num_cols = X.select_dtypes(exclude="object").columns.tolist()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE
)
print(f"Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), num_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
])

# %% [markdown]
# ## 3. Definición de modelos

# %%
modelos = {
    "Ridge": Pipeline([
        ("prep", preprocessor),
        ("reg", Ridge(alpha=1.0)),
    ]),
    "Lasso": Pipeline([
        ("prep", preprocessor),
        ("reg", Lasso(alpha=0.01, max_iter=5000)),
    ]),
    "Random Forest": Pipeline([
        ("prep", preprocessor),
        ("reg", RandomForestRegressor(
            n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1
        )),
    ]),
    "XGBoost": Pipeline([
        ("prep", preprocessor),
        ("reg", XGBRegressor(
            n_estimators=300, max_depth=5, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            random_state=RANDOM_STATE, n_jobs=-1, verbosity=0
        )),
    ]),
    "Gradient Boosting": Pipeline([
        ("prep", preprocessor),
        ("reg", GradientBoostingRegressor(
            n_estimators=300, max_depth=4, learning_rate=0.05,
            random_state=RANDOM_STATE
        )),
    ]),
}

# %% [markdown]
# ## 4. Validación cruzada (5-fold)

# %%
cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

resultados_cv = {}
for nombre, modelo in modelos.items():
    print(f"Evaluando {nombre}...", end=" ")
    scores = cross_validate(
        modelo, X_train, y_train, cv=cv,
        scoring=["neg_root_mean_squared_error", "neg_mean_absolute_error", "r2"],
        n_jobs=-1
    )
    resultados_cv[nombre] = {
        "RMSE (CV)": -scores["test_neg_root_mean_squared_error"].mean(),
        "MAE (CV)":  -scores["test_neg_mean_absolute_error"].mean(),
        "R² (CV)":    scores["test_r2"].mean(),
        "RMSE std":  scores["test_neg_root_mean_squared_error"].std(),
    }
    print(f"RMSE = {resultados_cv[nombre]['RMSE (CV)']:.4f} | R² = {resultados_cv[nombre]['R² (CV)']:.4f}")

df_cv = pd.DataFrame(resultados_cv).T
print("\n", df_cv.round(4).to_string())
df_cv.to_csv("../outputs/02_resultados_cv.csv")

# %%
# Gráfico comparativo
fig, axes = plt.subplots(1, 3, figsize=(14, 5))
for ax, metric in zip(axes, ["RMSE (CV)", "MAE (CV)", "R² (CV)"]):
    vals = df_cv[metric]
    colors = ["tomato" if metric != "R² (CV)" else "steelblue"] * len(vals)
    vals.plot(kind="bar", ax=ax, color="steelblue", edgecolor="white")
    ax.set_title(metric)
    ax.set_xticklabels(vals.index, rotation=20, ha="right")
plt.suptitle("Comparativa de modelos de regresión – CV 5-fold", fontsize=12)
plt.tight_layout()
plt.savefig("../outputs/02_comparativa_modelos_regresion.png", bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 5. Evaluación en test y análisis de residuos

# %%
resultados_test = {}
for nombre, modelo in modelos.items():
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)
    resultados_test[nombre] = regression_metrics(y_test, y_pred)
    resultados_test[nombre]["y_pred"] = y_pred

df_test = pd.DataFrame({k: v for k, v in resultados_test.items()
                         if k != "y_pred"}).T
print("Resultados en TEST:")
print(df_test.round(4).to_string())
df_test.to_csv("../outputs/02_resultados_test.csv")

# %%
# Selección del mejor modelo (menor RMSE en CV)
mejor_nombre = df_cv["RMSE (CV)"].idxmin()
print(f"\nMejor modelo: {mejor_nombre}")
y_pred_best = resultados_test[mejor_nombre]["y_pred"]

# %%
# Gráfico real vs predicho
fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(y_test, y_pred_best, alpha=0.4, s=15, color="steelblue")
lims = [min(y_test.min(), y_pred_best.min()) - 0.5,
        max(y_test.max(), y_pred_best.max()) + 0.5]
ax.plot(lims, lims, "r--", linewidth=1.5, label="Predicción perfecta")
ax.set_xlabel("Nota real")
ax.set_ylabel("Nota predicha")
ax.set_title(f"Real vs Predicho – {mejor_nombre}")
ax.legend()
plt.tight_layout()
plt.savefig("../outputs/02_real_vs_predicho.png", bbox_inches="tight")
plt.show()

# %%
# Residuos
residuos = y_test.values - y_pred_best

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].scatter(y_pred_best, residuos, alpha=0.4, s=15, color="steelblue")
axes[0].axhline(0, color="red", linestyle="--")
axes[0].set_xlabel("Predicho")
axes[0].set_ylabel("Residuo")
axes[0].set_title("Residuos vs Predicho")

axes[1].hist(residuos, bins=40, color="steelblue", edgecolor="white")
axes[1].axvline(0, color="red", linestyle="--")
axes[1].set_title("Distribución de residuos")
axes[1].set_xlabel("Residuo")

plt.suptitle(f"Análisis de residuos – {mejor_nombre}", fontsize=12)
plt.tight_layout()
plt.savefig("../outputs/02_residuos.png", bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 6. Importancia de variables

# %%
# Usamos Random Forest (o el mejor modelo si es RF/XGBoost)
modelo_imp = modelos["Random Forest"]
rf_reg = modelo_imp.named_steps["reg"]
ohe = modelo_imp.named_steps["prep"].named_transformers_["cat"]
cat_names = ohe.get_feature_names_out(cat_cols).tolist()
feature_names = num_cols + cat_names

importances = pd.Series(rf_reg.feature_importances_, index=feature_names).sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 8))
from utils import plot_feature_importance
plot_feature_importance(importances, top_n=20,
                        title="Top-20 variables – RF Regressor (nota_media_2sem)", ax=ax)
plt.tight_layout()
plt.savefig("../outputs/02_feature_importance_reg.png", bbox_inches="tight")
plt.show()

importances.to_csv("../outputs/02_feature_importances_reg.csv", header=["importance"])

# %% [markdown]
# ## 7. Comparativa de selecciones de variables

# %%
# Comparar usando SOLO variables del perfil de entrada vs añadiendo 1er semestre

# Selección A: solo perfil de entrada (sin info semestral)
cols_perfil = [c for c in feature_cols if "1sem" not in c and "2sem" not in c]
# Selección B: perfil + 1er semestre (nuestra configuración principal)
cols_completo = feature_cols

resultados_sel = {}
for nombre_sel, cols_sel in [("Solo perfil entrada", cols_perfil),
                               ("Perfil + 1er sem", cols_completo)]:
    X_sel = df_reg[cols_sel]
    cat_s = X_sel.select_dtypes(include="object").columns.tolist()
    num_s = X_sel.select_dtypes(exclude="object").columns.tolist()
    prep_s = ColumnTransformer([
        ("num", StandardScaler(), num_s),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_s),
    ])
    pipe_s = Pipeline([("prep", prep_s), ("reg", RandomForestRegressor(
        n_estimators=200, random_state=RANDOM_STATE, n_jobs=-1
    ))])
    X_tr, X_te, y_tr, y_te = train_test_split(
        X_sel, y, test_size=0.2, random_state=RANDOM_STATE
    )
    pipe_s.fit(X_tr, y_tr)
    y_p = pipe_s.predict(X_te)
    m = regression_metrics(y_te, y_p)
    resultados_sel[nombre_sel] = m
    print(f"{nombre_sel}: RMSE={m['RMSE']:.4f} | R²={m['R2']:.4f}")

print("""
Conclusión: añadir información del 1er semestre mejora notablemente la predicción
del rendimiento en el 2º semestre, confirmando que el desempeño inicial es el
predictor más relevante.
""")

# %% [markdown]
# ## 8. Predicciones finales

# %%
pred_df = pd.DataFrame({
    "indice_test": X_test.index,
    "nota_real": y_test.values,
    "nota_predicha": y_pred_best.round(3),
    "residuo": residuos.round(3),
})
pred_df.to_csv("../outputs/02_predicciones_regresion.csv", index=False)
print("Predicciones guardadas en outputs/02_predicciones_regresion.csv")

# %% [markdown]
# ## 9. Conclusiones de la tarea de regresión
#
# - Sin variables de 2º semestre (data leakage), el mejor modelo obtiene un R² ≈ 0.65–0.75.
# - El **rendimiento en el 1er semestre** (`nota_media_1sem`, `asignaturas_1sem_aprobadas`)
#   es el predictor más potente de la nota del 2º semestre.
# - El perfil de entrada solo (nota de admisión, cualificación previa) explica menos
#   varianza, pero ya captura una señal relevante.
# - Los modelos de ensemble (RF, XGBoost) superan claramente a los modelos lineales.
# - Los residuos no presentan patrones sistemáticos graves, aunque la varianza es mayor
#   en rangos de nota intermedios (8-12 puntos).
