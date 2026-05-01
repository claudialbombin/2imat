from gpiozero import MCP3008

sensor = MCP3008(channel=7)  # CH7 = potenciómetro
# CH0-CH6 para sensores externos

# Formas de leer:
valor_normalizado = sensor.value      # 0.0 a 1.0
voltios = sensor.voltage               # 0 a 3.3V
porcentaje = sensor.value * 100        # 0 a 100%

# Umbral simple
if voltios < 1.0:
    # condición
elif voltios > 2.0:
    # otra condición

    # Convertir voltios a lux (sensor lineal)
lux = (voltios / 3.0) * 1500  # 0V=0lx, 3V=1500lx