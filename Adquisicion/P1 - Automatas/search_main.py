class AFD:
	def __init__(self, estados, alfabeto, transiciones, estado_inicial, estados_finales, patron):
		self.estados = estados
		self.alfabeto = alfabeto
		self.transiciones = transiciones
		self.estado_inicial = estado_inicial
		self.estados_finales = estados_finales
		self.patron = patron

	def check_palabra(self, cadena_lower):
		# Verifica que la cadena completa solo contiene símbolos del alfabeto permitido.
		# Si encuentra un símbolo NO válido, imprime un mensaje de error y devuelve False.

		for c in cadena_lower:
			if c not in self.alfabeto:
				print(f"Error: símbolo no válido '{c}' en el texto.")
				return False
		return True

	def procesar_texto(self, texto):
		# Procesa el texto como una cadena continua (sin dividir en palabras).
		# Devuelve:
		#  - número de ocurrencias del patrón en el texto (incluyendo solapadas), o
		#  - 0 si el texto contiene símbolos no válidos.
		  
		texto_lower = texto.lower()

		# Validamos que el texto solo tenga símbolos válidos
		valido = self.check_palabra(texto_lower)
		if not valido:
			return 0

		ocurrencias = 0
		estado_actual = self.estado_inicial

		# Recorremos todo el texto carácter por carácter
		for simbolo in texto_lower:
			estado_actual = self.transiciones[estado_actual][simbolo]
			if estado_actual in self.estados_finales:
				ocurrencias += 1

		return ocurrencias

# Elementos para construir el AFD

# Alfabeto: letras minúsculas + dígitos + espacio
alfabeto = set("abcdefghijklmnopqrstuvwxyz0123456789 ")

# Pedimos al usuario que introduzca por terminal la cadena a buscar
buscar = str(input("Introduce la cadena que deseas buscar: "))

# Validaciones básicas del patrón a buscar
# Si no hay patron, error y volvemos a pedirlo
while not buscar:
	print("Error: la cadena a buscar no puede estar vacía.")
	buscar = str(input("Introduce la cadena que deseas buscar): "))

# Si el patron tiene simbolos no permitidos, error
for ch in buscar:
	if ch not in alfabeto:
		print(f"Error: el patrón contiene un símbolo no permitido: '{ch}'")

n = len(buscar)

# Estados q0..qn
# Sabemos que va a tener que haber un estado mas que simbolos en el patron
estados = {f"q{i}" for i in range(n+1)}
estado_inicial = "q0"
estados_finales = {f"q{n}"}

# Construcción de las transiciones
transiciones = {}

for i in range(n + 1):
    # Estado actual q0..qn
    estado_actual = f"q{i}"
    transiciones[estado_actual] = {}

    for simbolo in alfabeto:
        # Vemos a qué estado vamos si leemos este símbolo
        k = min(n, i + 1)
        candidato = buscar[:i] + simbolo

        # Buscamos el mayor k que encaje con el patrón
        while k > 0 and buscar[:k] != candidato[-k:]:
            k -= 1

        # Guardamos la transición
        transiciones[estado_actual][simbolo] = f"q{k}"

mi_afd = AFD(estados, alfabeto, transiciones, estado_inicial, estados_finales, buscar)

texto = input("Introduce el texto (cadena continua, puede contener espacios): ")
resultado = mi_afd.procesar_texto(texto)

print(f"Patrón configurado: '{buscar}'")
print(f"Texto suministrado: '{texto}'")
print(f"Número de ocurrencias: {resultado}")
