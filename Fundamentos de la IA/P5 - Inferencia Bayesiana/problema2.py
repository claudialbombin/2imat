import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# Parámetros
alpha0, beta0 = 30, 70  # prior
n, k = 10, 6            # datos
alpha_post, beta_post = 36, 74  # posterior

# 1. Distribuciones Beta
theta = np.linspace(0, 1, 1000)
prior_pdf = stats.beta.pdf(theta, alpha0, beta0)
post_pdf = stats.beta.pdf(theta, alpha_post, beta_post)

# 2. Simulaciones predictivas
np.random.seed(42)
n_sim = 10000
# Generar θ de la posterior
theta_sim = np.random.beta(alpha_post, beta_post, n_sim)
# Generar x_new para cada θ
x_new_sim = np.random.binomial(1, theta_sim)

# 3. Crear figura
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Gráfico 1: Prior y Posterior
ax1 = axes[0]
ax1.plot(theta, prior_pdf, 'b-', linewidth=2, label=f'Prior: Beta({alpha0},{beta0})')
ax1.plot(theta, post_pdf, 'r-', linewidth=2, label=f'Posterior: Beta({alpha_post},{beta_post})')

# Marcas importantes
mean_prior = alpha0/(alpha0+beta0)
mean_post = alpha_post/(alpha_post+beta_post)
sample_prop = k/n

ax1.axvline(mean_prior, color='blue', linestyle='--', alpha=0.5, label=f'Media prior: {mean_prior:.3f}')
ax1.axvline(sample_prop, color='green', linestyle='--', alpha=0.5, label=f'Proporción muestral: {sample_prop:.3f}')
ax1.axvline(mean_post, color='red', linestyle='--', alpha=0.5, label=f'Media posterior: {mean_post:.3f}')
ax1.axvline(0.4, color='black', linestyle=':', alpha=0.7, label='Umbral 40%')

# Rellenar P(θ > 0.4)
idx = theta > 0.4
ax1.fill_between(theta[idx], 0, post_pdf[idx], alpha=0.3, color='red', 
                  label=f'P(θ>0.4|datos) = {1-stats.beta.cdf(0.4, alpha_post, beta_post):.3f}')

ax1.set_xlabel('θ (proporción de hogares con gasto >40%)')
ax1.set_ylabel('Densidad')
ax1.set_title('Evolución de la creencia: Prior → Posterior')
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)

# Gráfico 2: Distribución predictiva (histograma)
ax2 = axes[1]
counts, bins, patches = ax2.hist(x_new_sim, bins=[-0.5, 0.5, 1.5], 
                                  density=True, alpha=0.7, color='purple',
                                  edgecolor='black', linewidth=1.5)

# Anotar probabilidades
p1 = np.mean(x_new_sim)  # ≈ alpha_post/(alpha_post+beta_post)
p0 = 1 - p1

ax2.text(0.05, 0.95, f'P(x_new=1) = {p1:.3f}\nP(x_new=0) = {p0:.3f}',
         transform=ax2.transAxes, fontsize=12,
         verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

ax2.set_xticks([0, 1])
ax2.set_xticklabels(['x_new=0\n(≤40% salario)', 'x_new=1\n(>40% salario)'])
ax2.set_ylabel('Probabilidad')
ax2.set_title(f'Distribución predictiva (n={n_sim} simulaciones)')
ax2.grid(True, alpha=0.3)

# Gráfico 3: Densidades juntas + histograma predictivo
ax3 = axes[2]

# Densidades
ax3.plot(theta, prior_pdf, 'b-', alpha=0.7, label='Prior')
ax3.plot(theta, post_pdf, 'r-', alpha=0.7, label='Posterior')

# Histograma de θ simulados (normalizado para comparar)
ax3.hist(theta_sim, bins=50, density=True, alpha=0.5, 
         color='orange', edgecolor='darkorange',
         label='Simulaciones de θ (posterior)')

ax3.axvline(mean_prior, color='blue', linestyle=':', alpha=0.7)
ax3.axvline(mean_post, color='red', linestyle=':', alpha=0.7)
ax3.axvline(sample_prop, color='green', linestyle=':', alpha=0.7, label='Datos (6/10)')

ax3.set_xlabel('θ')
ax3.set_ylabel('Densidad')
ax3.set_title('Comparación: Densidades analíticas vs Simulaciones')
ax3.legend(loc='upper left')
ax3.grid(True, alpha=0.3)

plt.suptitle('Estudio de alquileres en Madrid - Análisis Bayesiano', fontsize=14, y=1.02)
plt.tight_layout()
plt.show()

# Estadísticas adicionales
print("="*60)
print("ESTADÍSTICAS DEL ANÁLISIS")
print("="*60)
print(f"\nPRIOR:")
print(f"  θ ~ Beta({alpha0},{beta0})")
print(f"  Media: {mean_prior:.4f} ({mean_prior*100:.1f}%)")
print(f"  Desviación estándar: {np.sqrt((alpha0*beta0)/((alpha0+beta0)**2*(alpha0+beta0+1))):.4f}")

print(f"\nDATOS:")
print(f"  Muestra: n={n} hogares")
print(f"  k={k} gastan >40% ({k/n*100:.1f}%)")

print(f"\nPOSTERIOR:")
print(f"  θ|datos ~ Beta({alpha_post},{beta_post})")
print(f"  Media: {mean_post:.4f} ({mean_post*100:.1f}%)")
print(f"  Desviación estándar: {np.sqrt((alpha_post*beta_post)/((alpha_post+beta_post)**2*(alpha_post+beta_post+1))):.4f}")
print(f"  P(θ > 0.4|datos) = {1-stats.beta.cdf(0.4, alpha_post, beta_post):.4f}")

print(f"\nPREDICCIÓN:")
print(f"  P(nuevo hogar gaste >40%) = {p1:.4f} ({p1*100:.1f}%)")
print(f"  Cambio respecto al prior: {(p1-mean_prior)*100:+.1f} puntos porcentuales")
