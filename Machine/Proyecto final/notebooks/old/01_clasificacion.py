# %% [markdown]
# # Notebook 01 – Tarea 1: Clasificación
#
# **Objetivo:** Predecir la situación académica del estudiante:
# `Abandono` / `Matriculado` / `Graduado`.
#
# **Contenido:**
# 1. Preprocesado (encoding, escalado, SMOTE para desbalanceo)
# 2. Modelos: Regresión Logística, Random Forest, XGBoost
# 3. Evaluación multiclase: accuracy, F1-macro, matriz de confusión
# 4. Comparativa de modelos y selección del mejor
# 5. Análisis de importancia de variables (SHAP)
# 6. Análisis del desbalanceo de clases

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

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix,
    ConfusionMatrixDisplay, f1_score, accuracy_score
)
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

import shap

from utils import (
    load_data, set_plot_style, encode_binary_cols,
    get_feature_types, plot_confusion_matrix, plot_feature_importance,
    RANDOM_STATE, TARGET_CLF
)

os.makedirs("../outputs", exist_ok=True)
set_plot_style()

# %% [markdown]
# ## 1. Carga y preprocesado

# %%
df = load_data("../rendimiento_estudiantes.csv")
df = encode_binary_cols(df)

# Separar features y target
y_raw = df[TARGET_CLF]
X = df.drop(columns=[TARGET_CLF])

# Codificar target
le = LabelEncoder()
y = le.fit_transform(y_raw)
print("Clases:", le.classes_)  # abandono=0, graduado=1, matriculado=2

# %%
# Identificar columnas numéricas y categóricas restantes
cat_cols = X.select_dtypes(include="object").columns.tolist()
num_cols = X.select_dtypes(exclude="object").columns.tolist()

print(f"Variables numéricas ({len(num_cols)}): {num_cols}")
print(f"\nVariables categóricas ({len(cat_cols)}): {cat_cols}")

# %%
# Train / test split estratificado (80/20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)
print(f"Train: {X_train.shape[0]} muestras | Test: {X_test.shape[0]} muestras")

# %%
# Preprocesador (OneHotEncoder para categóricas, StandardScaler para numéricas)
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
    ],
    remainder="drop"
)

# %% [markdown]
# ## 2. Definición de modelos

# %%
# ── Modelo 1: Regresión Logística ─────────────────────────────────────────────
pipe_lr = Pipeline([
    ("prep", preprocessor),
    ("clf", LogisticRegression(
        max_iter=1000, class_weight="balanced",
        random_state=RANDOM_STATE, C=1.0
    )),
])

# ── Modelo 2: Random Forest ───────────────────────────────────────────────────
pipe_rf = Pipeline([
    ("prep", preprocessor),
    ("clf", RandomForestClassifier(
        n_estimators=300, class_weight="balanced",
        random_state=RANDOM_STATE, n_jobs=-1
    )),
])

# ── Modelo 3: XGBoost ─────────────────────────────────────────────────────────
# XGBoost maneja el desbalanceo con scale_pos_weight internamente; para multiclase
# usamos class_weight emulado mediante sample_weight en el fit, o simplemente dejamos
# que el modelo lo maneje con su regularización.
pipe_xgb = Pipeline([
    ("prep", preprocessor),
    ("clf", XGBClassifier(
        n_estimators=300, max_depth=5, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8,
        use_label_encoder=False, eval_metric="mlogloss",
        random_state=RANDOM_STATE, n_jobs=-1, verbosity=0
    )),
])

# ── Modelo 4: Random Forest + SMOTE (pipeline imbalanced-learn) ───────────────
pipe_rf_smote = ImbPipeline([
    ("prep", preprocessor),
    ("smote", SMOTE(random_state=RANDOM_STATE)),
    ("clf", RandomForestClassifier(
        n_estimators=300, random_state=RANDOM_STATE, n_jobs=-1
    )),
])

modelos = {
    "Logistic Regression": pipe_lr,
    "Random Forest": pipe_rf,
    "XGBoost": pipe_xgb,
    "RF + SMOTE": pipe_rf_smote,
}

# %% [markdown]
# ## 3. Evaluación con validación cruzada (5-fold estratificado)

# %%
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

resultados_cv = {}
for nombre, modelo in modelos.items():
    print(f"Evaluando {nombre}...", end=" ")
    scores = cross_validate(
        modelo, X_train, y_train, cv=cv,
        scoring=["accuracy", "f1_macro", "f1_weighted"],
        n_jobs=-1
    )
    resultados_cv[nombre] = {
        "Accuracy (CV)": scores["test_accuracy"].mean(),
        "F1-macro (CV)": scores["test_f1_macro"].mean(),
        "F1-weighted (CV)": scores["test_f1_weighted"].mean(),
        "Accuracy std": scores["test_accuracy"].std(),
        "F1-macro std": scores["test_f1_macro"].std(),
    }
    print(f"F1-macro = {resultados_cv[nombre]['F1-macro (CV)']:.4f} ± {resultados_cv[nombre]['F1-macro std']:.4f}")

df_cv = pd.DataFrame(resultados_cv).T
print("\n", df_cv.round(4).to_string())

# %%
# Guardar resultados CV
df_cv.to_csv("../outputs/01_resultados_cv.csv")

# Gráfico comparativo CV
fig, ax = plt.subplots(figsize=(8, 4))
df_cv[["Accuracy (CV)", "F1-macro (CV)", "F1-weighted (CV)"]].plot(
    kind="bar", ax=ax, edgecolor="white", width=0.7
)
ax.set_title("Comparativa de modelos – Validación cruzada (5-fold)")
ax.set_ylabel("Métrica")
ax.set_xticklabels(df_cv.index, rotation=20, ha="right")
ax.legend(loc="lower right")
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig("../outputs/01_comparativa_cv.png", bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 4. Evaluación en conjunto de test

# %%
resultados_test = {}
for nombre, modelo in modelos.items():
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)
    resultados_test[nombre] = {
        "Accuracy": accuracy_score(y_test, y_pred),
        "F1-macro": f1_score(y_test, y_pred, average="macro"),
        "F1-weighted": f1_score(y_test, y_pred, average="weighted"),
    }

df_test = pd.DataFrame(resultados_test).T
print("Resultados en TEST:")
print(df_test.round(4).to_string())
df_test.to_csv("../outputs/01_resultados_test.csv")

# %% [markdown]
# ## 5. Análisis detallado del mejor modelo

# %%
# Seleccionar el modelo con mayor F1-macro en CV
mejor_nombre = df_cv["F1-macro (CV)"].idxmax()
mejor_modelo = modelos[mejor_nombre]
print(f"\nMejor modelo: {mejor_nombre}")

y_pred_best = mejor_modelo.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred_best, target_names=le.classes_))

# %%
# Matriz de confusión del mejor modelo
cm = confusion_matrix(y_test, y_pred_best)
fig, ax = plt.subplots(figsize=(6, 5))
plot_confusion_matrix(cm, labels=le.classes_,
                      title=f"Matriz de confusión – {mejor_nombre}", ax=ax)
plt.tight_layout()
plt.savefig("../outputs/01_confusion_matrix_mejor.png", bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 6. Análisis del desbalanceo de clases

# %%
# Comparar RF estándar vs RF+SMOTE
nombres_comp = ["Random Forest", "RF + SMOTE"]
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for i, nombre in enumerate(nombres_comp):
    modelo = modelos[nombre]
    y_pred = modelo.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    plot_confusion_matrix(cm, labels=le.classes_, title=nombre, ax=axes[i])
plt.suptitle("Efecto del balanceo de clases (SMOTE vs class_weight)", fontsize=12)
plt.tight_layout()
plt.savefig("../outputs/01_desbalanceo_comparativa.png", bbox_inches="tight")
plt.show()

# Tabla de métricas por clase
print("\nRandom Forest – reporte completo:")
print(classification_report(
    y_test, modelos["Random Forest"].predict(X_test), target_names=le.classes_
))
print("\nRF + SMOTE – reporte completo:")
print(classification_report(
    y_test, modelos["RF + SMOTE"].predict(X_test), target_names=le.classes_
))

# %% [markdown]
# ## 7. Importancia de variables (Random Forest)

# %%
# Extraer importancias del RF (entrenado sobre todo el training set)
rf = modelos["Random Forest"]
rf_clf = rf.named_steps["clf"]
ohe = rf.named_steps["prep"].named_transformers_["cat"]
cat_names = ohe.get_feature_names_out(cat_cols).tolist()
feature_names = num_cols + cat_names

importances = pd.Series(rf_clf.feature_importances_, index=feature_names).sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 8))
plot_feature_importance(importances, top_n=20,
                        title="Top-20 variables – Random Forest (clasificación)", ax=ax)
plt.tight_layout()
plt.savefig("../outputs/01_feature_importance_rf.png", bbox_inches="tight")
plt.show()

importances.to_csv("../outputs/01_feature_importances.csv", header=["importance"])

# %% [markdown]
# ## 8. SHAP values (XGBoost)

# %%
# SHAP sobre XGBoost para interpretabilidad global y local
xgb_pipe = modelos["XGBoost"]
X_test_prep = xgb_pipe.named_steps["prep"].transform(X_test)
feature_names_xgb = num_cols + xgb_pipe.named_steps["prep"].named_transformers_["cat"].get_feature_names_out(cat_cols).tolist()

explainer = shap.TreeExplainer(xgb_pipe.named_steps["clf"])
shap_values = explainer.shap_values(X_test_prep)

# SHAP summary para cada clase
for i, clase in enumerate(le.classes_):
    fig, ax = plt.subplots(figsize=(9, 6))
    shap.summary_plot(
        shap_values[i], X_test_prep,
        feature_names=feature_names_xgb,
        show=False, max_display=15, plot_type="bar"
    )
    plt.title(f"SHAP – Importancia global para clase: {clase}")
    plt.tight_layout()
    plt.savefig(f"../outputs/01_shap_{clase}.png", bbox_inches="tight")
    plt.close()
    print(f"SHAP guardado para clase: {clase}")

# SHAP beeswarm para la clase Abandono
shap.summary_plot(
    shap_values[0], X_test_prep,
    feature_names=feature_names_xgb,
    show=False, max_display=15
)
plt.title("SHAP beeswarm – clase Abandono")
plt.tight_layout()
plt.savefig("../outputs/01_shap_beeswarm_abandono.png", bbox_inches="tight")
plt.show()

# %% [markdown]
# ## 9. Predicciones finales (para entrega)

# %%
# Guardar predicciones del mejor modelo sobre el test set
pred_df = pd.DataFrame({
    "indice_test": X_test.index,
    "prediccion": le.inverse_transform(y_pred_best),
    "real": le.inverse_transform(y_test),
})
pred_df.to_csv("../outputs/01_predicciones_clasificacion.csv", index=False)
print("Predicciones guardadas en outputs/01_predicciones_clasificacion.csv")

# %% [markdown]
# ## 10. Conclusiones de la tarea de clasificación
#
# - El **XGBoost** y el **Random Forest** son los modelos con mejor F1-macro.
# - La clase `Matriculado` es la más difícil de predecir (menor recall) debido a que
#   sus características son intermedias entre Abandono y Graduado.
# - Las variables más importantes son las del **rendimiento del primer semestre**
#   (`nota_media_1sem`, `asignaturas_1sem_aprobadas`) y las **notas de acceso**.
# - Variables socioeconómicas como `matricula_al_dia` y `deudor` también tienen peso
#   significativo, especialmente para predecir el abandono.
# - El uso de `class_weight="balanced"` mejora el recall de las clases minoritarias
#   sin pérdida sustancial de accuracy global.
