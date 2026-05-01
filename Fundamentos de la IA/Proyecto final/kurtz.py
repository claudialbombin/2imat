"""
Programa principal unificado para el proyecto FIA Parte 2
Integra todas las funcionalidades de ambas partes

Este archivo sirve como punto de entrada principal que:
1. Importa todos los módulos del proyecto
2. Muestra un menú unificado con todas las opciones
3. Gestiona la ejecución de cada parte del proyecto
4. Proporciona una interfaz coherente para el usuario
"""

import sys
import time

# Importar módulos de cada parte del proyecto
try:
    from funciones_kurtz import modo_jugador, modo_auto_inteligente
    from palacio_bayesiano import modo_bayesiano
    from river_mdp import modo_rio_mdp
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrate de que todos los archivos .py están en el mismo directorio")
    sys.exit(1)

def mostrar_banner():
    """
    Muestra el banner principal del proyecto
    
    Incluye:
    - Título del proyecto
    - Información sobre las partes implementadas
    - Datos del autor y asignatura
    """
    print("\n" + "▓"*60)
    print("▓              BUSCANDO AL CORONEL KURTZ                 ▓")
    print("▓              Proyecto FIA - Parte 1 & 2               ▓")
    print("▓"*60)
    print()
    print("Implementación completa con:")
    print("  - Parte 1: Agente lógico y explorador (palacio original)")
    print("  - Parte 2: Agente bayesiano (trampas específicas)")
    print("  - Parte 2: MDP del río (Value Iteration)")
    print()
    print("Autor: Claudia Maria Lopez Bombin")
    print("Asignatura: Fundamentos de Inteligencia Artificial 25-26")
    print("Grado en Ingeniería Matemática e Inteligencia Artificial")
    print()

def comparar_resultados():
    """
    Muestra comparativa entre los diferentes enfoques implementados
    
    Analiza:
    - Ventajas y desventajas de cada enfoque
    - Casos de uso recomendados para cada uno
    - Consideraciones prácticas de implementación
    """
    print("\n" + "="*60)
    print("COMPARATIVA DE ENFOQUES")
    print("="*60)
    print()
    
    # Comparativa del agente lógico (Parte 1)
    print("PARTE 1 - Agente Lógico (Palacio Original):")
    print("  • Ventajas:")
    print("    - Rápido y determinista")
    print("    - Fácil de depurar y entender")
    print("    - Bajo costo computacional")
    print("  • Desventajas:")
    print("    - No maneja incertidumbre")
    print("    - Puede quedar atrapado en bucles")
    print("    - Decisiones basadas en reglas fijas")
    print()
    
    # Comparativa del agente bayesiano (Parte 2)
    print("PARTE 2 - Agente Bayesiano (Palacio Mejorado):")
    print("  • Ventajas:")
    print("    - Maneja incertidumbre de forma probabilística")
    print("    - Actualiza creencias con nueva información")
    print("    - Más robusto en entornos complejos")
    print("  • Desventajas:")
    print("    - Computacionalmente más costoso")
    print("    - Más complejo de implementar y depurar")
    print("    - Requiere mantener distribuciones de probabilidad")
    print()
    
    # Comparativa del MDP (Parte 2)
    print("PARTE 2 - MDP del Río (Value Iteration):")
    print("  • Ventajas:")
    print("    - Encuentra política óptima garantizada")
    print("    - Maneja recompensas y decisiones secuenciales")
    print("    - Considera efectos a largo plazo")
    print("  • Desventajas:")
    print("    - Requiere espacio de estados completo")
    print("    - Costoso para problemas grandes (curse of dimensionality)")
    print("    - Asume modelo de transición conocido")
    print()
    
    # Recomendaciones de uso
    print("RECOMENDACIONES DE USO:")
    print("  • Para entornos deterministas pequeños: Agente Lógico")
    print("  • Para entornos con incertidumbre parcial: Agente Bayesiano")
    print("  • Para decisiones secuenciales con recompensas: MDP")
    print("  • Para problemas grandes: considerar métodos aproximados")
    print()
    
    # Consideraciones para la implementación
    print("CONSIDERACIONES TÉCNICAS:")
    print("  • Agente Lógico: Más fácil de extender con nuevas reglas")
    print("  • Agente Bayesiano: Escala mejor con más tipos de trampas")
    print("  • MDP: Puede combinarse con aprendizaje por refuerzo")
    print()
    
    print("="*60)
    input("\nPresiona Enter para volver al menú principal...")

def main():
    """
    Función principal que gestiona el menú unificado
    
    Flujo:
    1. Mostrar banner inicial
    2. Presentar menú con todas las opciones
    3. Ejecutar la opción seleccionada
    4. Manejar errores y excepciones
    5. Permitir salir ordenadamente
    """
    mostrar_banner()
    
    # Bucle principal del programa
    while True:
        print("\n" + "="*60)
        print("MENÚ PRINCIPAL - PROYECTO COMPLETO")
        print("="*60)
        
        # Opciones organizadas por partes del proyecto
        print("PARTE 1 - PALACIO (Agente Lógico):")
        print("  1. Jugar yo mismo (modo manual)")
        print("  2. Ver al agente inteligente MEJORADO (exploración automática)")
        print()
        
        print("PARTE 2 - PALACIO (Agente Bayesiano):")
        print("  3. Agente Bayesiano (trampas específicas: Fuego, Pinchos, Dardos)")
        print()
        
        print("PARTE 2 - RÍO (MDP y Value Iteration):")
        print("  4. Cruzar el río (Proceso de Decisión de Markov)")
        print()
        
        print("UTILIDADES Y ANÁLISIS:")
        print("  5. Comparar resultados de todas las partes")
        print("  6. Salir del programa")
        print("="*60)
        
        try:
            # Leer opción del usuario
            opcion = input("\nSelecciona una opción (1-6): ").strip()
            
            # Ejecutar opción seleccionada
            if opcion == '1':
                print("\n" + ">"*30)
                print("INICIANDO: MODO MANUAL (PARTE 1)")
                print(">"*30)
                # Ejecutar modo jugador de la parte 1
                modo_jugador()
                
            elif opcion == '2':
                print("\n" + ">"*30)
                print("INICIANDO: AGENTE INTELIGENTE (PARTE 1)")
                print(">"*30)
                # Ejecutar modo automático de la parte 1
                modo_auto_inteligente()
                
            elif opcion == '3':
                print("\n" + ">"*30)
                print("INICIANDO: AGENTE BAYESIANO (PARTE 2)")
                print(">"*30)
                # Ejecutar modo bayesiano de la parte 2
                modo_bayesiano()
                
            elif opcion == '4':
                print("\n" + ">"*30)
                print("INICIANDO: RÍO MDP (PARTE 2)")
                print(">"*30)
                # Ejecutar modo río MDP de la parte 2
                modo_rio_mdp()
                
            elif opcion == '5':
                # Mostrar comparativa de enfoques
                comparar_resultados()
                
            elif opcion == '6':
                # Salir ordenadamente del programa
                print("\n¡Gracias por usar el proyecto completo!")
                print("Hasta la próxima misión...")
                break
                
            else:
                # Opción no válida
                print("\nOpción no válida. Por favor, selecciona un número del 1 al 6.")
                print("Las opciones disponibles son:")
                print("  1-2: Parte 1 (Agente Lógico)")
                print("  3-4: Parte 2 (Bayesiano y MDP)")
                print("  5: Comparativa")
                print("  6: Salir")
        
        except KeyboardInterrupt:
            # Manejar interrupción por Ctrl+C
            print("\n\nPrograma interrumpido por el usuario.")
            continuar = input("¿Deseas salir del programa? (s/n): ").strip().lower()
            if continuar == 's':
                print("Saliendo del programa...")
                break
            else:
                print("Continuando con el programa...")
                continue
        
        except Exception as e:
            # Manejar cualquier otro error inesperado
            print(f"\nError inesperado: {e}")
            print("Reiniciando menú principal...")
            time.sleep(2)

def verificar_dependencias():
    """
    Verifica que todas las dependencias necesarias estén instaladas
    
    Dependencias requeridas:
    - NumPy: Para cálculos numéricos en MDP y Bayesiano
    - Funciones propias: Todos los módulos .py del proyecto
    """
    print("Verificando dependencias...")
    
    # Verificar NumPy (requerido para parte 2)
    try:
        import numpy as np
        print("NumPy cargado correctamente")
    except ImportError:
        print("ERROR: Se requiere NumPy para la Parte 2")
        print("  Instala con: pip install numpy")
        return False
    
    # Verificar que todos los módulos se importan correctamente
    modulos_requeridos = [
        'kurtz',
        'palacio_bayesiano', 
        'river_mdp'
    ]
    
    for modulo in modulos_requeridos:
        try:
            __import__(modulo)
            print(f"Módulo '{modulo}' cargado correctamente")
        except ImportError as e:
            print(f"ERROR: No se pudo cargar módulo '{modulo}': {e}")
            return False
    
    print("\nTodas las dependencias verificadas correctamente")
    return True

if __name__ == "__main__":
    """
    Punto de entrada cuando se ejecuta este archivo directamente
    
    Realiza:
    1. Verificación de dependencias
    2. Ejecución del programa principal
    3. Manejo de errores críticos
    """
    
    # Verificar dependencias antes de ejecutar
    if not verificar_dependencias():
        print("\nNo se pueden verificar todas las dependencias.")
        print("Asegúrate de tener instalado NumPy y todos los archivos .py")
        sys.exit(1)
    
    # Ejecutar programa principal con manejo de errores
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma terminado por el usuario.")
    except Exception as e:
        print(f"\nError crítico en la ejecución: {e}")
        print("Por favor, revisa que todos los archivos estén completos.")
        sys.exit(1)
    
    # Mensaje final al salir
    print("\n" + "-"*60)
    print("FIN DEL PROYECTO FIA - BUSCANDO AL CORONEL KURTZ")
    print("¡Gracias por usar la implementación completa!")
    print("-"*60)