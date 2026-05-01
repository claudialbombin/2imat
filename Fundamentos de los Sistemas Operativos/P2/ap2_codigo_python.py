import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score



if __name__ == "__main__":
    # Leer argumentos
    if len(sys.argv) != 3:
        print("Uso: python <fichero_python> <archivo_csv> <porcentaje_training>")
        sys.exit(1)

    file_path = sys.argv[1]
    train_size = float(sys.argv[2]) / 100
    test_size = 1 - train_size


    # Cargar el conjunto de datos
    data = pd.read_csv(file_path)

    # Separamos las features (matriz X) de la clase (vector y)
    X = data.drop('class', axis=1)
    y = data['class']

    # Dividir el conjunto de datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=train_size, test_size=test_size, random_state=42)

    # Entrenamos un modelo de regresion logistica
    clf = LogisticRegression(max_iter=10000, random_state=42)
    clf.fit(X_train, y_train)

    # Predecimos y evaluamos el modelo
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f'Precisión del modelo con {train_size*100:.0f}% entrenamiento y {test_size*100:.0f}% prueba: {accuracy * 100:.2f}%')
