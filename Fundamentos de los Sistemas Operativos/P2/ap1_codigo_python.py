from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
import argparse
import numpy as np




if __name__ == "__main__":

    # Argument parser (execute the python script considering the argumentss)
    parser = argparse.ArgumentParser(description='execution of different machine learning models')

    # Add all necessary argumentss
    parser.add_argument('model', type=str, help='Machine learning model')
    parser.add_argument('--neigh', type=str, help='neighbors for KNN model')

    # Parse the arguments
    args = parser.parse_args()

    # Store parameter values
    model = args.model
    neigh = args.neigh

    np.random.seed(1)

    # Import dataset:
    url = "iris_csv.csv"

    # Convert dataset to a pandas dataframe:
    dataset = pd.read_csv(url)

    # Use head() function to return the first 5 rows:

    dataset.head()
    # Assign values to the X and y variables:
    X = dataset.iloc[:, :-1].values
    y = dataset.iloc[:, 4].values

    # Split dataset into random train and test subsets:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

    # Standardize features by removing mean and scaling to unit variance:
    scaler = StandardScaler()
    scaler.fit(X_train)

    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)

    # Use the KNN classifier to fit data:
    if model == "KNeighborsClassifier":
        classifier = KNeighborsClassifier(n_neighbors=int(neigh))
    elif model == "GaussianNB":
        classifier = GaussianNB()
    elif model == "RandomForestClassifier":
        classifier = RandomForestClassifier()
    else:
        print("This model does not exist")
        exit(0)

    classifier.fit(X_train, y_train)

    # Predict y data with classifier:
    y_predict = classifier.predict(X_test)

    accuracy = accuracy_score(y_test, y_predict)

    print('------------------------------------')
    print(model)
    if neigh is not None:
        print(f'Neighs {neigh}')
    print("Accuracy:", accuracy)
    print('------------------------------------')
