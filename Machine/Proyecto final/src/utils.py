"""
src/utils.py
Funciones auxiliares compartidas por todos los notebooks del proyecto.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder

# ── Configuración global ──────────────────────────────────────────────────────
RANDOM_STATE = 42
DATA_PATH = "../rendimiento_estudiantes.csv"   # ajusta si es necesario
OUTPUT_DIR = "../outputs"

# Columnas del segundo semestre que NO deben usarse como predictores en la
# tarea de regresión (data leakage respecto a nota_media_2sem).
LEAKAGE_COLS_REGRESION = [
    "asignaturas_2sem_matriculadas",
    "asignaturas_2sem_evaluadas",
    "asignaturas_2sem_aprobadas",
    "asignaturas_2sem_sin_evaluacion",
    "asignaturas_2sem_convalidadas",
    # La variable objetivo misma
    "nota_media_2sem",
]

# Variable objetivo clasificación
TARGET_CLF = "objetivo"

# Variable objetivo regresión
TARGET_REG = "nota_media_2sem"


# ── Carga y preprocesado básico ───────────────────────────────────────────────

def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    """Carga el dataset y devuelve un DataFrame limpio."""
    df = pd.read_csv(path, sep=";")
    return df


def get_feature_types(df: pd.DataFrame, target_cols: list = None) -> dict:
    """
    Devuelve un diccionario con listas de columnas categóricas y numéricas,
    excluyendo las columnas objetivo indicadas.
    """
    if target_cols is None:
        target_cols = []
    cols = [c for c in df.columns if c not in target_cols]
    cat_cols = [c for c in cols if df[c].dtype == "object"]
    num_cols = [c for c in cols if df[c].dtype != "object"]
    return {"categorical": cat_cols, "numerical": num_cols}


def encode_binary_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte columnas binarias si/no → 1/0.
    Actúa in-place sobre una copia.
    """
    df = df.copy()
    binary_map = {"si": 1, "no": 0}
    binary_cols = [
        "desplazado", "necesidades_educativas_especiales",
        "deudor", "matricula_al_dia", "becado", "internacional",
    ]
    for col in binary_cols:
        if col in df.columns:
            df[col] = df[col].map(binary_map)
    # Género
    if "genero" in df.columns:
        df["genero"] = df["genero"].map({"hombre": 1, "mujer": 0})
    # Asistencia
    if "asistencia_diurna_vespertina" in df.columns:
        df["asistencia_diurna_vespertina"] = df["asistencia_diurna_vespertina"].map(
            {"diurna": 1, "vespertina": 0}
        )
    return df


# ── Visualización ─────────────────────────────────────────────────────────────

def set_plot_style():
    sns.set_theme(style="whitegrid", palette="Set2", font_scale=1.1)
    plt.rcParams["figure.dpi"] = 120


def plot_class_distribution(df: pd.DataFrame, col: str = TARGET_CLF, ax=None):
    """Gráfico de barras con distribución de la variable objetivo."""
    counts = df[col].value_counts()
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x=counts.index, y=counts.values, ax=ax, palette="Set2")
    ax.set_title(f"Distribución de '{col}'")
    ax.set_ylabel("Frecuencia")
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height())}",
                    (p.get_x() + p.get_width() / 2, p.get_height()),
                    ha="center", va="bottom", fontsize=10)
    return ax


def plot_confusion_matrix(cm, labels, title="Matriz de confusión", ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels, yticklabels=labels, ax=ax)
    ax.set_xlabel("Predicho")
    ax.set_ylabel("Real")
    ax.set_title(title)
    return ax


def plot_feature_importance(importances: pd.Series, top_n: int = 20,
                             title: str = "Importancia de variables", ax=None):
    top = importances.nlargest(top_n)
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, top_n * 0.35 + 1))
    top[::-1].plot(kind="barh", ax=ax, color="steelblue")
    ax.set_title(title)
    ax.set_xlabel("Importancia")
    return ax


# ── Métricas ──────────────────────────────────────────────────────────────────

def regression_metrics(y_true, y_pred) -> dict:
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return {"RMSE": rmse, "MAE": mae, "R2": r2}


def print_metrics(metrics: dict, model_name: str = "Modelo"):
    print(f"\n{'='*40}")
    print(f"  {model_name}")
    print(f"{'='*40}")
    for k, v in metrics.items():
        print(f"  {k:>10}: {v:.4f}")
