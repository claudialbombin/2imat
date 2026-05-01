from gpiozero import LED, Button
import socket
from signal import pause

# Configurar LEDs (GPIO20 a GPIO27 como bits 0-7)
leds = [LED(pin) for pin in range(20, 28)]

# Configurar botones
botones = {
    'primero': Button(7, pull_up=True),
    'segundo': Button(16, pull_up=True),
    'tercero': Button(17, pull_up=True),
    'cuarto': Button(19, pull_up=True)
}

def obtener_ip():
    """Obtiene la dirección IP de la Raspberry Pi"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.1.100"  # IP por defecto si hay error

def mostrar_octeto(octeto):
    """Muestra un octeto en binario en los LEDs"""
    for i, led in enumerate(leds):
        bit = (octeto >> i) & 0x1
        led.on() if bit else led.off()

# Obtener IP y separar en octetos
ip = obtener_ip()
octetos = [int(x) for x in ip.split('.')]

# Asignar funciones a botones
botones['primero'].when_pressed = lambda: mostrar_octeto(octetos[0])
botones['segundo'].when_pressed = lambda: mostrar_octeto(octetos[1])
botones['tercero'].when_pressed = lambda: mostrar_octeto(octetos[2])
botones['cuarto'].when_pressed = lambda: mostrar_octeto(octetos[3])

print(f"IP: {ip}")
print("Presione botones para mostrar octetos")

pause()