import numpy as np
import matplotlib.pyplot as plt

# ========== DATOS ==========
v = 1800.0  # m/s, velocidad horizontal Scud
error_tiempo = 0.214667  # segundos (error tras 100h)
t_deteccion = 3.0  # s
t_intercepcion_planeada = 5.0  # s desde lanzamiento

# Tiempo medido por Patriot (con error)
t_medido = t_intercepcion_planeada - error_tiempo

# Posiciones
x_real = v * t_intercepcion_planeada
x_calc = v * t_medido
error_pos = x_real - x_calc

# ========== TRAYECTORIA ==========
# Tiempos para gráfica
t = np.linspace(0, 6, 400)
x = v * t  # trayectoria real

# Puntos clave
t_points = [0, t_deteccion, t_intercepcion_planeada]
x_points = [0, v * t_deteccion, x_real]

# Puntos según cálculo Patriot
t_calc_points = [0, t_deteccion - error_tiempo, t_medido]
x_calc_points = [0, v * (t_deteccion - error_tiempo), x_calc]

# ========== GRÁFICA ==========
plt.figure(figsize=(12, 6))

# Trayectoria real
plt.plot(t, x, 'b-', linewidth=2, label='Trayectoria real Scud')

# Trayectoria según Patriot (desplazada en tiempo)
plt.plot(t - error_tiempo, x, 'r--', linewidth=2, alpha=0.7, 
         label='Trayectoria según Patriot (con error de tiempo)')

# Puntos reales
plt.scatter(t_points, x_points, color='blue', s=100, zorder=5, 
            label='Eventos reales')
plt.annotate('Lanzamiento (t=0)', (0, 0), xytext=(0.2, 500))
plt.annotate(f'Detección (t={t_deteccion}s)\nx={v*t_deteccion:.0f} m', 
             (t_deteccion, v*t_deteccion), xytext=(t_deteccion+0.1, v*t_deteccion+500))
plt.annotate(f'Intercepción real (t={t_intercepcion_planeada}s)\nx={x_real:.0f} m', 
             (t_intercepcion_planeada, x_real), xytext=(t_intercepcion_planeada+0.1, x_real+500))

# Puntos calculados por Patriot
plt.scatter(t_calc_points, x_calc_points, color='red', s=100, zorder=5, 
            marker='s', label='Eventos calculados por Patriot')
plt.annotate(f'Detección calculada\nt={t_deteccion-error_tiempo:.3f}s', 
             (t_deteccion-error_tiempo, v*(t_deteccion-error_tiempo)),  # ¡CORREGIDO!
             xytext=(t_deteccion-error_tiempo+0.1, v*(t_deteccion-error_tiempo)-800))
plt.annotate(f'Intercepción calculada\nt={t_medido:.3f}s\nx={x_calc:.0f} m', 
             (t_medido, x_calc), xytext=(t_medido+0.1, x_calc-800))

# Línea vertical de intercepción real
plt.axvline(x=t_intercepcion_planeada, color='green', linestyle=':', alpha=0.5, 
            label='Instante real de intercepción')
plt.axhline(y=x_real, color='green', linestyle=':', alpha=0.5)

# Error visual
plt.fill_between([t_medido, t_intercepcion_planeada], 
                 [x_calc, x_calc], [x_real, x_real], 
                 color='yellow', alpha=0.3, label='Error de posición')

# Configuración
plt.xlabel('Tiempo desde lanzamiento (s)', fontsize=12)
plt.ylabel('Distancia horizontal (m)', fontsize=12)
plt.title('Error de Intercepción Patriot-Scud\nDebido a error de tiempo acumulado tras 100 horas', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend(loc='upper left')
plt.xlim(0, 6)
plt.ylim(0, 11000)

# Añadir texto informativo
info_text = f'''Parámetros:
• Velocidad Scud: {v} m/s
• Error tiempo tras 100h: {error_tiempo*1000:.3f} ms
• Error posición: {error_pos:.1f} m
• Tiempo real intercepción: {t_intercepcion_planeada} s
• Tiempo calculado: {t_medido:.3f} s'''
plt.figtext(0.02, 0.02, info_text, fontsize=10, 
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow"))

plt.tight_layout()
plt.show()

# ========== RESULTADOS NUMÉRICOS ==========
print("="*60)
print("RESULTADOS EJERCICIO 11:")
print("="*60)
print(f"1. Error acumulado tras 100 horas: {error_tiempo} s")
print(f"2. Tiempo real de intercepción: {t_intercepcion_planeada} s desde lanzamiento")
print(f"3. Tiempo medido por Patriot: {t_medido:.6f} s")
print(f"4. Posición real de intercepción: {x_real} m")
print(f"5. Posición calculada por Patriot: {x_calc:.2f} m")
print(f"6. Error en posición de intercepción: {error_pos:.2f} m")
print(f"7. Error relativo en tiempo: {error_tiempo/t_intercepcion_planeada*100:.4f}%")
print("="*60)
