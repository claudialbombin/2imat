class AFD:
    def __init__(self, estados, alfabeto, transiciones, estado_inicial, estados_finales):
        self.estados = estados
        self.alfabeto = alfabeto
        self.transiciones = transiciones # Diccionario de diccionarios: {estado: {letra: siguiente_estado}} OJO: hay que incluir todos los simbolos del diccionario y sus transiciones(si no no funciona xd)
        self.estado_inicial = estado_inicial
        self.estados_finales = estados_finales

    def check_cadena(self, cadena_lower): # Funcion para checkear que la cadena solo este compuesta de simbolos que este en el alfabeto
        # No necesito convertir la cadena lower porque ya se la paso en minusculas
        for i in cadena_lower:
            if i not in self.alfabeto:
                print(f"La cadena '{cadena_lower}' contiene símbolos no válidos.")  # Mantengo tu comentario original
                return False
        return True

    def procesar_cadena(self, cadena):
        cadena_lower = cadena.lower()  # Convertir la cadena a minúsculas por si alguna de las letras de ajo estuviese en mayuscula
        cadena_ok = self.check_cadena(cadena_lower)
        if not cadena_ok:
            return False
            # Si la cadena contiene simbolos no validos, devolvemos False y no procesamos la cadena

            # Considero que es mas importante que la cadena sea valida a que la cadena a buscar este dentro de 
            # Por ejemplo, si la cadena a buscar es 'ajo' y el texto es 'ajoaj0', aunque la cadena 'ajo' esta en el texto, 
            # la cadena no es valida porque contiene un simbolo no valido (el 0), salta un error y automaticamente es False y no la analiza.
        estado_actual = self.estado_inicial
        for simbolo in cadena_lower:
            # Si no existe la transición, volvemos al estado inicial
            estado_actual = self.transiciones[estado_actual].get(simbolo, self.estado_inicial)
            if estado_actual in self.estados_finales:
                return True  # Si llegamos al estado final, devolvemos True
        return estado_actual in self.estados_finales

# Un AFD que acepta cadenas que conjetngan -ajo- 
estados = {'q0', 'q1', 'q2', 'fin'}
alfabeto = set("abcdefghijklmnopqrstuvwxyz0123456789 ")

# Transiciones: {estado_actual: {símbolo_entrada: siguiente_estado}}
transiciones = {}

# q0
transiciones['q0'] = {}
for c in alfabeto:
    if c == 'a':
        estado = 'q1'
    else:
        estado = 'q0'
    transiciones['q0'][c] = estado

# q1
transiciones['q1'] = {}
for c in alfabeto:
    if c == 'j':
        estado = 'q2'
    else:
        estado = 'q0'
    transiciones['q1'][c] = estado

# q2
transiciones['q2'] = {}
for c in alfabeto:
    if c == 'o':
        estado = 'fin'
    else:
        estado = 'q0'
    transiciones['q2'][c] = estado

# fin
transiciones['fin'] = {}
for c in alfabeto:
    if c == 'a':
        estado = 'q1'
    else:
        estado = 'q0'
    transiciones['fin'][c] = estado

estado_inicial = 'q0'
estados_finales = {'fin'}

# Crear el autómata
mi_afd = AFD(estados, alfabeto, transiciones, estado_inicial, estados_finales)

# Probar con algunas cadenas
# print(f"Cadena 'estar': {mi_afd.procesar_cadena('estar')}") # Debería ser False 
# print(f"Cadena 'majo': {mi_afd.procesar_cadena('majo')}") # Debería ser True
# print(f"Cadena 'maja': {mi_afd.procesar_cadena('maja')}") # Debería ser False

# Probemos ahora con una cadena de entrada por terminal
cadena = str(input("Introduce una cadena para verificar si es aceptada por el AFD: "))
# mi_afd.procesar_cadena(cadena)
print(f"Cadena '{cadena}': {mi_afd.procesar_cadena(cadena)}")