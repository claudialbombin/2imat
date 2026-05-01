#estadisticas.py
import sys
import os

if __name__ == "__main__":
    fichero = sys.argv[1]
    usuarios = set()
    localizaciones = set()
    total_interacciones = 0
    checkins_julio = 0
    checkins_agosto = 0
    
    # Añadir encoding para evitar problemas con caracteres
    with open(fichero, "r", encoding='utf-8') as f:
        for l in f:
            total_interacciones += 1
            lista_elementos = l.strip().split()
            
            if len(lista_elementos) >= 5:  # Verificar que tenga todos los campos
                id_usuario = lista_elementos[0]
                fecha = lista_elementos[1]
                id_loc = lista_elementos[4]
                usuarios.add(id_usuario)
                localizaciones.add(id_loc)

                if fecha.startswith("2010-07"):
                    checkins_julio += 1
                if fecha.startswith("2010-08"):
                    checkins_agosto += 1
    
    print(f"Estadísticas para {os.path.basename(fichero)}")
    print(f"Número de usuarios distintos: {len(usuarios)}")
    print(f"Número de localizaciones distintas: {len(localizaciones)}")
    print(f"Número de filas completas: {total_interacciones}")
    print(f"Número de check-ins en 2010-07: {checkins_julio}")
    print(f"Número de check-ins en 2010-08: {checkins_agosto}")