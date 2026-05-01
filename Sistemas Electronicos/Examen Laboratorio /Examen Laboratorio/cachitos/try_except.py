def main():
    # Inicializar hardware
    led = LED(20)
    boton = Button(16)
    
    try:
        while True:
            # Código principal
            pass
            
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