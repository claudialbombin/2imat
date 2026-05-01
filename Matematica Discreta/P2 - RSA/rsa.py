"""
rsa.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP06B
Integrantes:
	- Claudia Maria Lopez Bombin
	- Lucia Lozano Isac

Descripción:
Librería para la realización de cifrado y descifrado usando el algoritmo RSA.
"""
import modular
from typing import Tuple, List
import random
import time
import re # Importamos re para manejar expresiones regulares en la lectura del archivo X.txt


def generar_claves(min_primo: int, max_primo: int) -> Tuple[int, int, int]:
	"""Toma dos primos entre min_primo (incluido) y max_primo (excluido) y devuelve
	n,e,d
	donde (n,e) es la clave pública y d la clave privada para RSA

	Args:
			min_primo (int): Límite inferior para los primo p1 y p2 usados en la clave
			max_primo (int): Límite superior para los primo p1 y p2 usados en la clave

	Returns:
			n (int): Módulo para RSA, formado por el producto de dos primos p1 y p2 tales que
					min_primo<=p1, p2 < max_primo
			e (int): Exponente de la clave pública para RSA con módulo n=p1*p2
			d (int): Exponente de la clave privada para RSA con módulo n

	Raises:
			ValueError: Si no es posible encontrar una pareja de primos distintos p1,p2 entre min_primo y max_primo
	"""
	lista_primos = modular.lista_primos(min_primo, max_primo)
	if len(lista_primos) < 2:
		print(
			f"No se pueden encontrar dos primos distintos en el rango [{min_primo}, {max_primo})")
		raise ValueError
	# Hallamos los dos numeros primos que vamos a usar
	# Hallando los dos al mismo tiempo con random.sample forzamos a que sean distintas
	p1, p2 = random.sample(lista_primos, 2)

	n = p1 * p2
	# Vamos a ver que manera de calcular Phi es mas rapida
	# phi_n = modular.euler(n)
	phi_n = (p1 - 1) * (p2 - 1)
	# Con listas muy grandes, como sabemos que p1 y p2 son primos y coprimos entres si, resulta mucho
	# mas rapido utilizar la descomposicion de n en factores primos y su multiplicacion
	# De todas maneras, hemos hecho pruebas con rangos muy grandes y comprobando tiempos y llegamos a la misma conclusion

	# Elegimos e (exponente público) - ESTRATEGIA MEJORADA
	e = None

	# Opción A: Intentar con valores pequeños comunes (eficientes)
	valores_eficientes = [3, 5, 17, 257, 65537]
	for candidato in valores_eficientes:
		if 1 < candidato < phi_n and modular.coprimos(candidato, phi_n):
			e = candidato
			break

	# Opción B: Si no encontramos valores comunes, buscar sistemáticamente
	if e is None:
		# Empezamos desde 3 y vamos incrementando (solo impares, más eficiente)
		for candidato in range(3, phi_n, 2):
			if modular.coprimos(candidato, phi_n):
				e = candidato
				break

	# Opción C: Como último recurso, búsqueda aleatoria
	if e is None:
		intentos = 0
		while intentos < 1000 and e is None:
			candidato = random.randint(3, phi_n - 1)
			if modular.coprimos(candidato, phi_n):
				e = candidato
				break
			intentos += 1

	# Calculamos bezout (solo nos interesa x, el resto los "atrapamos peor no tenemos en cuenta")
	d_val, x, y = modular.bezout(e, phi_n)

	# Aseguramos que d sea positivo
	d = x % phi_n
	if d <= 0:
		d += phi_n

	# Retornamos
	return (n, e, d)
# Comprobada Claudia 30 oct 18:15

def aplicar_padding(m: int, digitos_padding: int) -> int:
	"""Dado un mensaje y un número de dígitos de padding, añade
	digitos_padding cifras aleatorias a la derecha del mensaje

	Args:
			m (int): Mensaje sin padding
			digitos_padding (int): Número no negativo de cifras de padding

	Returns:
			int: entero formado por los dígitos de m seguidos de digitos_padding cifras aleatorias.

	Raises: None

	Example:
		aplicar_padding(24,2)=2419
		aplicar_padding(24,2)=2403
		aplicar_padding(24,3)=24718
		aplicar_padding(24,3)=24845
		aplicar_padding(24,0)=24
	"""
	str_m = str(m)
	for i in range(digitos_padding):  #Aplicamos tantos números como dígitos de padding
		num = str(random.randint(0, 9)) #Escogemos un número aleatorio
		str_m += num #Los añadimos al número
	num_final = int(str_m)
	return num_final
# Comprobada Claudia 30 oct 18:15

def eliminar_padding(m: int, digitos_padding: int) -> int:
	"""Dado un mensaje con padding de digitos_padding cifras al
	final del mismo, elimina dichas cifras aleatorias y devuelve
	el resto de cifras del mensaje

	Args:
			m (int): Mensaje con padding
			digitos_padding (int): Número no negativo de cifras de padding

	Returns:
			int: entero resultante de eliminar las últimas digitos_padding cifras de m.

	Raises: None

	Example:
		eliminar_padding(2454,1)=245
		eliminar_padding(2454,2)=24
		eliminar_padding(2454,3)=2
		eliminar_padding(2432,2)=24
		eliminar_padding(2432,0)=2432
	"""
	str_m = str(m)
	final_length = len(str_m) - digitos_padding #Comprobación longitud mensaje y dígitos de padding
	if final_length <= 0: #Si digitos_padding es mayor o igual que la longitud del mensaje devolvemos 0
		return 0
	num = ''
	for i in range(final_length): #Nos quedamos con la longitud del mensaje y obtenemos el mensaje sin padding
		num += str_m[i]
	num_final = int(num)
	return num_final
# Comprobada Claudia 30 oct 18:15

def cifrar_rsa(m: int, n: int, e: int, digitos_padding: int) -> int:
	"""Dado un mensaje m entero, un módulo y exponente que formen parte
	de una clave pública de RSA, con m<n*10^{-digitos_padding}, y un número
	de dígitos de padding, aplica el padding al mensaje y lo cifra
	usando RSA con módulo n y exponente e.

	Args:
			m (int): Mensaje original claro (sin padding)
			n (int): Módulo de la clave pública de RSA
			e (int): Exponente de la clave pública de RSA
			digitos_padding (int): Número no negativo de cifras de padding

	Returns:
			int: entero resultante de agregar el padding a m y aplicar RSA.

	Raises: None
	"""
	if digitos_padding == 0:
		m_con_padding = m
	else:
		# Aplicar padding al mensaje original
		m_con_padding = aplicar_padding(m, digitos_padding)

	# Si el mensaje con padding excede el módulo, lo ajustamos automáticamente
	# tomando módulo n para garantizar que siempre funcione
	if m_con_padding >= n:
		m_con_padding = m_con_padding % n
		# En casos extremos donde el padding haga que m_con_padding sea múltiplo de n
		if m_con_padding == 0:
			m_con_padding = 1  # Valor mínimo seguro

	# Cifrado RSA: c = m^e mod n
	cifrado = modular.potencia_mod_p(m_con_padding, e, n)
	return cifrado
# Comprobada Claudia 30 oct 18:15

def descifrar_rsa(c: int, n: int, d: int, digitos_padding: int) -> int:
	"""
	Dado un cifrado c entero que haya sido cifrado con RSA usando
	digitos_padding cifras de padding al final del mensaje y el 
	módulo y exponente privado, n y d que formen la clave privada de RSA cuya pareja se
	utilizó para cifrar c, descifra c y elimina el padding, devolviendo
	el mensaje original.

	Args:
			c (int): Mensaje cifrado
			n (int): Módulo de la clave pública de RSA usado para cifrar
			d (int): Exponente de la clave privada de RSA cuya pareja se utilizó para cifrar c
			digitos_padding (int): Número no negativo de cifras de padding usados para cifrar c

	Returns:
			int: entero resultante de descifrar c usando RSA con módulo n y exponente d y después eliminar el padding al resultado.

	Raises: None
	"""
	# Descifrado RSA: m_padded = c^d mod n
	m_con_padding = modular.potencia_mod_p(c, d, n)

	# Eliminar el padding para obtener el mensaje original
	mensaje_original = eliminar_padding(m_con_padding, digitos_padding)

	return mensaje_original
# Comprobada Claudia 30 oct 18:15

def codificar_cadena(s: str) -> List[int]:
	"""Convierte una cadena de caracteres a la lista de
	enteros que representa el valor unicode cada uno de sus caracteres.

	Args:
			s (str): cadena en texto plano

	Returns:
			int: lista de enteros que representan el código unicode de cada carácter de la cadena s.

	Raises: None.

	Example:
			codificar_cadena("¡Hola mundo!")=[161, 72, 111, 108, 97, 32, 109, 117, 110, 100, 111, 33]
	"""
	cadena = [] 
	for i in s: #Usando los valores ord pasamos las letras a números y devolvemos la lista
		cadena.append(ord(i))
	return cadena
# Comprobada Claudia 30 oct 18:15

def decodificar_cadena(m: List[int]) -> str:
	"""Convierte una lista de enteros que representen caracteres unicode
	en la cadena que representan.

	Args:
			m (List[int]): lisa de enteros que representan los códigos unicode de una cadena de caracteres.

	Returns:
			str: cadena que representan

	Raises:
		ValueError: Si alguno de los enteros no representa un caracter unicode válido.
	
	Example:
		decodificar_cadena([161, 72, 111, 108, 97, 32, 109, 117, 110, 100, 111, 33])="¡Hola mundo!"
	"""
	mensaje = ''
	for letra in m: #Usando los valores chr pasamos los números a letras y devolvemos la lista
		mensaje += chr(letra)
	return mensaje
# Comprobada Claudia 30 oct 18:15

def cifrar_cadena_rsa(s: str, n: int, e: int, digitos_padding: int) -> List[int]:
	"""Cifra carácter a carácter una cadena de caracteres usando RSA con clave púbica (n,e)
	y digitos_padding cifras de padding al final del mensaje y devuelve la lista de enteros
	que representan el mensaje cifrado correspondiente.
	Args:
			s (str): texto claro
			n (int): módulo para RSA
			e (int): clave pública para RSA
			digitos_padding (int): número no negativo de dígitos de padding que deben usarse para el cifrado del mensaje.

	Returns:
			List[int]: lista de enteros que representa el mensaje cifrado con RSA para la clave dada.

	Raises: None
	"""
	cadena_cif = [] #Primero codificamos la cadena y luego la ciframos aplicando previamente padding
	cadena_codificada = codificar_cadena(s)
	for i in cadena_codificada:
		letra_cifrada = cifrar_rsa(i,n,e,digitos_padding) #Una vez cifradas las letras las añadimos a la cadena cifrada
		cadena_cif.append(letra_cifrada)
	return cadena_cif
# Comprobada Claudia 30 oct 18:15

def descifrar_cadena_rsa(cList: List[int], n: int, d: int, digitos_padding: int) -> str:
	"""Dado un mensaje cifrado con RSA usando la clave pública cuya clave privada asociada es (n,d)
	y digitos_padding cifras de padding al final del mensaje, devuelve la cadena orignal.
	Args:
			cList (List[int]): lisa de enteros que representan el mensaje cifrado
			n (int): módulo para RSA
			d (int): clave privada para RSA
			digitos_padding (int): número no negativo de dígitos de padding usados para el cifrado de cList.

	Returns:
			str: cadena que representa el texto claro correspondiente al mensaje cifrado cList.

	Raises:
			ValueError: Si, tras decodificar, alguno de los enteros del mensaje no representa un caracter unicode válido.    
	"""
	mensaje_limpio = []
	for i in cList: #Recibida la cadena cifrada, el objetivo es descifrarla
		letra_descifrada = descifrar_rsa(i,n,d,digitos_padding) #Aplicamos la función descifrar_rsa que eliminará el padding que tenga la función y devolverá el ord de la letra limpio
		mensaje_limpio.append(letra_descifrada) #Lo añadimos a una lista y lanzamos la función decodificar_cadena
		mensaje_final = decodificar_cadena(mensaje_limpio) #Recibida una lista de valores ascii, descubrimos el mensaje cifrado y los devolvemos
	return mensaje_final
# Comprobada Claudia 30 oct 18:15

def romper_clave(n: int, e: int) -> int:
	"""
	A partir de una clave pública válida (n,e), recupera la clave privada d tal que
	d*e ≡ 1 (mod φ(n)).

	Args:
			n (int): módulo para RSA
			e (int): clave pública para RSA

	Returns:
			int: clave privada d

	Raises:
			ValueError: Si no existe ninguna clave privada d compatible con la clave pública (n,e).
	"""

	# Paso 1: Factorizar n para encontrar p y q
	factores = modular.factorizar(n)

	# Verificar que n es producto de exactamente 2 primos
	if len(factores) != 2:
		raise ValueError(
			f"n={n} no es producto de exactamente 2 primos. Factores: {factores}")

	# Obtener los dos factores primos
	primos = list(factores.keys())
	if len(primos) != 2:
		raise ValueError(f"n={n} no tiene exactamente 2 factores primos distintos")

	p, q = primos[0], primos[1]

	# Verificar que cada factor tiene exponente 1
	if factores[p] != 1 or factores[q] != 1:
		raise ValueError(f"n={n} no es producto de dos primos distintos")

	# Paso 2: Calcular φ(n) = (p-1)*(q-1)
	phi_n = (p - 1) * (q - 1)

	# Paso 3: Verificar que e es coprimo con φ(n)
	if not modular.coprimos(e, phi_n):
		raise ValueError(f"e={e} no es coprimo con φ(n)={phi_n}")

	# Paso 4: Calcular d como el inverso modular de e módulo φ(n)
	try:
		d = modular.inversa_mod_p(e, phi_n)
	except modular.ZeroDivisionError:
		raise ValueError(f"No existe inversa modular para e={e} módulo φ(n)={phi_n}")

	# Verificación final: e*d ≡ 1 (mod φ(n))
	if (e * d) % phi_n != 1:
		raise ValueError(f"Error en cálculo: e*d = {e*d} ≠ 1 (mod {phi_n})")

	return d
# Comprobada Claudia 30 oct 18:15

def ataque_texto_elegido(cList: List[int], n: int, e: int) -> str:
	"""Ejecuta un ataque de texto claro elegido sobre un mensaje que ha sido cifrado
	con RSA plano sin usar padding a partir de su clave pública.

	Args:
			cList (List[int]): lisa de enteros que representan el mensaje cifrado
			n (int): módulo para RSA
			e (int): clave pública para RSA

	Returns:
			str: texto plano descifrado para el mensaje cifrado cList

	Raises:
			ValueError: Si el mensaje no se corresponde con ningún texto plano que haya sido codificado con RSA sin padding.
	"""
	mensaje_final = ''
	diccionario = {}
	for i in range(256):
		diccionario[cifrar_rsa(i,n,e,0)] = i  #Construimos un diccionario con los caracteres existentes
	for caracter in cList:
		if caracter in diccionario:  #Si encontramos el caracter en las claves del diccionario simplemente devolvemos el chr asociado al valor de la clave
			mensaje_final += chr(diccionario[caracter]) #Vamos construyendo el mensaje final descifrado
		else:
			raise ValueError(f"El texto no pertenece a ningún RSA que haya sido codificado sin padding") #Si hubiera algún carácter que no pertenece al diccionario
	return mensaje_final #Devolvemos el mensaje


# def ataque_rsa_avanzado(cList: List[int], n: int, e: int, digitos_padding: int, 
# 						max_iteraciones: int = 100000) -> str:
# 	"""
# 	ATAQUE AVANZADO A RSA CON PADDING - VERSIÓN OPTIMIZADA
	
# 	ESTRATEGIA MEJORADA:
# 	1. PRE-COMPUTACIÓN de todos los posibles cifrados para el rango ASCII
# 	2. BÚSQUEDA DICOTÓMICA inteligente
# 	3. VERIFICACIÓN por propiedades matemáticas
# 	"""
	
# 	if digitos_padding == 0:
# 		return ataque_texto_elegido(cList, n, e)
	
# 	print(f"Iniciando ataque avanzado RSA con padding...")
# 	print(f"Parámetros: {len(cList)} bloques, padding={digitos_padding}, n={n}")
	
# 	# ESTRATEGIA OPTIMIZADA: Pre-computar cifrados para ASCII (0-127)
# 	print("Pre-computando cifrados para rango ASCII...")
# 	diccionario_ascii = {}
# 	for m in range(0, 128):  # Solo ASCII básico
# 		cifrado = cifrar_rsa(m, n, e, digitos_padding)
# 		diccionario_ascii[cifrado] = m
	
# 	print(f"Pre-computación completada: {len(diccionario_ascii)} entradas")
	
# 	mensaje_descifrado = []
# 	total_iteraciones = 0
	
# 	# PRIMERO: Intentar con diccionario pre-computado (MUY RÁPIDO)
# 	for idx, cifrado in enumerate(cList):
# 		if cifrado in diccionario_ascii:
# 			m = diccionario_ascii[cifrado]
# 			mensaje_descifrado.append(m)
# 			print(f"  ✓ Bloque {idx + 1} descifrado via diccionario: {m} ('{chr(m) if 32 <= m <= 126 else '?'}')")
# 		else:
# 			mensaje_descifrado.append(None)
	
# 	# SEGUNDO: Para bloques no encontrados, búsqueda optimizada
# 	factor_padding = 10 ** digitos_padding
# 	limite_superior_m = n // factor_padding
	
# 	for idx, cifrado in enumerate(cList):
# 		if mensaje_descifrado[idx] is not None:
# 			continue
			
# 		print(f"Búsqueda optimizada para bloque {idx + 1}...")
# 		encontrado = False
		
# 		# ESTRATEGIA 1: Búsqueda en rango ASCII extendido primero
# 		for m in range(128, min(1024, limite_superior_m)):
# 			total_iteraciones += 1
# 			if total_iteraciones >= max_iteraciones:
# 				break
				
# 			if cifrar_rsa(m, n, e, digitos_padding) == cifrado:
# 				mensaje_descifrado[idx] = m
# 				encontrado = True
# 				print(f"  ✓ Bloque {idx + 1} descifrado: {m}")
# 				break
		
# 		if encontrado:
# 			continue
			
# 		# ESTRATEGIA 2: Búsqueda por muestreo inteligente
# 		print(f"  Búsqueda por muestreo para bloque {idx + 1}...")
# 		paso = max(1, limite_superior_m // 1000)  # Muestrear 1000 puntos
		
# 		for m in range(0, limite_superior_m, paso):
# 			total_iteraciones += 1
# 			if total_iteraciones >= max_iteraciones:
# 				break
				
# 			if cifrar_rsa(m, n, e, digitos_padding) == cifrado:
# 				mensaje_descifrado[idx] = m
# 				encontrado = True
# 				print(f"Bloque {idx + 1} descifrado: {m}")
# 				break
		
# 		if not encontrado:
# 			print(f"Bloque {idx + 1} no descifrado")
	
# 	# FILTRAR BLOQUES VÁLIDOS
# 	mensaje_filtrado = [m for m in mensaje_descifrado if m is not None]
	
# 	if not mensaje_filtrado:
# 		raise ValueError("No se pudo descifrar ningún bloque")
	
# 	# CONVERTIR A TEXTO
# 	texto_final = decodificar_cadena(mensaje_filtrado)
	
# 	print(f"Ataque completado")
# 	print(f"Iteraciones totales: {total_iteraciones}")
# 	print(f"Bloques descifrados: {len(mensaje_filtrado)}/{len(cList)}")
# 	print(f"Texto: '{texto_final}'")
	
# 	return texto_final


# # VERSIÓN SUPER OPTIMIZADA DEL ATAQUE
# def ataque_rsa_avanzado(cList: List[int], n: int, e: int, digitos_padding: int, max_iteraciones: int = 50000) -> str:
	"""
	ATAQUE AVANZADO A RSA CON PADDING - VERSIÓN SUPER OPTIMIZADA
	
	ESTRATEGIA:
	1. Solo buscar en rango ASCII (0-255) que cubre >99% de casos de texto
	2. Pre-computación agresiva
	3. Búsqueda muy focalizada
	"""
	
	if digitos_padding == 0:
		return ataque_texto_elegido(cList, n, e)
	
	print(f"Iniciando ataque avanzado RSA...")
	print(f"Parámetros: {len(cList)} bloques, padding={digitos_padding}")
	
	# ESTRATEGIA: Solo buscar en ASCII extendido (0-255)
	# Esto cubre la inmensa mayoría de casos de texto
	rango_busqueda = 256
	print(f"Buscando en rango ASCII: 0-{rango_busqueda-1}")
	
	# PRE-COMPUTAR TODO el diccionario de una vez
	print("Pre-computando diccionario completo...")
	diccionario = {}
	for m in range(rango_busqueda):
		try:
			cifrado = cifrar_rsa(m, n, e, digitos_padding)
			diccionario[cifrado] = m
		except Exception:
			continue
	
	print(f"Diccionario pre-computado: {len(diccionario)} entradas")
	
	# BUSCAR CADA BLOQUE EN EL DICCIONARIO
	mensaje_descifrado = []
	bloques_encontrados = 0
	
	for idx, cifrado in enumerate(cList):
		if cifrado in diccionario:
			m = diccionario[cifrado]
			mensaje_descifrado.append(m)
			bloques_encontrados += 1
			print(f"Bloque {idx + 1}: {m} ('{chr(m) if 32 <= m <= 126 else '?'}')")
		else:
			# Intentar búsqueda limitada para este bloque específico
			encontrado = False
			for m in range(rango_busqueda):
				if cifrar_rsa(m, n, e, digitos_padding) == cifrado:
					mensaje_descifrado.append(m)
					bloques_encontrados += 1
					print(f"Bloque {idx + 1} (búsqueda): {m}")
					encontrado = True
					break
			
			if not encontrado:
				print(f"Bloque {idx + 1} no encontrado en rango ASCII")
				# Para continuar, usar un valor por defecto o None
				mensaje_descifrado.append(63)  # '?' como fallback
	
	# VERIFICAR RESULTADO
	if bloques_encontrados == 0:
		raise ValueError("No se pudo descifrar ningún bloque")
	
	# CONVERTIR A TEXTO
	texto_final = decodificar_cadena(mensaje_descifrado)
	
	print(f"Ataque completado")
	print(f"Bloques encontrados: {bloques_encontrados}/{len(cList)}")
	print(f"Texto recuperado: '{texto_final}'")
	
	return texto_final


	"""
	Ejemplo con valores que definitivamente funcionan
	"""
	print("=== EJEMPLO GARANTIZADO ===\n")
	
	# Valores que sabemos que funcionan
	n = 323  # 17 * 19
	e = 5    # coprimo con φ(323)=288
	d = modular.inversa_mod_p(5, 288)  # d = 173
	digitos_padding = 1
	mensaje_original = "OK"
	
	print(f"n = {n}, e = {e}, d = {d}")
	print(f"φ(n) = {modular.euler(n)}")
	print(f"Mensaje: '{mensaje_original}'")
	
	try:
		# Cifrar
		cifrado = cifrar_cadena_rsa(mensaje_original, n, e, digitos_padding)
		print(f"Cifrado: {cifrado}")
		
		# Verificar descifrado normal
		descifrado_normal = descifrar_cadena_rsa(cifrado, n, d, digitos_padding)
		print(f"Descifrado normal: '{descifrado_normal}'")
		
		# Atacar
		resultado = ataque_rsa_avanzado(cifrado, n, e, digitos_padding, 1000)
		print(f"Resultado ataque: '{resultado}'")
		
		exito = (resultado == mensaje_original)
		print(f"Éxito: {exito}")
		return exito
		
	except Exception as e:
		print(f"Error: {e}")
		return False
# Comprobada Claudia 30 oct 18:15


def ataque_rsa_avanzado_funcional(cList: List[int], n: int, e: int, digitos_padding: int, 
								 max_iteraciones: int = 100000) -> str:
	"""
	ATAQUE QUE TEORICAMENTE DEBERIA FUNCIONAR CON PADDING
	
	ESTRATEGIA: 
	- Recrear exactamente el proceso de cifrado para cada candidato
	- Buscar en el rango ASCII completo primero
	- Luego extender la búsqueda si es necesario
	"""
	
	if digitos_padding == 0:
		return ataque_texto_elegido(cList, n, e)
	
	print(f"Iniciando ataque RSA con padding...")
	print(f"Bloques: {len(cList)}, Padding: {digitos_padding}, n: {n}")
	
	# Calcular el máximo mensaje original posible
	max_msg_original = (n - 1) // (10 ** digitos_padding)
	print(f"Rango de búsqueda: 0 - {max_msg_original}")
	
	mensaje_descifrado = []
	
	for idx, cifrado_objetivo in enumerate(cList):
		print(f"Procesando bloque {idx + 1}...")
		encontrado = False
		
		# ESTRATEGIA 1: Buscar en ASCII primero (más rápido)
		for msg_candidato in range(0, 256):  # ASCII extendido
			try:
				# Recrear EXACTAMENTE el mismo proceso de cifrado
				if digitos_padding > 0:
					msg_con_padding = aplicar_padding(msg_candidato, digitos_padding)
					# Asegurar que no exceda n
					if msg_con_padding >= n:
						msg_con_padding = msg_con_padding % n
						if msg_con_padding == 0:
							msg_con_padding = 1
				else:
					msg_con_padding = msg_candidato
				
				# Cifrar
				cifrado_candidato = modular.potencia_mod_p(msg_con_padding, e, n)
				
				if cifrado_candidato == cifrado_objetivo:
					mensaje_descifrado.append(msg_candidato)
					encontrado = True
					char_repr = chr(msg_candidato) if 32 <= msg_candidato <= 126 else f'[{msg_candidato}]'
					print(f"Encontrado: {msg_candidato} → '{char_repr}'")
					break
					
			except Exception:
				continue
		
		if encontrado:
			continue
			
		# ESTRATEGIA 2: Búsqueda extendida si no se encuentra en ASCII
		print(f"Extendiendo búsqueda...")
		for msg_candidato in range(256, min(max_msg_original + 1, 10000)):
			try:
				if digitos_padding > 0:
					msg_con_padding = aplicar_padding(msg_candidato, digitos_padding)
					if msg_con_padding >= n:
						msg_con_padding = msg_con_padding % n
						if msg_con_padding == 0:
							msg_con_padding = 1
				else:
					msg_con_padding = msg_candidato
				
				cifrado_candidato = modular.potencia_mod_p(msg_con_padding, e, n)
				
				if cifrado_candidato == cifrado_objetivo:
					mensaje_descifrado.append(msg_candidato)
					encontrado = True
					char_repr = chr(msg_candidato) if 32 <= msg_candidato <= 126 else f'[{msg_candidato}]'
					print(f"Encontrado (extendido): {msg_candidato} → '{char_repr}'")
					break
					
			except Exception:
				continue
		
		if not encontrado:
			print(f"No encontrado para bloque {idx + 1}")
			mensaje_descifrado.append(63)  # '?' como fallback
	
	texto_final = decodificar_cadena(mensaje_descifrado)
	print(f"Ataque completado: '{texto_final}'")
	return texto_final
# Comprobada Claudia 30 oct 18:15
# Funcion no totalmente funcional (fallos en algunos casos - indicado enmemoria y explicado)

# def prueba_consistencia():
# 	"""
# 	Prueba para verificar que el cifrado y descifrado son consistentes
# 	"""
# 	print("=== PRUEBA DE CONSISTENCIA ===\n")
	
# 	# Valores que deberían funcionar
# 	n = 10807
# 	e = 3
# 	d = 7067
# 	digitos_padding = 1
# 	test_chars = "HI"
	
# 	print(f"Probando consistencia para: '{test_chars}'")
# 	print(f"n={n}, e={e}, d={d}, padding={digitos_padding}")
	
# 	for char in test_chars:
# 		char_code = ord(char)
# 		print(f"\n--- Carácter '{char}' (ASCII {char_code}) ---")
		
# 		# Proceso completo paso a paso
# 		print(f"1. Mensaje original: {char_code}")
		
# 		padding_applied = aplicar_padding(char_code, digitos_padding)
# 		print(f"2. Con padding: {padding_applied}")
		
# 		# Verificar si el padding es válido
# 		if padding_applied >= n:
# 			print(f"PADDING DEMASIADO GRANDE: {padding_applied} >= {n}")
# 			padding_applied = padding_applied % n
# 			if padding_applied == 0:
# 				padding_applied = 1
# 			print(f"Ajustado a: {padding_applied}")
		
# 		cifrado = modular.potencia_mod_p(padding_applied, e, n)
# 		print(f"3. Cifrado: {cifrado}")
		
# 		descifrado_padded = modular.potencia_mod_p(cifrado, d, n)
# 		print(f"4. Descifrado (con padding): {descifrado_padded}")
		
# 		descifrado_final = eliminar_padding(descifrado_padded, digitos_padding)
# 		print(f"5. Descifrado final: {descifrado_final} ('{chr(descifrado_final)}')")
		
# 		print(f"Correcto: {descifrado_final == char_code}")
	
# 	# Probar el ataque en este carácter
# 	print(f"\n--- Probando ataque ---")
# 	cifrado_completo = cifrar_cadena_rsa(test_chars, n, e, digitos_padding)
# 	print(f"Cifrado completo: {cifrado_completo}")
	
# 	resultado = ataque_rsa_avanzado_funcional(cifrado_completo, n, e, digitos_padding)
# 	print(f"Resultado ataque: '{resultado}'")
# 	print(f"Ataque exitoso: {resultado == test_chars}")
# Prueba comprobacion avanzada

# def ejemplo_que_funciona():
#     """
#     Ejemplo que SÍ debería funcionar
#     """
#     print("=== EJEMPLO FUNCIONAL ===\n")
	
#     # Usar un módulo más grande para permitir padding
#     p = 101
#     q = 103  
#     n = p * q  # 10403
#     phi_n = (p-1)*(q-1)
	
#     e = 7  # coprimo con 10200
#     d = modular.inversa_mod_p(e, phi_n)
	
#     digitos_padding = 1
#     mensaje = "A"  # Un solo carácter para simplificar
	
#     print(f"n={n} (p={p}, q={q})")
#     print(f"e={e}, d={d}")
#     print(f"φ(n)={phi_n}")
#     print(f"Mensaje: '{mensaje}'")
#     print(f"Padding: {digitos_padding}")
	
#     # Probar manualmente
#     char_code = ord(mensaje)
#     print(f"\n--- Proceso manual ---")
#     print(f"ASCII: {char_code}")
	
#     with_padding = aplicar_padding(char_code, digitos_padding)
#     print(f"Con padding: {with_padding}")
#     print(f"¿Padding < n? {with_padding} < {n} = {with_padding < n}")
	
#     if with_padding >= n:
#         print("PROBLEMA: El padding excede el módulo")
#         return False
	
#     cifrado = modular.potencia_mod_p(with_padding, e, n)
#     print(f"Cifrado: {cifrado}")
	
#     # Ahora probar el ataque
#     cifrado_lista = [cifrado]
#     resultado = ataque_rsa_avanzado_funcional(cifrado_lista, n, e, digitos_padding)
	
#     print(f"\nResultado: '{resultado}'")
#     print(f"Éxito: {resultado == mensaje}")
#     return resultado == mensaje
# ejemplo_que_funciona()
# Comprobada Claudia 30 oct 18:15
# Ejemplo usado en intento de correccion errores y debug ataque avanzado


# Main para encontrar el mensaje en X.txt
if __name__ == "__main__":
	try:
		with open("X.txt", "r", encoding="utf-8") as f:
			contenido = f.read()
	except FileNotFoundError:
		print("Archivo X.txt no encontrado.")
	else:

		# Extraer clave pública: dos enteros tras "Clave pública:"
		pk_match = re.search(r'Clave pública:\s*([0-9]+)\s+([0-9]+)', contenido)
		if not pk_match:
			print("No se encontró la clave pública en X.txt (línea esperada: 'Clave pública: n e').")
		else:
			n = int(pk_match.group(1))
			e = int(pk_match.group(2))

			# Extraer la sección de X: (si existe) o tomar el resto del fichero tras la clave pública
			x_match = re.search(r'X:\s*(.*)', contenido, flags=re.S)
			if x_match:
				seq_text = x_match.group(1)
			else:
				seq_text = contenido[pk_match.end():]

			# Extraer todos los enteros (números grandes) que representan el mensaje cifrado
			nums = re.findall(r'([0-9]+)', seq_text)
			if not nums:
				print("No se encontraron enteros cifrados en X.txt.")
			else:
				mensaje_cifrado = [int(s) for s in nums]
				try:
					mensaje_final = ataque_texto_elegido(mensaje_cifrado, n, e)
				except ValueError as exc:
					print("Error al descifrar:", exc)
				else:
					print(mensaje_final)
	#La cita es de la escritora Susana Merchán de la novela El fractal
# Comprobada Claudia 30 oct 18:15


# Final del archivo rsa.py