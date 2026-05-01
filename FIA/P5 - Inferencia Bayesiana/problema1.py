import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Parámetros
mu0 = 1.0      # media prior
tau0 = 0.5     # desviación prior
sigma = 0.6    # desviación de las observaciones
n = 20         # número de observaciones
y_bar = 1.5    # media muestral

# 1. Calcular posterior
# Precisión posterior = 1/tau_n^2
precision_posterior = 1/tau0**2 + n/sigma**2
tau_n_sq = 1 / precision_posterior
tau_n = np.sqrt(tau_n_sq)

# Media posterior
mu_n = (mu0/tau0**2 + n*y_bar/sigma**2) / precision_posterior

print("=== RESULTADOS NUMÉRICOS ===")
print(f"Posterior: μ ~ N({mu_n:.3f}, {tau_n:.3f}^2)")
print(f"Intervalo 95% para μ: [{mu_n-1.96*tau_n:.3f}, {mu_n+1.96*tau_n:.3f}]")

# 2. Distribución predictiva
mu_pred = mu_n
sigma_pred = np.sqrt(sigma**2 + tau_n_sq)
print(f"\nPredictiva: y_new ~ N({mu_pred:.3f}, {sigma_pred:.3f}^2)")
print(f"Intervalo 95% predictivo: [{mu_pred-1.96*sigma_pred:.3f}, {mu_pred+1.96*sigma_pred:.3f}]")

# 3. Visualización
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Rango de valores para graficar
x_mu = np.linspace(0, 2.5, 1000)  # para μ
x_y = np.linspace(-1, 4, 1000)    # para y

# Gráfico 1: Prior y Posterior de μ
axes[0,0].plot(x_mu, norm.pdf(x_mu, mu0, tau0), 'b-', linewidth=2, label=f'Prior: N({mu0}, {tau0:.2f}²)')
axes[0,0].plot(x_mu, norm.pdf(x_mu, mu_n, tau_n), 'r-', linewidth=2, label=f'Posterior: N({mu_n:.3f}, {tau_n:.3f}²)')
axes[0,0].axvline(mu0, color='blue', linestyle='--', alpha=0.5)
axes[0,0].axvline(y_bar, color='green', linestyle='--', alpha=0.5, label=f'Media muestral = {y_bar}')
axes[0,0].axvline(mu_n, color='red', linestyle='--', alpha=0.5)
axes[0,0].fill_between(x_mu, 0, norm.pdf(x_mu, mu_n, tau_n), alpha=0.3, color='red')
axes[0,0].set_xlabel('μ (anomalía media, °C)')
axes[0,0].set_ylabel('Densidad')
axes[0,0].set_title('Prior y Posterior de μ')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# Gráfico 2: Intervalos de credibilidad
# Prior interval
prior_interval = [mu0 - 1.96*tau0, mu0 + 1.96*tau0]
# Posterior interval
post_interval = [mu_n - 1.96*tau_n, mu_n + 1.96*tau_n]

axes[0,1].errorbar(1, mu0, yerr=1.96*tau0, fmt='o', color='blue', 
                   capsize=10, label=f'Prior 95% CI', markersize=8)
axes[0,1].errorbar(2, mu_n, yerr=1.96*tau_n, fmt='o', color='red', 
                   capsize=10, label=f'Posterior 95% CI', markersize=8)
axes[0,1].axhline(y_bar, color='green', linestyle='--', alpha=0.5, label=f'Media muestral')
axes[0,1].set_xlim(0.5, 2.5)
axes[0,1].set_ylim(0, 2.2)
axes[0,1].set_xticks([1, 2])
axes[0,1].set_xticklabels(['Prior', 'Posterior'])
axes[0,1].set_ylabel('μ (anomalía media, °C)')
axes[0,1].set_title('Intervalos de credibilidad del 95% para μ')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# Gráfico 3: Distribución predictiva
axes[1,0].plot(x_y, norm.pdf(x_y, mu_pred, sigma_pred), 'purple', 
               linewidth=2, label=f'Predictiva: N({mu_pred:.3f}, {sigma_pred:.3f}²)')
axes[1,0].axvline(mu_pred, color='purple', linestyle='--', alpha=0.5)
axes[1,0].fill_between(x_y, 0, norm.pdf(x_y, mu_pred, sigma_pred), alpha=0.3, color='purple')
axes[1,0].set_xlabel('y_new (nueva observación, °C)')
axes[1,0].set_ylabel('Densidad')
axes[1,0].set_title('Distribución predictiva para y_new')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# Gráfico 4: Efecto del tamaño muestral n
n_values = [0, 5, 10, 20, 50, 100]
mu_n_values = []
tau_n_values = []

for n_val in n_values:
    if n_val == 0:
        mu_n_values.append(mu0)
        tau_n_values.append(tau0)
    else:
        prec = 1/tau0**2 + n_val/sigma**2
        tau_n_val = np.sqrt(1/prec)
        mu_n_val = (mu0/tau0**2 + n_val*y_bar/sigma**2) / prec
        mu_n_values.append(mu_n_val)
        tau_n_values.append(tau_n_val)

axes[1,1].plot(n_values, mu_n_values, 'bo-', linewidth=2, markersize=8, label='Media posterior μ_n')
axes[1,1].fill_between(n_values, 
                       [m - 1.96*t for m, t in zip(mu_n_values, tau_n_values)],
                       [m + 1.96*t for m, t in zip(mu_n_values, tau_n_values)],
                       alpha=0.3, color='blue', label='Intervalo 95%')
axes[1,1].axhline(y_bar, color='green', linestyle='--', label=f'Media muestral = {y_bar}')
axes[1,1].axhline(mu0, color='red', linestyle='--', label=f'Media prior = {mu0}')
axes[1,1].set_xlabel('Tamaño muestral n')
axes[1,1].set_ylabel('μ_n (media posterior)')
axes[1,1].set_title('Efecto del tamaño muestral en la posterior')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Tabla resumen
print("\n=== RESUMEN COMPARATIVO ===")
print(f"{'':<25} {'Media':<10} {'Desv. Est.':<12} {'95% CI'}")
print("-" * 60)
print(f"{'Prior μ':<25} {mu0:<10.3f} {tau0:<12.3f} [{mu0-1.96*tau0:.3f}, {mu0+1.96*tau0:.3f}]")
print(f"{'Posterior μ|datos':<25} {mu_n:<10.3f} {tau_n:<12.3f} [{mu_n-1.96*tau_n:.3f}, {mu_n+1.96*tau_n:.3f}]")
print(f"{'Predictiva y_new|datos':<25} {mu_pred:<10.3f} {sigma_pred:<12.3f} [{mu_pred-1.96*sigma_pred:.3f}, {mu_pred+1.96*sigma_pred:.3f}]")

# Comparación de intervalos
print("\n=== REDUCCIÓN DE INCERTIDUMBRE ===")
print(f"Ancho intervalo prior: {2*1.96*tau0:.3f} °C")
print(f"Ancho intervalo posterior: {2*1.96*tau_n:.3f} °C")
print(f"Reducción: {(1 - (2*1.96*tau_n)/(2*1.96*tau0))*100:.1f}%")
