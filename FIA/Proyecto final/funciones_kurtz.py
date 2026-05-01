import random
import sys
import time
from collections import deque

# ============================================================================
# CLASE PALACIO
# ============================================================================

class Palacio:
    def __init__(self, tamano=6):
        self.n = tamano
        self.capitán_pos = (0, 0)
        self.con_kurtz = False
        self.soldado_vivo = True
        self.tengo_granada = True
        self.pasos = 0
        self.celdas_visitadas = []
        self.celdas_seguras = []
        self.celdas_peligrosas = []

        # DEBUG: Para ver qué está pasando
        # print(f"[DEBUG] Creando palacio {tamano}x{tamano}")

        print("Generando palacio aleatorio...")
        time.sleep(0.1)

        # Crear todas las celdas excepto la inicial
        todas = []
        for i in range(self.n):
            for j in range(self.n):
                if (i, j) != (0, 0):
                    todas.append((i, j))

        random.shuffle(todas)

        # Asignar elementos (esto es como una lotería pero con muerte)
        self.precipicios = []
        for i in range(3):
            if todas:
                p = todas.pop()
                self.precipicios.append(p)

        # DEBUG: Ver posiciones de precipicios
        # print(f"[DEBUG] Precipicios en: {self.precipicios}")

        if todas:
            self.soldado = todas.pop()

        if todas:
            self.kurtz = todas.pop()

        if todas:
            self.salida = todas.pop()

        # DEBUG: Ver dónde está todo
        # print(f"[DEBUG] Soldado en: {self.soldado}")
        # print(f"[DEBUG] Kurtz en: {self.kurtz}")
        # print(f"[DEBUG] Salida en: {self.salida}")
        # print(f"[DEBUG] Celdas sobrantes: {len(todas)}")

        # Inicializar listas (esto parece obvio pero lo pongo por si acaso)
        self.celdas_visitadas.append(self.capitán_pos)
        self.celdas_seguras.append(self.capitán_pos)

        # NOTA PARA MI: La posición (0,0) siempre es segura al inicio
        # No tocar esto o se rompe todo

        print("¡Palacio listo!")
        print()

    def mover(self, dirección):
        """Intenta mover al capitán"""
        self.pasos += 1
        x, y = self.capitán_pos
        nueva = None
        dir_texto = ""

        # Este bloque de ifs es feo pero funciona
        # No intentar "refactorizar" o se rompe la magia
        if dirección == 'N' and x > 0:
            nueva = (x-1, y)
            dir_texto = "norte"
        elif dirección == 'S' and x < self.n-1:
            nueva = (x+1, y)
            dir_texto = "sur"
        elif dirección == 'O' and y > 0:
            nueva = (x, y-1)
            dir_texto = "oeste"
        elif dirección == 'E' and y < self.n-1:
            nueva = (x, y+1)
            dir_texto = "este"  # CORRECCIÓN: Faltaba esto

        # DEBUG: Ver qué movimiento se intenta
        # print(f"[DEBUG] Intento mover {dirección} de ({x},{y}) a {nueva}")

        if nueva is None:
            # print(f"[DEBUG] Movimiento inválido: {dirección} desde ({x},{y})")
            return False, f"No puedo ir al {dirección} (pared)"

        # Verificar peligros (aquí es donde suelen morir los agentes)
        if nueva in self.precipicios:
            # print(f"[DEBUG] ¡CAÍDA! Precipicio en {nueva}")
            return False, "¡Caíste por un precipicio!"

        if self.soldado_vivo and nueva == self.soldado:
            # print(f"[DEBUG] ¡MUERTE! Soldado en {nueva}")
            return False, "¡El soldado te mató!"

        # Movimiento exitoso (si llegamos aquí, es un milagro)
        self.capitán_pos = nueva
        if nueva not in self.celdas_visitadas:
            self.celdas_visitadas.append(nueva)

        if nueva in self.celdas_peligrosas:
            self.celdas_peligrosas.remove(nueva)

        # Ver si encontramos a Kurtz (¡OBJETIVO PRINCIPAL!)
        if not self.con_kurtz and nueva == self.kurtz:
            self.con_kurtz = True
            # print(f"[DEBUG] ¡KURTZ ENCONTRADO en {nueva}!")
            return True, f"Moví {dir_texto}. ¡ENCONTRASTE A KURTZ!"

        # Ver si llegamos a la salida (pero sin Kurtz no vale)
        if nueva == self.salida:
            if self.con_kurtz:
                # print(f"[DEBUG] ¡EN SALIDA CON KURTZ!")
                return True, f"Moví {dir_texto}. ¡Estás en la salida con Kurtz!"
            else:
                # print(f"[DEBUG] En salida pero sin Kurtz...")
                return True, f"Moví {dir_texto}. Estás en la salida."

        # print(f"[DEBUG] Movimiento normal a {nueva}")
        return True, f"Moví {dir_texto} a ({nueva[0]+1},{nueva[1]+1})"

    def tirar_granada(self, dirección):
        """Tira la granada (solo una)"""
        if not self.tengo_granada:
            # print("[DEBUG] Intento tirar granada pero ya no tengo")
            return False, "No tengo granadas."

        x, y = self.capitán_pos
        objetivo = None

        # Más ifs feos pero funcionales
        if dirección == 'N' and x > 0:
            objetivo = (x-1, y)
        elif dirección == 'S' and x < self.n-1:
            objetivo = (x+1, y)
        elif dirección == 'O' and y > 0:
            objetivo = (x, y-1)
        elif dirección == 'E' and y < self.n-1:
            objetivo = (x, y+1)

        if objetivo is None:
            # print(f"[DEBUG] Granada a pared desde ({x},{y}) dirección {dirección}")
            return False, "No puedo tirar ahí (pared)"

        self.tengo_granada = False
        # print(f"[DEBUG] Granada usada. Objetivo: {objetivo}")

        # Aquí la lógica de la granada. CUIDADO: tocar esto rompe el equilibrio.
        if objetivo == self.soldado and self.soldado_vivo:
            self.soldado_vivo = False
            # La celda del soldado ahora es segura (obvio)
            if objetivo not in self.celdas_seguras:
                self.celdas_seguras.append(objetivo)
            # print(f"[DEBUG] ¡SOLDADO ELIMINADO en {objetivo}!")
            return True, "¡Granada efectiva! Soldado eliminado."

        elif objetivo == self.kurtz:
            # print(f"[DEBUG] Kurtz esquiva la granada (lógico)")
            return True, "Kurtz evita la granada."

        else:
            # print(f"[DEBUG] Granada desperdiciada en {objetivo}")
            return True, "Granada a celda vacía."

    def intentar_salir(self):
        """Intenta salir del palacio (comando X)"""
        # print(f"[DEBUG] Intentar salir desde {self.capitán_pos}, salida en {self.salida}")
        if self.capitán_pos == self.salida:
            if self.con_kurtz:
                # print("[DEBUG] ¡VICTORIA!")
                return True, "¡MISIÓN CUMPLIDA! Has rescatado a Kurtz."
            else:
                # print("[DEBUG] En salida pero sin Kurtz (qué pena)")
                return False, "No puedes salir sin Kurtz."
        else:
            # print("[DEBUG] No estoy en la salida")
            return False, "No estás en la salida."

    def que_siento(self):
        """Devuelve lo que percibe el capitán"""
        x, y = self.capitán_pos
        percepciones = []

        # DEBUG: Para ver qué se está sintiendo
        # print(f"[DEBUG] Calculando perceptos desde ({x},{y})")

        # Paredes (esto es fácil)
        if x == 0:
            percepciones.append("pared_norte")
        if x == self.n-1:
            percepciones.append("pared_sur")
        if y == 0:
            percepciones.append("pared_oeste")
        if y == self.n-1:
            percepciones.append("pared_este")

        # Brisa (precipicios adyacentes)
        vecinos = self.vecinos_de((x, y))
        for v in vecinos:
            if v in self.precipicios:
                percepciones.append("brisa")
                # print(f"[DEBUG] Brisa por precipicio en {v}")
                break

        # Ronquido (soldado adyacente y vivo)
        if self.soldado_vivo:
            for v in vecinos:
                if v == self.soldado:
                    percepciones.append("ronquido")
                    # print(f"[DEBUG] Ronquido por soldado en {v}")
                    break

        # Resplandor (en o cerca de salida)
        if (x, y) == self.salida:
            percepciones.append("resplandor_fuerte")
            # print("[DEBUG] ¡Resplandor FUERTE! (en salida)")
        else:
            for v in vecinos:
                if v == self.salida:
                    percepciones.append("resplandor_suave")
                    # print(f"[DEBUG] Resplandor suave (salida en {v})")
                    break

        # print(f"[DEBUG] Perceptos finales: {percepciones}")
        return percepciones

    def vecinos_de(self, pos):
        """Devuelve las celdas vecinas de una posición"""
        x, y = pos
        vecinos = []
        if x > 0:
            vecinos.append((x-1, y))
        if x < self.n-1:
            vecinos.append((x+1, y))
        if y > 0:
            vecinos.append((x, y-1))
        if y < self.n-1:
            vecinos.append((x, y+1))
        # print(f"[DEBUG] Vecinos de {pos}: {vecinos}")
        return vecinos

    def mostrar_mapa_conocido(self):
        """Muestra el mapa como lo ve el capitán"""
        print("\n" + "-"*40)
        print("MAPA ACTUAL:")
        print("-"*40)

        for i in range(self.n):
            fila = ""
            for j in range(self.n):
                celda = (i, j)

                if celda == self.capitán_pos:
                    if self.con_kurtz:
                        fila += "[CK]"  # Capitán con Kurtz
                    else:
                        fila += "[CW]"  # Capitán solo

                elif celda in self.celdas_visitadas:
                    if celda in self.precipicios:
                        fila += "[P] "  # Precipicio
                    elif celda == self.soldado and not self.soldado_vivo:
                        fila += "[X] "  # Soldado muerto
                    elif celda == self.soldado and self.soldado_vivo:
                        fila += "[S] "  # Soldado vivo
                    elif celda == self.kurtz:
                        fila += "[K] "  # Kurtz
                    elif celda == self.salida:
                        fila += "[E] "  # Exit/Salida
                    elif celda in self.celdas_seguras:
                        fila += "[.] "  # Segura
                    else:
                        fila += "[v] "  # Visitada
                else:
                    fila += "[?] "     # Desconocida

            print(f"Fila {i+1}: {fila}")

        print(f"\nPosición: ({self.capitán_pos[0]+1},{self.capitán_pos[1]+1})")
        if self.con_kurtz:
            print("Tienes a Kurtz contigo.")
        print("-"*40)

    def mostrar_mapa_completo(self):
        """Muestra el mapa completo (modo cheat)"""
        print("\n" + "-"*40)
        print("MAPA COMPLETO (cheat):")
        print("-"*40)

        for i in range(self.n):
            fila = ""
            for j in range(self.n):
                celda = (i, j)

                if celda == self.capitán_pos:
                    if self.con_kurtz:
                        fila += "[CK]"
                    else:
                        fila += "[CW]"

                elif celda in self.precipicios:
                    fila += "[P] "
                elif celda == self.soldado and self.soldado_vivo:
                    fila += "[S] "
                elif celda == self.kurtz:
                    fila += "[K] "
                elif celda == self.salida:
                    fila += "[E] "
                elif celda in self.celdas_visitadas:
                    fila += "[.] "
                else:
                    fila += "[?] "

            print(f"Fila {i+1}: {fila}")

        print("\n(Modo cheat - no usar en producción)")
        print("-"*40)

# ============================================================================
# CLASE AGENTE EXPLORADOR (INTELIGENTE) - REVISADA Y MEJORADA Y EVITANDO BUCLES?
# ============================================================================

class AgenteExplorador:
    """Agente que explora sistemáticamente evitando peligros"""
    # NOTA: Esta clase es compleja. Si no la entiendes, no eres el único.
    # Yo misma la escribí y a veces me pregunto cómo funciona.
    # CORRECCIÓN: Ahora con menos bucles infinitos (en teoría)
    # CORRECCIÓN 2: Ahora guarda camino a la salida cuando la encuentra

    def __init__(self, palacio):
        self.p = palacio
        self.conocimiento = {}
        self.stack = []  # Pila para DFS (creo)
        self.camino = []  # Para no perdernos (en teoría)
        self.celdas_con_brisa = set()
        self.celdas_con_ronquido = set()
        # Para evitar bucles (lo intenta pero falla mas q yo bajo presion)
        self.intentos_movimiento = {}
        self.celdas_riesgo = {}  # Para celdas con posibles peligros
        self.objetivo_actual = None  # Nuevo: para tener un objetivo claro
        self.buscando_salida = False  # Nuevo: si ya tenemos a Kurtz
        self.camino_a_salida = None  # NUEVO: guarda camino a salida cuando se detecta
        self.salida_encontrada = False  # NUEVO: si hemos encontrado la salida

        print("[AGENTE] Inicializando conocimiento...")

        # Inicializar conocimiento (matriz de conocimiento)
        # Esto es un diccionario gigante. No es eficiente pero funciona. Se xq? no, pero funciona
        for i in range(self.p.n):
            for j in range(self.p.n):
                self.conocimiento[(i, j)] = {
                    'visitada': False,
                    'segura': False,
                    'precipicio': False,
                    'soldado': False,
                    'brisa_detectada': False,
                    'ronquido_detectado': False,
                    'riesgo_precipicio': 0,  # Contador de riesgo precipicio
                    'riesgo_soldado': 0,     # Contador de riesgo soldado
                    'resplandor': False      # Nuevo: si hemos sentido resplandor
                }
                self.intentos_movimiento[(i, j)] = 0
                self.celdas_riesgo[(i, j)] = 0

        # Inicializar desde posición actual (esto es importante)
        self.marcar_visitada(self.p.capitán_pos)
        self.marcar_segura(self.p.capitán_pos)
        self.camino.append(self.p.capitán_pos)

        # Iniciar exploración (aquí empieza la magia)
        self.iniciar_exploracion()

        # print(f"[AGENTE] Inicializado. Camino: {self.camino}")
        # print(f"[AGENTE] Stack inicial: {self.stack}")

    def marcar_visitada(self, celda):
        """Marca una celda como visitada (parece obvio, lo sé)"""
        self.conocimiento[celda]['visitada'] = True
        if celda not in self.p.celdas_visitadas:
            self.p.celdas_visitadas.append(celda)
        # print(f"[AGENTE] Celda {celda} marcada como visitada")

    def marcar_segura(self, celda):
        """Marca una celda como segura (ojalá fuera verdad)"""
        self.conocimiento[celda]['segura'] = True
        if celda not in self.p.celdas_seguras:
            self.p.celdas_seguras.append(celda)
        # print(f"[AGENTE] Celda {celda} marcada como segura"

    def actualizar_conocimiento(self, percepciones):
        """Actualiza el conocimiento con los perceptos actuales"""
        # print(f"[AGENTE] Actualizando conocimiento con: {percepciones}")
        pos = self.p.capitán_pos
        vecinos = self.p.vecinos_de(pos)

        # Resetear marcas de peligro para esta posición
        self.conocimiento[pos]['brisa_detectada'] = False
        self.conocimiento[pos]['ronquido_detectado'] = False
        self.conocimiento[pos]['resplandor'] = False

        # NUEVO: Si detectamos resplandor fuerte (estamos en la salida)
        if 'resplandor_fuerte' in percepciones:
            # print(f"[AGENTE] ¡ESTAMOS EN LA SALIDA! Guardando posición...")
            self.salida_encontrada = True
            self.guardar_camino_a_salida(pos)

        # NUEVO: Si detectamos resplandor suave (salida adyacente)
        elif 'resplandor_suave' in percepciones:
            # print(f"[AGENTE] Salida adyacente detectada desde {pos}")
            for v in vecinos:
                if not self.conocimiento[v]['visitada']:
                    # Marcar que esta celda podría ser la salida
                    # print(f"[AGENTE] Posible salida en {v}")
                    pass

        # Actualizar basado en perceptos actuales
        if 'brisa' in percepciones:
            # print(f"[AGENTE] ¡BRISA en {pos}!")
            self.conocimiento[pos]['brisa_detectada'] = True
            self.celdas_con_brisa.add(pos)

            # Incrementar riesgo en vecinos no visitados
            for v in vecinos:
                if not self.conocimiento[v]['visitada']:
                    self.conocimiento[v]['riesgo_precipicio'] += 1
                    # Marcar como precipicio solo si hay suficiente evidencia
                    if self.conocimiento[v]['riesgo_precipicio'] >= 2:
                        self.conocimiento[v]['precipicio'] = True
                        if v in self.p.celdas_seguras:
                            self.p.celdas_seguras.remove(v)
                        # print(f"[AGENTE] Celda {v} marcada como posible precipicio")

        if 'ronquido' in percepciones and self.p.soldado_vivo:
            # print(f"[AGENTE] ¡RONQUIDO en {pos}!")
            self.conocimiento[pos]['ronquido_detectado'] = True
            self.celdas_con_ronquido.add(pos)

            # Incrementar riesgo en vecinos no visitados
            for v in vecinos:
                if not self.conocimiento[v]['visitada']:
                    self.conocimiento[v]['riesgo_soldado'] += 1
                    # Marcar como soldado solo si hay suficiente evidencia
                    if self.conocimiento[v]['riesgo_soldado'] >= 2:
                        self.conocimiento[v]['soldado'] = True
                        if v in self.p.celdas_seguras:
                            self.p.celdas_seguras.remove(v)
                        # print(f"[AGENTE] Celda {v} marcada como posible soldado")

        # Nuevo: Guardar información de resplandor
        if 'resplandor_fuerte' in percepciones or 'resplandor_suave' in percepciones:
            self.conocimiento[pos]['resplandor'] = True
            # print(f"[AGENTE] ¡RESPLANDOR en {pos}!")

        # Lógica de SEGURIDAD (cuando NO hay peligros)
        # Esto es tan importante como lo anterior pero menos emocionante y falla bastante mas
        if 'brisa' not in percepciones:
            for v in vecinos:
                # Reducir riesgo de precipicio
                if self.conocimiento[v]['riesgo_precipicio'] > 0:
                    self.conocimiento[v]['riesgo_precipicio'] -= 1

                # Si riesgo bajo y no hay soldado, marcar como segura
                if (self.conocimiento[v]['riesgo_precipicio'] <= 1 and
                        not self.conocimiento[v]['soldado']):
                    self.marcar_segura(v)
                    self.conocimiento[v]['precipicio'] = False

        if 'ronquido' not in percepciones and self.p.soldado_vivo:
            for v in vecinos:
                # Reducir riesgo de soldado
                if self.conocimiento[v]['riesgo_soldado'] > 0:
                    self.conocimiento[v]['riesgo_soldado'] -= 1

                # Si riesgo bajo y no hay precipicio, marcar como segura
                if (self.conocimiento[v]['riesgo_soldado'] <= 1 and
                        not self.conocimiento[v]['precipicio']):
                    self.marcar_segura(v)
                    self.conocimiento[v]['soldado'] = False

        # Si el soldado está muerto, limpiar marcas ya que ya no hay soldado en la celda
        if not self.p.soldado_vivo:
            # print("[AGENTE] Soldado muerto - limpiando marcas de soldado")
            for i in range(self.p.n):
                for j in range(self.p.n):
                    self.conocimiento[(i, j)]['soldado'] = False
                    self.conocimiento[(i, j)]['riesgo_soldado'] = 0

        # Si tenemos a Kurtz, cambiar objetivo a buscar salida
        if self.p.con_kurtz and not self.buscando_salida:
            print("[AGENTE] ¡Tengo a Kurtz! Ahora buscaré la salida.")
            self.buscando_salida = True
            # Limpiar objetivo actual para buscar salida
            self.objetivo_actual = None

            # NUEVO: Si ya conocemos la salida, usar el camino guardado
            if self.salida_encontrada and self.camino_a_salida:
                print("[AGENTE] ¡Ya conozco la salida! Usando camino guardado...")

    def guardar_camino_a_salida(self, pos_salida):
        """Guarda el camino desde la posición actual hasta la salida"""
        # print(f"[AGENTE] Guardando camino a salida desde {pos_salida}")

        # Calcular camino inverso (desde salida hasta posición actual)
        # Usamos BFS para encontrar el camino más corto a través de celdas seguras
        inicio = self.p.capitán_pos
        objetivo = pos_salida

        # print(f"[AGENTE] BFS para guardar camino desde {inicio} a {objetivo}")
        cola = deque()
        cola.append((inicio, []))
        visitados = set([inicio])

        while cola:
            actual, camino = cola.popleft()

            if actual == objetivo:
                if camino:
                    # Invertir el camino para que vaya desde inicio hasta objetivo
                    camino_completo = [inicio] + camino
                    self.camino_a_salida = camino_completo
                    # print(f"[AGENTE] Camino a salida guardado: {self.camino_a_salida}")
                    return
                else:
                    # Estamos en la salida
                    self.camino_a_salida = [inicio]
                    # print(f"[AGENTE] Ya estamos en la salida: {self.camino_a_salida}")
                    return

            for vecino in self.p.vecinos_de(actual):
                if vecino not in visitados:
                    # Solo considerar celdas seguras o visitadas
                    if (self.conocimiento[vecino]['segura'] or
                        vecino in self.p.celdas_seguras or
                            self.conocimiento[vecino]['visitada']):
                        visitados.add(vecino)
                        nuevo_camino = camino + [vecino]
                        cola.append((vecino, nuevo_camino))

        # print(f"[AGENTE] No se pudo guardar camino a salida desde {inicio}")

    def iniciar_exploracion(self):
        """Inicia la exploración sistemática"""
        # print("[AGENTE] Iniciando exploración...")
        pos = self.p.capitán_pos
        for v in self.p.vecinos_de(pos):
            if v not in self.stack:
                self.stack.append(v)
        # print(f"[AGENTE] Stack después de iniciar: {self.stack}")

    def es_movimiento_seguro(self, direccion):
        """Verifica si un movimiento es seguro"""
        # print(f"[AGENTE] Verificando seguridad de mover {direccion}")
        x, y = self.p.capitán_pos
        nueva_pos = None

        if direccion == 'N' and x > 0:
            nueva_pos = (x-1, y)
        elif direccion == 'S' and x < self.p.n-1:
            nueva_pos = (x+1, y)
        elif direccion == 'O' and y > 0:
            nueva_pos = (x, y-1)
        elif direccion == 'E' and y < self.p.n-1:
            nueva_pos = (x, y+1)

        if nueva_pos is None:
            # print(f"[AGENTE] Movimiento {direccion} inválido (pared)")
            return False

        # NO moverse a celdas peligrosas conocidas
        if nueva_pos in self.p.precipicios:
            # print(f"[AGENTE] {nueva_pos} es un precipicio conocido")
            return False

        if self.p.soldado_vivo and nueva_pos == self.p.soldado:
            # print(f"[AGENTE] {nueva_pos} es el soldado vivo")
            return False

        # NO moverse a celdas marcadas como peligrosas
        if self.conocimiento[nueva_pos]['precipicio'] and self.conocimiento[nueva_pos]['riesgo_precipicio'] >= 2:
            # print(f"[AGENTE] {nueva_pos} marcada como precipicio con alta seguridad")
            return False

        if self.conocimiento[nueva_pos]['soldado'] and self.conocimiento[nueva_pos]['riesgo_soldado'] >= 2:
            # print(f"[AGENTE] {nueva_pos} marcada como soldado con alta seguridad")
            return False

        # Si estamos buscando salida y tenemos camino a salida guardado, ser más permisivo
        if self.buscando_salida and self.camino_a_salida:
            # Permitir moverse a celdas en el camino a salida aunque tengan algo de riesgo
            if nueva_pos in self.camino_a_salida:
                # print(f"[AGENTE] {nueva_pos} está en camino a salida - permitiendo")
                # Pero aún así evitar peligros altos
                if self.conocimiento[nueva_pos]['riesgo_precipicio'] >= 3 or self.conocimiento[nueva_pos]['riesgo_soldado'] >= 3:
                    return False
                return True

        # Si estamos buscando salida y hay resplandor, ser más agresivo
        if self.buscando_salida and self.conocimiento[self.p.capitán_pos]['resplandor']:
            # print(f"[AGENTE] Buscando salida con resplandor - permitiendo más riesgo")
            # Permitir más riesgo cuando estamos cerca de la salida
            if self.conocimiento[nueva_pos]['riesgo_precipicio'] <= 2 and self.conocimiento[nueva_pos]['riesgo_soldado'] <= 2:
                return True

        # Si hay brisa, permitir movimientos con precaución
        if self.conocimiento[self.p.capitán_pos]['brisa_detectada']:
            if not self.conocimiento[nueva_pos]['segura']:
                # Permitir si el riesgo es bajo y estamos atrapados
                if self.conocimiento[nueva_pos]['riesgo_precipicio'] <= 1:
                    # Verificar si estamos en un bucle
                    if self.detectar_bucle():
                        # print(f"[AGENTE] Bucle detectado - arriesgando con {nueva_pos}")
                        return True
                # print(f"[AGENTE] {nueva_pos} no segura y hay brisa")
                return False

        # Si hay ronquido, permitir movimientos con precaución
        if (self.conocimiento[self.p.capitán_pos]['ronquido_detectado'] and
                self.p.soldado_vivo):
            if not self.conocimiento[nueva_pos]['segura']:
                # Permitir si el riesgo es bajo
                if self.conocimiento[nueva_pos]['riesgo_soldado'] <= 1:
                    # Verificar si estamos en un bucle
                    if self.detectar_bucle():
                        # print(f"[AGENTE] Bucle detectado - arriesgando con {nueva_pos}")
                        return True
                # print(f"[AGENTE] {nueva_pos} no segura y hay ronquido")
                return False

        # Doble peligro - ser extremadamente cuidadoso
        if (self.conocimiento[self.p.capitán_pos]['brisa_detectada'] and
                self.conocimiento[self.p.capitán_pos]['ronquido_detectado']):
            if not self.conocimiento[nueva_pos]['visitada']:
                # Solo permitir si estamos completamente seguros
                if (self.conocimiento[nueva_pos]['riesgo_precipicio'] > 0 or
                        self.conocimiento[nueva_pos]['riesgo_soldado'] > 0):
                    # print(f"[AGENTE] Doble peligro - evitando {nueva_pos}")
                    return False

        # Contar intentos de movimiento para evitar bucles
        self.intentos_movimiento[nueva_pos] = self.intentos_movimiento.get(
            nueva_pos, 0) + 1
        if self.intentos_movimiento[nueva_pos] > 5 and len(self.camino) > 10:
            # Demasiados intentos a la misma celda - probable bucle
            # print(f"[AGENTE] Demasiados intentos a {nueva_pos} - evitando")
            return False

        # print(f"[AGENTE] Movimiento {direccion} a {nueva_pos} considerado seguro")
        return True

    def detectar_bucle(self):
        """Detecta si el agente está en un bucle"""
        # print("[AGENTE] Detectando posibles bucles...")
        if len(self.camino) < 6:
            return False

        # Verificar patrón repetitivo
        ultimas = self.camino[-6:]
        # Si estamos yendo y viniendo entre las mismas celdas
        if len(set(ultimas)) <= 2:
            # print(f"[AGENTE] ¡BUCLE DETECTADO! Últimas posiciones: {ultimas}")
            return True

        # Verificar si hemos visitado la posición actual muchas veces
        pos_actual = self.p.capitán_pos
        visitas_recientes = self.camino[-10:].count(pos_actual)
        if visitas_recientes >= 4:
            # print(f"[AGENTE] ¡BUCLE DETECTADO! Posición {pos_actual} visitada {visitas_recientes} veces")
            return True

        return False

    def encontrar_celda_con_resplandor(self):
        """Encuentra la celda más cercana con resplandor"""
        # print("[AGENTE] Buscando celdas con resplandor...")
        celdas_con_resplandor = []

        for i in range(self.p.n):
            for j in range(self.p.n):
                if self.conocimiento[(i, j)]['resplandor'] and not self.conocimiento[(i, j)]['visitada']:
                    celdas_con_resplandor.append((i, j))

        if not celdas_con_resplandor:
            return None

        # Encontrar la más cercana a nuestra posición actual
        pos_actual = self.p.capitán_pos
        mejor_celda = None
        menor_distancia = float('inf')

        for celda in celdas_con_resplandor:
            distancia = abs(celda[0] - pos_actual[0]) + \
                abs(celda[1] - pos_actual[1])
            if distancia < menor_distancia:
                menor_distancia = distancia
                mejor_celda = celda

        # print(f"[AGENTE] Celda con resplandor más cercana: {mejor_celda}")
        return mejor_celda

    def encontrar_celda_no_visitada_cercana(self):
        """Encuentra la celda no visitada más cercana"""
        # print("[AGENTE] Buscando celdas no visitadas cercanas...")
        pos_actual = self.p.capitán_pos
        mejor_celda = None
        menor_distancia = float('inf')

        for i in range(self.p.n):
            for j in range(self.p.n):
                if not self.conocimiento[(i, j)]['visitada'] and self.conocimiento[(i, j)]['segura']:
                    distancia = abs(i - pos_actual[0]) + abs(j - pos_actual[1])
                    if distancia < menor_distancia:
                        menor_distancia = distancia
                        mejor_celda = (i, j)

        return mejor_celda

    def decidir_siguiente_movimiento(self):
        """Decide el próximo movimiento inteligentemente"""
        # print("\n[AGENTE] Decidiendo próximo movimiento...")

        # Si tenemos a Kurtz y estamos en salida, salir
        if self.p.con_kurtz and self.p.capitán_pos == self.p.salida:
            # print("[AGENTE] ¡EN SALIDA CON KURTZ! Comando SALIR")
            return 'SALIR', None

        # NUEVO ESTRATEGIA 0: Si tenemos a Kurtz y conocemos el camino a salida, seguirlo
        if self.p.con_kurtz and self.camino_a_salida and len(self.camino_a_salida) > 1:
            # print(f"[AGENTE] Usando camino guardado a salida: {self.camino_a_salida}")

            # Encontrar nuestra posición en el camino
            try:
                indice_actual = self.camino_a_salida.index(self.p.capitán_pos)
                if indice_actual < len(self.camino_a_salida) - 1:
                    siguiente = self.camino_a_salida[indice_actual + 1]
                    # print(f"[AGENTE] Siguiente en camino a salida: {siguiente}")

                    # Calcular dirección hacia siguiente celda
                    if siguiente[0] < self.p.capitán_pos[0]:
                        if self.es_movimiento_seguro('N'):
                            return 'MOVER', 'N'
                    elif siguiente[0] > self.p.capitán_pos[0]:
                        if self.es_movimiento_seguro('S'):
                            return 'MOVER', 'S'
                    elif siguiente[1] < self.p.capitán_pos[1]:
                        if self.es_movimiento_seguro('O'):
                            return 'MOVER', 'O'
                    elif siguiente[1] > self.p.capitán_pos[1]:
                        if self.es_movimiento_seguro('E'):
                            return 'MOVER', 'E'
            except ValueError:
                # No estamos en el camino guardado, continuar con otras estrategias
                pass

        # Si tenemos a Kurtz y estamos ADYACENTE a la salida, intentar entrar
        if self.p.con_kurtz:
            vecinos = self.p.vecinos_de(self.p.capitán_pos)
            for v in vecinos:
                if v == self.p.salida:
                    # Calcular dirección hacia la salida
                    if v[0] < self.p.capitán_pos[0]:
                        if self.es_movimiento_seguro('N'):
                            return 'MOVER', 'N'
                    elif v[0] > self.p.capitán_pos[0]:
                        if self.es_movimiento_seguro('S'):
                            return 'MOVER', 'S'
                    elif v[1] < self.p.capitán_pos[1]:
                        if self.es_movimiento_seguro('O'):
                            return 'MOVER', 'O'
                    elif v[1] > self.p.capitán_pos[1]:
                        if self.es_movimiento_seguro('E'):
                            return 'MOVER', 'E'

        # Obtener perceptos actuales
        percepciones = self.p.que_siento()
        # print(f"[AGENTE] Perceptos actuales: {percepciones}")

        # ESTRATEGIA 1: Usar granada si hay ronquido
        # Esto parece buena idea, pero a veces falla espectacularmente
        if ('ronquido' in percepciones and
            self.p.tengo_granada and
                self.p.soldado_vivo):

            # print("[AGENTE] Estrategia 1: Considerando granada (hay ronquido)")
            vecinos = self.p.vecinos_de(self.p.capitán_pos)
            posibles_soldados = []

            for v in vecinos:
                if not self.conocimiento[v]['visitada']:
                    posibles_soldados.append(v)

            if posibles_soldados:
                # Elegir uno (evitar Kurtz si es posible)
                for v in posibles_soldados:
                    if v != self.p.kurtz:
                        if v[0] < self.p.capitán_pos[0]:
                            # print(f"[AGENTE] Tirando granada al N (hacia {v})")
                            return 'GRANADA', 'N'
                        elif v[0] > self.p.capitán_pos[0]:
                            # print(f"[AGENTE] Tirando granada al S (hacia {v})")
                            return 'GRANADA', 'S'
                        elif v[1] < self.p.capitán_pos[1]:
                            # print(f"[AGENTE] Tirando granada al O (hacia {v})")
                            return 'GRANADA', 'O'
                        elif v[1] > self.p.capitán_pos[1]:
                            # print(f"[AGENTE] Tirando granada al E (hacia {v})")
                            return 'GRANADA', 'E'

                # Si todos podrían ser Kurtz, tirar al primero (arriesgado)
                v = posibles_soldados[0]
                # print(f"[AGENTE] ¡CUIDADO! Podría ser Kurtz en {v}, pero tiro igual")
                if v[0] < self.p.capitán_pos[0]:
                    return 'GRANADA', 'N'
                elif v[0] > self.p.capitán_pos[0]:
                    return 'GRANADA', 'S'
                elif v[1] < self.p.capitán_pos[1]:
                    return 'GRANADA', 'O'
                elif v[1] > self.p.capitán_pos[1]:
                    return 'GRANADA', 'E'

        # ESTRATEGIA 1.5: Si tenemos a Kurtz, buscar salida activamente
        if self.p.con_kurtz:
            # print("[AGENTE] Estrategia 1.5: Buscando salida (tengo a Kurtz)")

            # Primero intentar ir directamente a la salida si la conocemos
            if hasattr(self.p, 'salida') and self.p.salida:
                movimiento = self.calcular_movimiento_seguro_hacia(
                    self.p.salida)
                if movimiento:
                    return movimiento

            # Buscar celdas con resplandor primero
            objetivo_resplandor = self.encontrar_celda_con_resplandor()
            if objetivo_resplandor:
                # print(f"[AGENTE] Objetivo: celda con resplandor {objetivo_resplandor}")
                movimiento = self.calcular_movimiento_seguro_hacia(
                    objetivo_resplandor)
                if movimiento:
                    return movimiento

            # Si no hay resplandor, explorar sistemáticamente
            # print("[AGENTE] No hay resplandor detectado, explorando...")

        # ESTRATEGIA 2: Buscar celdas seguras NO visitadas
        # print("[AGENTE] Estrategia 2: Buscando celdas seguras no visitadas")
        celdas_seguras_no_visitadas = []
        for celda in self.p.celdas_seguras:
            if not self.conocimiento[celda]['visitada']:
                celdas_seguras_no_visitadas.append(celda)

        if celdas_seguras_no_visitadas:
            # print(f"[AGENTE] Celdas seguras no visitadas: {celdas_seguras_no_visitadas}")
            # Ordenar por cercanía
            pos_actual = self.p.capitán_pos
            celdas_seguras_no_visitadas.sort(
                key=lambda c: abs(c[0]-pos_actual[0]) + abs(c[1]-pos_actual[1])
            )

            for objetivo in celdas_seguras_no_visitadas:
                movimiento = self.calcular_movimiento_seguro_hacia(objetivo)
                if movimiento:
                    # print(f"[AGENTE] Movimiento hacia celda segura {objetivo}: {movimiento}")
                    return movimiento

        # ESTRATEGIA 3: Si hay un objetivo actual, intentar llegar a él
        if self.objetivo_actual:
            # print(f"[AGENTE] Estrategia 3: Intentando llegar a objetivo {self.objetivo_actual}")
            movimiento = self.calcular_movimiento_seguro_hacia(
                self.objetivo_actual)
            if movimiento:
                # print(f"[AGENTE] Movimiento hacia objetivo: {movimiento}")
                return movimiento
            else:
                # print("[AGENTE] No puedo llegar al objetivo, limpiándolo")
                self.objetivo_actual = None

        # ESTRATEGIA 4: Establecer nuevo objetivo (celda no visitada cercana)
        # print("[AGENTE] Estrategia 4: Estableciendo nuevo objetivo")
        nuevo_objetivo = self.encontrar_celda_no_visitada_cercana()
        if nuevo_objetivo:
            # print(f"[AGENTE] Nuevo objetivo: {nuevo_objetivo}")
            self.objetivo_actual = nuevo_objetivo
            movimiento = self.calcular_movimiento_seguro_hacia(nuevo_objetivo)
            if movimiento:
                return movimiento

        # ESTRATEGIA 5: Retroceder a posición anterior segura
        # Cuando no sabes qué hacer, retrocede
        if len(self.camino) > 1:
            # print("[AGENTE] Estrategia 5: Retrocediendo...")
            for i in range(len(self.camino)-2, -1, -1):
                pos_anterior = self.camino[i]
                movimiento = self.calcular_movimiento_seguro_hacia(
                    pos_anterior)
                if movimiento:
                    # print(f"[AGENTE] Retrocediendo a {pos_anterior}: {movimiento}")
                    return movimiento

        # ESTRATEGIA 6: Movimiento conservador
        # print("[AGENTE] Estrategia 6: Movimiento conservador")
        direcciones_seguras = []
        for dir in ['N', 'S', 'O', 'E']:
            if self.es_movimiento_seguro(dir):
                nueva_pos = self.calcular_nueva_posicion(dir)
                if nueva_pos and nueva_pos not in self.camino[-3:]:
                    direcciones_seguras.append(dir)

        if direcciones_seguras:
            # print(f"[AGENTE] Direcciones seguras: {direcciones_seguras}")
            # Preferir direcciones que exploren zonas nuevas
            for dir in direcciones_seguras:
                nueva_pos = self.calcular_nueva_posicion(dir)
                if not self.conocimiento[nueva_pos]['visitada']:
                    # print(f"[AGENTE] Dirección {dir} lleva a celda no visitada {nueva_pos}")
                    return 'MOVER', dir

            # Si todas llevan a visitadas, elegir una al azar (qué más da)
            dir_elegida = random.choice(direcciones_seguras)
            # print(f"[AGENTE] Todas direcciones llevan a visitadas. Elegida al azar: {dir_elegida}")
            return 'MOVER', dir_elegida

        # ESTRATEGIA 7: Si estamos en un bucle, tomar riesgos controlados
        # Desesperación nivel: máximo
        if self.detectar_bucle():
            print("  [AGENTE] ¡BUCLE DETECTADO! Estrategia especial activada")

            # Si tenemos a Kurtz, priorizar buscar salida
            if self.p.con_kurtz:
                movimiento_especial = self.evitar_bucle_y_buscar_salida()
                if movimiento_especial:
                    return movimiento_especial

            vecinos = self.p.vecinos_de(self.p.capitán_pos)
            vecinos_no_visitados = []

            for v in vecinos:
                if not self.conocimiento[v]['visitada']:
                    vecinos_no_visitados.append(v)

            if vecinos_no_visitados:
                # print(f"[AGENTE] Vecinos no visitados desde bucle: {vecinos_no_visitados}")
                # Elegir el vecino con menor riesgo
                mejor_vecino = None
                menor_riesgo = float('inf')

                for v in vecinos_no_visitados:
                    riesgo = (self.conocimiento[v]['riesgo_precipicio'] +
                              self.conocimiento[v]['riesgo_soldado'])
                    # print(f"[AGENTE] Vecino {v}: riesgo {riesgo}")
                    if riesgo < menor_riesgo:
                        menor_riesgo = riesgo
                        mejor_vecino = v

                if mejor_vecino:
                    # print(f"[AGENTE] Mejor vecino para escape: {mejor_vecino} (riesgo: {menor_riesgo})")
                    if mejor_vecino[0] < self.p.capitán_pos[0]:
                        if self.es_movimiento_seguro('N'):
                            return 'MOVER', 'N'
                    elif mejor_vecino[0] > self.p.capitán_pos[0]:
                        if self.es_movimiento_seguro('S'):
                            return 'MOVER', 'S'
                    elif mejor_vecino[1] < self.p.capitán_pos[1]:
                        if self.es_movimiento_seguro('O'):
                            return 'MOVER', 'O'
                    elif mejor_vecino[1] > self.p.capitán_pos[1]:
                        if self.es_movimiento_seguro('E'):
                            return 'MOVER', 'E'

        # ESTRATEGIA 8: Arriesgarse solo si no hay peligro inmediato
        # print("[AGENTE] Estrategia 8: Arriesgarse (sin peligros inmediatos)")
        if 'brisa' not in percepciones and 'ronquido' not in percepciones:
            vecinos = self.p.vecinos_de(self.p.capitán_pos)
            for v in vecinos:
                if not self.conocimiento[v]['visitada']:
                    if v[0] < self.p.capitán_pos[0]:
                        if self.es_movimiento_seguro('N'):
                            # print(f"[AGENTE] Arriesgando al N hacia {v}")
                            return 'MOVER', 'N'
                    elif v[0] > self.p.capitán_pos[0]:
                        if self.es_movimiento_seguro('S'):
                            # print(f"[AGENTE] Arriesgando al S hacia {v}")
                            return 'MOVER', 'S'
                    elif v[1] < self.p.capitán_pos[1]:
                        if self.es_movimiento_seguro('O'):
                            # print(f"[AGENTE] Arriesgando al O hacia {v}")
                            return 'MOVER', 'O'
                    elif v[1] > self.p.capitán_pos[1]:
                        if self.es_movimiento_seguro('E'):
                            # print(f"[AGENTE] Arriesgando al E hacia {v}")
                            return 'MOVER', 'E'

        # ESTRATEGIA 9: Movimiento de último recurso
        # Cuando todo lo demás falla, prueba cosas al azar
        print("  [AGENTE] ¡ÚLTIMO RECURSO! Probando cualquier movimiento")
        for dir in ['N', 'S', 'O', 'E']:
            nueva_pos = self.calcular_nueva_posicion(dir)
            if nueva_pos:
                # Solo evitar precipicios y soldados reales (lo básico)
                if (nueva_pos not in self.p.precipicios and
                        (not self.p.soldado_vivo or nueva_pos != self.p.soldado)):
                    # print(f"[AGENTE] Último recurso: {dir} hacia {nueva_pos}")
                    return 'MOVER', dir

        # ESTRATEGIA 10: Rendirse
        # A veces hay que saber cuándo parar
        print("  [AGENTE] No encuentro opciones. Me rindo.")
        return 'RENDIRSE', None

    def evitar_bucle_y_buscar_salida(self):
        """Estrategia especial cuando detecta bucle y tiene a Kurtz"""
        if not self.p.con_kurtz:
            return None

        # NUEVO: Si tenemos camino a salida guardado, usarlo
        if self.camino_a_salida:
            # print(f"[AGENTE] Bucle con Kurtz - usando camino guardado a salida")
            try:
                indice_actual = self.camino_a_salida.index(self.p.capitán_pos)
                if indice_actual < len(self.camino_a_salida) - 1:
                    siguiente = self.camino_a_salida[indice_actual + 1]
                    if siguiente[0] < self.p.capitán_pos[0]:
                        if self.es_movimiento_seguro('N'):
                            return 'MOVER', 'N'
                    elif siguiente[0] > self.p.capitán_pos[0]:
                        if self.es_movimiento_seguro('S'):
                            return 'MOVER', 'S'
                    elif siguiente[1] < self.p.capitán_pos[1]:
                        if self.es_movimiento_seguro('O'):
                            return 'MOVER', 'O'
                    elif siguiente[1] > self.p.capitán_pos[1]:
                        if self.es_movimiento_seguro('E'):
                            return 'MOVER', 'E'
            except ValueError:
                pass

        # Buscar cualquier camino a celdas no visitadas
        vecinos = self.p.vecinos_de(self.p.capitán_pos)
        for v in vecinos:
            if not self.conocimiento[v]['visitada']:
                if v[0] < self.p.capitán_pos[0]:
                    if self.es_movimiento_seguro('N'):
                        return 'MOVER', 'N'
                elif v[0] > self.p.capitán_pos[0]:
                    if self.es_movimiento_seguro('S'):
                        return 'MOVER', 'S'
                elif v[1] < self.p.capitán_pos[1]:
                    if self.es_movimiento_seguro('O'):
                        return 'MOVER', 'O'
                elif v[1] > self.p.capitán_pos[1]:
                    if self.es_movimiento_seguro('E'):
                        return 'MOVER', 'E'

        # Si no hay celdas no visitadas, intentar retroceder
        if len(self.camino) > 2:
            pos_anterior = self.camino[-2]
            if pos_anterior[0] < self.p.capitán_pos[0]:
                if self.es_movimiento_seguro('N'):
                    return 'MOVER', 'N'
            elif pos_anterior[0] > self.p.capitán_pos[0]:
                if self.es_movimiento_seguro('S'):
                    return 'MOVER', 'S'
            elif pos_anterior[1] < self.p.capitán_pos[1]:
                if self.es_movimiento_seguro('O'):
                    return 'MOVER', 'O'
            elif pos_anterior[1] > self.p.capitán_pos[1]:
                if self.es_movimiento_seguro('E'):
                    return 'MOVER', 'E'

        return None

    def calcular_nueva_posicion(self, direccion):
        """Calcula la nueva posición dado un movimiento"""
        x, y = self.p.capitán_pos
        if direccion == 'N' and x > 0:
            return (x-1, y)
        elif direccion == 'S' and x < self.p.n-1:
            return (x+1, y)
        elif direccion == 'O' and y > 0:
            return (x, y-1)
        elif direccion == 'E' and y < self.p.n-1:
            return (x, y+1)
        return None

    def calcular_movimiento_seguro_hacia(self, objetivo):
        """Calcula movimiento seguro hacia un objetivo"""
        # print(f"[AGENTE] Calculando camino seguro hacia {objetivo}")
        inicio = self.p.capitán_pos

        # Si el objetivo es adyacente y seguro, ir directamente
        vecinos = self.p.vecinos_de(inicio)
        if objetivo in vecinos and self.es_movimiento_seguro_hacia(objetivo):
            # print(f"[AGENTE] Objetivo {objetivo} es adyacente y seguro")
            if objetivo[0] < inicio[0]:
                return 'MOVER', 'N'
            elif objetivo[0] > inicio[0]:
                return 'MOVER', 'S'
            elif objetivo[1] < inicio[1]:
                return 'MOVER', 'O'
            elif objetivo[1] > inicio[1]:
                return 'MOVER', 'E'

        # Búsqueda más amplia (BFS simple)
        # print(f"[AGENTE] BFS desde {inicio} hacia {objetivo}")
        cola = deque()
        cola.append((inicio, []))
        visitados = set([inicio])

        while cola:
            actual, camino = cola.popleft()

            if actual == objetivo:
                if camino:
                    primer_paso = camino[0]
                    if self.es_movimiento_seguro_hacia(primer_paso):
                        # print(f"[AGENTE] Camino encontrado: {camino}, primer paso: {primer_paso}")
                        if primer_paso[0] < inicio[0]:
                            return 'MOVER', 'N'
                        elif primer_paso[0] > inicio[0]:
                            return 'MOVER', 'S'
                        elif primer_paso[1] < inicio[1]:
                            return 'MOVER', 'O'
                        elif primer_paso[1] > inicio[1]:
                            return 'MOVER', 'E'

            for vecino in self.p.vecinos_de(actual):
                if vecino not in visitados:
                    # NUEVO: Si estamos buscando salida y este vecino está en el camino a salida, priorizarlo
                    prioridad_extra = 0
                    if self.buscando_salida and self.camino_a_salida and vecino in self.camino_a_salida:
                        prioridad_extra = 10  # Prioridad alta para celdas en camino a salida

                    # Permitir celdas seguras o con bajo riesgo si estamos desesperados
                    if (self.conocimiento[vecino]['segura'] or
                        vecino in self.p.celdas_seguras or
                        (self.detectar_bucle() and
                         self.conocimiento[vecino]['riesgo_precipicio'] <= 1 and
                         self.conocimiento[vecino]['riesgo_soldado'] <= 1) or
                            prioridad_extra > 0):
                        visitados.add(vecino)
                        nuevo_camino = camino + [vecino]
                        cola.append((vecino, nuevo_camino))

        # print(f"[AGENTE] No se encontró camino seguro hacia {objetivo}")
        return None

    def es_movimiento_seguro_hacia(self, celda):
        """Verifica si moverse hacia una celda específica es seguro"""
        # Esto es básicamente un wrapper. No se xq está separado.
        x_act, y_act = self.p.capitán_pos
        x_obj, y_obj = celda

        if x_obj < x_act:
            return self.es_movimiento_seguro('N')
        elif x_obj > x_act:
            return self.es_movimiento_seguro('S')
        elif y_obj < y_act:
            return self.es_movimiento_seguro('O')
        elif y_obj > y_act:
            return self.es_movimiento_seguro('E')

        return False

    def registrar_movimiento(self, nueva_pos):
        """Registra el movimiento realizado"""
        # print(f"[AGENTE] Registrando movimiento a {nueva_pos}")
        if not self.camino or nueva_pos != self.camino[-1]:
            self.camino.append(nueva_pos)

        # Limitar longitud del camino (para no consumir toda la RAM -ejem ejem FUSO-)
        if len(self.camino) > 50:
            # print(f"[AGENTE] Recortando camino de {len(self.camino)} a 30 elementos")
            self.camino = self.camino[-30:]

        # Actualizar pila de exploración
        vecinos = self.p.vecinos_de(nueva_pos)
        for v in vecinos:
            if v not in self.stack and not self.conocimiento[v]['visitada']:
                self.stack.append(v)

        # Limpiar contadores de intentos periódicamente
        if len(self.camino) % 10 == 0:
            # print("[AGENTE] Limpiando contadores de intentos...")
            for celda in list(self.intentos_movimiento.keys()):
                if self.intentos_movimiento[celda] > 0:
                    self.intentos_movimiento[celda] -= 1

# ============================================================================
# MODO AUTOMÁTICO INTELIGENTE (MEJORADO)
# ============================================================================


def modo_auto_inteligente():
    """Modo automático con exploración sistemática"""
    # Esta función es larga y complicada. Buena suerte.
    print("\n" + ">"*30)
    print("MODO: AUTOMÁTICO INTELIGENTE (MEJORADO)")
    print(">"*30)
    print("\nEl agente explorará sistemáticamente.")
    print("Evitará brisa (precipicios) y ronquidos (soldados).")
    print("(En teoría... en práctica a veces se mata igual)")
    print("¡PERO AHORA CON MENOS BUCLES INFINITOS! (eso espero)")
    print("¡AHORA TAMBIÉN GUARDA EL CAMINO A LA SALIDA!")
    input("(Enter para comenzar...)")

    palacio = Palacio()
    agente = AgenteExplorador(palacio)

    print("\nIniciando exploración inteligente...")
    print("El agente evitará moverse hacia peligros.")
    print("(O eso dice, luego veremos)")
    print()

    max_pasos = 200  # Para que no se eternice
    paso = 0
    exito = False
    resultado = ""

    # Bucle principal del agente
    while paso < max_pasos and not exito:
        paso += 1
        print(f"\n" + "="*60)
        print(f"PASO {paso}")
        print(
            f"Posición: ({palacio.capitán_pos[0]+1},{palacio.capitán_pos[1]+1})")
        print("="*60)

        # Mostrar mapa
        palacio.mostrar_mapa_conocido()

        # Obtener y mostrar perceptos
        percepciones = palacio.que_siento()
        if percepciones:
            print("Perceptos:", ", ".join(percepciones))
            if 'brisa' in percepciones:
                print("¡ATENCIÓN! Brisa detectada - Precipicio cerca")
            if 'ronquido' in percepciones and palacio.soldado_vivo:
                print("¡PELIGRO! Ronquido detectado - Soldado cerca")
            if 'brisa' in percepciones and 'ronquido' in percepciones:
                print("¡DOBLE PELIGRO! Brisa Y ronquido - Extremadamente peligroso")
            if 'resplandor_fuerte' in percepciones:
                print("¡RESPLANDOR FUERTE! Estás en la salida")
            elif 'resplandor_suave' in percepciones:
                print("Resplandor suave - Salida cerca")
        else:
            print("Perceptos: (nada especial)")
            print("(¿O será que no estoy prestando atención?)")

        # Actualizar conocimiento del agente
        agente.actualizar_conocimiento(percepciones)

        # Decidir acción (aquí es donde la "inteligencia" entra en juego)
        accion, parametro = agente.decidir_siguiente_movimiento()

        if accion == 'SALIR':
            print("\n[AGENTE] Intenta salir...")
            ok, mensaje = palacio.intentar_salir()
            print(f"\n{mensaje}")
            resultado = mensaje
            exito = True

        elif accion == 'MOVER':
            print(f"\n[AGENTE] Decisión: Mover {parametro}")
            ok, mensaje = palacio.mover(parametro)
            print(f"Resultado: {mensaje}")

            if ok:
                agente.registrar_movimiento(palacio.capitán_pos)
                agente.marcar_visitada(palacio.capitán_pos)

                if "¡ENCONTRASTE A KURTZ!" in mensaje:
                    print("\n" + "="*50)
                    print("¡HAS ENCONTRADO AL CORONEL KURTZ!")
                    print("Ahora buscará la salida más agresivamente.")
                    print("="*50)

            else:
                print("\n¡Fallo! El agente murió.")
                resultado = mensaje
                break

        elif accion == 'GRANADA':
            print(f"\n[AGENTE] Decisión: Tirar granada al {parametro}")
            ok, mensaje = palacio.tirar_granada(parametro)
            print(f"Resultado: {mensaje}")

            if ok and "Soldado eliminado" in mensaje:
                print("¡Soldado eliminado! El camino está más seguro.")
                agente.actualizar_conocimiento(palacio.que_siento())

        elif accion == 'RENDIRSE':
            print("\nEl agente se rinde. No encuentra camino seguro.")
            resultado = "Agente se rindió - atrapado"
            break

        else:
            print(f"\n[ERROR] Acción desconocida: {accion}")
            break

        time.sleep(0.05)  # Reducido para velocidad (pero que se vea)

    # Resultado final (aquí vemos si aprobamos o no)
    print("\n" + "="*60)
    print("RESULTADO FINAL:")
    print("="*60)
    print(f"Pasos totales: {palacio.pasos}")
    print(f"Kurtz encontrado: {'SÍ' if palacio.con_kurtz else 'NO'}")
    print(f"Soldado eliminado: {'SÍ' if not palacio.soldado_vivo else 'NO'}")
    print(f"Granada usada: {'SÍ' if not palacio.tengo_granada else 'NO'}")

    if palacio.con_kurtz and palacio.capitán_pos == palacio.salida:
        print("¡MISIÓN COMPLETADA CON ÉXITO!")
    elif palacio.con_kurtz:
        print("Encontró a Kurtz pero no llegó a la salida")
    else:
        print("No encontró a Kurtz")

    # Mostrar información sobre el camino a salida guardado
    if hasattr(agente, 'camino_a_salida') and agente.camino_a_salida:
        print(
            f"Camino a salida guardado: {len(agente.camino_a_salida)} celdas")
    if hasattr(agente, 'salida_encontrada') and agente.salida_encontrada:
        print("Salida encontrada durante exploración: SÍ")
    else:
        print("Salida encontrada durante exploración: NO")

    print("="*60)

    # Mostrar mapas finales (para análisis post-mortem)
    print("\nMapa final (lo que descubrió el agente):")
    palacio.mostrar_mapa_conocido()

    print("\nMapa completo real (para comparar):")
    palacio.mostrar_mapa_completo()

    # Estadísticas (para la memoria)
    print("\n" + "-"*40)
    print("ESTADÍSTICAS DEL AGENTE:")
    print(
        f"Celdas exploradas: {len(palacio.celdas_visitadas)}/{palacio.n*palacio.n}")
    print(f"Celdas seguras identificadas: {len(palacio.celdas_seguras)}")
    print(f"Longitud del camino recorrido: {len(agente.camino)}")
    print(f"Celdas con brisa detectada: {len(agente.celdas_con_brisa)}")
    print(f"Celdas con ronquido detectado: {len(agente.celdas_con_ronquido)}")
    print(f"Buscando salida: {'SÍ' if agente.buscando_salida else 'NO'}")
    print(f"Salida encontrada: {'SÍ' if agente.salida_encontrada else 'NO'}")
    print(
        f"Camino a salida guardado: {'SÍ' if agente.camino_a_salida else 'NO'}")
    if agente.camino_a_salida:
        print(f"Longitud camino a salida: {len(agente.camino_a_salida)}")
    print("-"*40)

# ============================================================================
# MODO JUGADOR (MANUAL) - Sin cambios
# ============================================================================

def modo_jugador():
    """Modo donde juego yo"""
    # Este modo es más divertido porque tú controlas
    print("\n" + ">"*30)
    print("MODO: JUGADOR HUMANO")
    print(">"*30)
    print("\nVoy a controlar al capitán yo mismo.")
    input("(Enter para empezar...)")

    mi_palacio = Palacio()

    print("\nCONTROLES RÁPIDOS:")
    print("N/W - Norte  |  S - Sur  |  O/A - Oeste  |  E/D - Este")
    print("G - Granada  |  X - SALIR")
    print("I - Info  |  C - Mapa completo (cheat)  |  Q - Rendirse")
    print()
    print("OBJETIVO: Encontrar a Kurtz, luego ir a la salida y usar 'X'")
    print()

    jugando = True
    while jugando:
        print("\n" + "="*60)
        print(f"TURNO #{mi_palacio.pasos + 1}")
        print("="*60)

        mi_palacio.mostrar_mapa_conocido()

        sensaciones = mi_palacio.que_siento()
        if sensaciones:
            print("\nPERCEPCIONES:")
            for s in sensaciones:
                if "pared" in s:
                    print(f"  • {s.replace('_', ' ')}")
                elif "resplandor_fuerte" in s:
                    print("  • ¡RESPLANDOR FUERTE! (Estás EN la salida)")
                elif "resplandor_suave" in s:
                    print("  • Resplandor suave (salida cerca)")
                else:
                    print(f"  • {s}")
        else:
            print("\nNo siento nada especial.")
            print("(¿O será que no estoy prestando atención?)")

        accion = input("\n¿Qué hago? ").upper()

        if accion in ['N', 'W']:
            ok, msg = mi_palacio.mover('N')
            print(f"\n{msg}")
            if not ok:
                jugando = False
                print("\n¡GAME OVER!")

        elif accion == 'S':
            ok, msg = mi_palacio.mover('S')
            print(f"\n{msg}")
            if not ok:
                jugando = False
                print("\n¡GAME OVER!")

        elif accion in ['O', 'A']:
            ok, msg = mi_palacio.mover('O')
            print(f"\n{msg}")
            if not ok:
                jugando = False
                print("\n¡GAME OVER!")

        elif accion in ['E', 'D']:
            ok, msg = mi_palacio.mover('E')
            print(f"\n{msg}")
            if not ok:
                jugando = False
                print("\n¡GAME OVER!")

        elif accion == 'G':
            if mi_palacio.tengo_granada:
                dir_g = input(
                    "¿Hacia dónde tiro la granada? (N/S/O/E): ").upper()
                if dir_g in ['N', 'S', 'O', 'E']:
                    ok, msg = mi_palacio.tirar_granada(dir_g)
                    print(msg)
                    if "Soldado eliminado" in msg:
                        print("(¡Buen tiro!)")
                    elif "Kurtz evita" in msg:
                        print("(Uf, por poco matas a Kurtz...)")
                    else:
                        print("(Granada desperdiciada...)")
                else:
                    print("Dirección no válida.")
                    mi_palacio.tengo_granada = False
            else:
                print("Ya no tengo granadas.")

        elif accion == 'X':
            ok, msg = mi_palacio.intentar_salir()
            print(f"\n{msg}")
            if ok:
                jugando = False
                print("\n¡FELICIDADES!")
            else:
                print("(Sigue intentándolo...)")

        elif accion == 'I':
            print("\n" + "="*40)
            print("INFORMACIÓN:")
            print("="*40)
            print(f"Pasos: {mi_palacio.pasos}")
            print(
                f"Kurtz: {'CON NOSOTROS' if mi_palacio.con_kurtz else 'NO ENCONTRADO'}")
            print(
                f"Soldado: {'VIVO' if mi_palacio.soldado_vivo else 'MUERTO'}")
            print(
                f"Granada: {'DISPONIBLE' if mi_palacio.tengo_granada else 'USADA'}")
            print(f"Celdas visitadas: {len(mi_palacio.celdas_visitadas)}")
            print("="*40)
            input("(Enter para continuar...)")
            continue

        elif accion == 'C':
            print("\n(MAPA COMPLETO - modo cheat)")
            mi_palacio.mostrar_mapa_completo()
            input("(Enter para continuar...)")
            continue

        elif accion == 'Q':
            print("\nTe rindes...")
            print("\nMapa completo real:")
            mi_palacio.mostrar_mapa_completo()
            jugando = False

        else:
            print("Comando no reconocido.")
            print("(Lee las instrucciones, por favor)")
            continue

        time.sleep(0.1)

        if "¡MISIÓN CUMPLIDA!" in msg:
            print("\n¡¡¡VICTORIA!!!")
            print("\nMapa final completo:")
            mi_palacio.mostrar_mapa_completo()
            jugando = False

# ============================================================================
# PROGRAMA PRINCIPAL
# ============================================================================

def main():
    """Función principal del juego"""
    # Esto es lo primero que se ejecuta. No tocar mucho.

    print("\n" + "▓"*40)
    print("▓         BUSCANDO AL CORONEL KURTZ         ▓")
    print("▓           Proyecto FIA - Parte 1          ▓")
    print("▓"*40)
    print()
    print("Código por: Claudia Maria Lopez Bombin")
    print("Asignatura: Fundamentos de IA")
    print()

    while True:
        print("\n" + "-"*40)
        print("MENÚ PRINCIPAL - ELIGE MODO DE JUEGO")
        print("-"*40)
        print("1. Jugar yo mismo (modo manual)")
        print("2. Ver al agente inteligente MEJORADO (exploración sistemática)")
        print("3. Salir (rendirse)")
        print("-"*40)
        print("NOTA: El modo 2 ahora tiene menos bucles infinitos (creo)")
        print("      ¡Y GUARDA EL CAMINO A LA SALIDA!")
        print("-"*40)

        try:
            op = input("\nElige (1-3): ").strip()

            if op == '1':
                modo_jugador()
            elif op == '2':
                modo_auto_inteligente()
            elif op == '3':
                print("\n¡Gracias por jugar! Hasta la próxima.")
                break
            else:
                print("Opción no válida. Intenta de nuevo.")
                print("(Es 1, 2 o 3. No es tan difícil)")

        except KeyboardInterrupt:
            print("\n\nJuego interrumpido.")
            print("(Ctrl+C, el enemigo de todo programador)")
            break
        except Exception as e:
            print(f"\nError inesperado: {e}")
            print("(Seguro que fue algo que toqué y no debía)")
            time.sleep(1)

# ============================================================================
# EJECUCIÓN
# ============================================================================

if __name__ == "__main__":
    # Esto se ejecuta solo si el archivo se corre directamente
    # Si se importa como módulo, no se ejecuta
    # (Cosas básicas de Python, pero por si acaso)

    try:
        import random
        import time
        # print("[INICIO] Módulos importados correctamente")
    except ImportError as e:
        print(f"ERROR: No se puede importar una librería necesaria: {e}")
        print("(Instala Python bien, por favor)")
        sys.exit(1)

    # Ejecutar el juego
    # print("[INICIO] Ejecutando main()...")
    main()

    # Créditos finales (por si llegais hasta aquí)
    print("\n" + "-"*40)
    print("CRÉDITOS:")
    print("- Implementación completa del proyecto FIA Parte 1")
    print("- Agente inteligente que evita brisa y ronquidos")
    print("- Modo manual y automático")
    print("- AHORA CON MENOS BUCLES INFINITOS (eso espero)")
    print("- AHORA GUARDA CAMINO A SALIDA CUANDO LA ENCUENTRA")
    print("- Para Fundamentos de IA 25-26")
    print("- Código con comentarios explicativos (y algún que otro desahogo fruto de mi desesperacion)")
    print("- No patrocinado por Pantene (a la perdida de pelo por estres me remito)")
    print("-"*40)
    print("\nFIN DEL PROGRAMA")
    print("(Si hay errores, fue el compilador, no yo... probablemente)")
