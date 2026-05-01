from gpiozero import *
def main():
    # Inicializar hardware
    led = PWMLED(23, frequency = 3)
    # led2 = LED(23)
    led.dutycycle(.25)
    # led2.blink()
    
    try:
        while True:
            main()
            
    except KeyboardInterrupt:
        print("\nPrograma terminado por usuario")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Limpieza siempre se ejecuta
        led.off()
        print("GPIO limpio")

if __name__ == "__main__":
    main()