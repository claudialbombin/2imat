# Número a lista de bits (LSB primero)
bits = [(numero >> bit) & 1 for bit in range(8)]  # 8 bits

# Mostrar en LEDs (lista leds tiene 8 elementos)
for i, led in enumerate(leds):
    if bits[i]:
        led.on()
    else:
        led.off()

# Para 4 bits específicos
bits = [(numero >> bit) & 1 for bit in range(4)]
for i, led in enumerate(leds_referencia):  # GPIO20-23
    if bits[i]:
        led.on()
    else:
        led.off()

# Invertir orden (si GPIO20 es MSB)
bits = [(numero >> bit) & 1 for bit in range(4)]
bits.reverse()  # Ahora bits[0] es MSB

# Toggle de un bit específico
numero ^= (1 << 2)  # Toggle del bit 2