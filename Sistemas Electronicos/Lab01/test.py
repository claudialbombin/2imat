from gpiozero import LEDBoard, MCP3008
from signal import pause

def main() -> None:
    leds = LEDBoard(20, 21, 22, 23, 24, 25, 26, 27)
    leds.on()

    potenciometro = MCP3008(7)
    print(potenciometro.voltage)

    print('Pulse CTRL + C para parar')
    pause()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

# sudo shutdown -h now