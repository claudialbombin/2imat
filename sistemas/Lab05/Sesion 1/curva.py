from gpiozero import MCP3008
sensor = MCP3008(channel =0)
voltios = sensor.voltage
porcentaje = sensor.value * 100

print(f"Voltios: {voltios:.2f} V")
print(f"Porcentaje: {porcentaje:.2f} %")