# topn_selection_Claudia_Gonzalo.py
import sys

if __name__ == "__main__":
    archivo = sys.argv[1]
    n = int(sys.argv[2])
    archivo_salida = sys.argv[3]
    
    dic_usuarios = {}
    
    with open(archivo, "r") as e:
        for l in e:
            l = l.strip().split()
            if l:
                usuario = l[0]
                if usuario in dic_usuarios:
                    dic_usuarios[usuario] += 1
                else:
                    dic_usuarios[usuario] = 1  # CORRECCIÓN: Inicializar en 1, no en 0
    
    # Ordenar usuarios por número de check-ins (descendente)
    usuarios_ordenados = sorted(dic_usuarios.items(), key=lambda x: x[1], reverse=True)
    
    with open(archivo_salida, "w") as s:
        for i in range(min(n, len(usuarios_ordenados))):
            usuario, count = usuarios_ordenados[i]
            s.write(f"{usuario} {count}\n")