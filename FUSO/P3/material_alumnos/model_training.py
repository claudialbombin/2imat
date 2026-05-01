import numpy as np
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
from matplotlib import pyplot as plt

# import generate_dataset from the file provided
### ### TU CODIGO AQUI (1 LINEA)


# Create the model
model = linear_model.LinearRegression()

print("Creating dataset")
# generate a dataset with 200 samples
###############
beta = 4
### ### TU CODIGO AQUI (1 LINEA)

# Split the dataset into trainset (80%) and testset (20%)
### ### TU CODIGO AQUI (4 LINEAs)

# Train the model
model.fit(x_train, y_train)

# We can check the predicted coefficient of our regression
# (should be close to the beta parameter of the generate_dataset function)

print(f"Fitted coefficient: {model.coef_}")

# Find now the prediction over the testset and plot
# this prediction compared to the real one
### TU CODIGO AQUI (1 LINEA)

fig = plt.figure(figsize=(10, 8))
plt.scatter(x, y, s=1, color="blue", label="real points")

# real function
x_real = np.arange(0, 200)
y_real = x_real * beta
plt.plot(x_real, y_real, color="red", label="real function")
# plot the predicted regression
### TU CODIGO AQUI (1 Linea)
plt.legend()

plt.savefig("results.png")
print("Fitting completed")
