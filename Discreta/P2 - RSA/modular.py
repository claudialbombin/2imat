"""
modular.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP06B
Integrantes:
	- Claudia Maria Lopez Bombin
	- Lucia Lozano Isac

Descripción:
Librería para la realización de cálculos y resolución de problemas de aritmética modular.
"""

from typing import Tuple, List, Dict


class IncompatibleEquationError(Exception):
    pass


# Funcion 1
def es_primo(n: int) -> bool:
    """ Reciba un entero n y devuelva verdadero si es un número primo y falso en caso contrario

    Args:
            n (int): Entero

    Returns:
            true si el entero es un número primo.
            false en caso contrario.

    Raises: None

    Examples:
            es_primo(5)=True
            es_primo(4)=False
    """

    if n <= 1:
        return False
    if n <= 3:
        return True  # 2 y 3 son primos
    if n % 2 == 0 or n % 3 == 0:
        return False  # descartamos múltiplos de 2 y 3

    # Prechequeo de primos pequeños (5 y 7) para reducir iteraciones
    if (n % 5 == 0 or n % 7 == 0) and (n != 5 and n != 7):
        return False

    # Solo comprobamos divisores de la forma 6k ± 1 empezando desde 5
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6  # probamos 6k-1 y 6k+1
    return True


# Funcion 2
def lista_primos(a: int, b: int) -> List[int]:
    """ Recibe dos enteros a y b y devuelva la lista de números primos en el intervalo [a, b)

    Args:
            a (int): Elemento inicial del intervalo (incluido)
            b (int): Elemento final del intervalo (no incluido)

    Returns:
            List[int]: lista ordenada de primos mayores o iguales que a y menores que b.

    Raises: None

    Examples:
            lista_primos(1,11)=[2,3,5,7]
    """
    primos = []
    for n in range(a, b):
        if es_primo(n):
            primos.append(n)

    return primos


# Funcion 3 - CORREGIDA
def factorizar(n: int) -> Dict[int, int]:
    """ Recibe  un entero n y devuelve un diccionario cuyas claves son los primos que dividen a n y sus valores los
    correspondientes exponentes en la descomposición en producto de factores primos de n.
    Args:
            n (int): Entero que se desea factorizar.

    Returns:
            Dict[int,int]: Diccionario en el que las claves son primos positivos p_i que dividen a n y, para cada p_i,
                    su valor asociado es el máximo exponente e_i tal que p_i^(e_i) divide a n. Si n=0, devuelve un diccionario vacío.

    Raises: None

    Examples:
            factorizar(12)={2: 2, 3: 1}
            factorizar(0)={}
            factorizar(1)={}
            factorizar(-1)={}
    """
    factores = {}

    if n == 0:
        return {}
    
    # CORRECCIÓN: Manejo explícito de n=1 y n=-1
    # Según el informe, factorizar(1) y factorizar(-1) no devolvían lo esperado
    if abs(n) == 1:
        return {}  # 1 y -1 no tienen factores primos
    
    n = abs(n)  # ignoramos el signo, solo factorizamos la magnitud

    # Contar factores de 2
    exp = 0
    while n % 2 == 0:
        exp += 1
        n //= 2
    if exp > 0:
        factores[2] = exp

    # Contar factores impares
    p = 3
    while p * p <= n:
        exp = 0
        while n % p == 0:
            exp += 1
            n //= p
        if exp > 0:
            factores[p] = exp
        p += 2

    # Si queda un primo mayor que sqrt(n)
    if n > 1:
        factores[n] = 1

    return factores


# Funcion 4.1
def mcd(a: int, b: int) -> int:
    """ Calcula el máximo común divisor de dos enteros a y b.
    Args:
            a (int): Primer entero.
            b (int): Segundo entero.

    Returns:
            int: devuelve el máximo común divisor de a y b

    Raises: None

    Examples:
            mcd(10,15)=5
    """
    a, b = abs(a), abs(b)  # trabajar solo con positivos
    # bucle mientras b no sea cero
    while b:
        a, b = b, a % b

    return a


# Funcion 4.2
def bezout(n: int, m: int) -> Tuple[int, int, int]:
    """ Calcula el máximo común divisor d de dos enteros a y b junto con dos enteros x e y tales que
                    d=ax+by

    Args:
            a (int): Primer entero.
            b (int): Segundo entero.

    Returns: (d,x,y)
            d (int): Máximo común divisor.
            x (int): Coeficiente de a.
            y (int): Coeficiente de b.

    Raises: None

    Examples:
            bezout(6,10)=(2,2,-1)
    """
    if m == 0:
        return n, 1, 0
    elif n == 0:
        return m, 0, 1
    else:
        d, x1, y1 = bezout(m, n % m)
        x = y1
        y = x1 - (n//m) * y1
        return d, x, y


# Funcion 5.1: opcional mcd_n
def mcd_n(nlist: List[int]) -> int:
    """ Dados una lista de enteros, devuelve el máximo divisor común a todos ellos.
    Args:
            nList (List[int]): Lista de enteros.        

    Returns:
            int: devuelve el máximo entero que divide a todos los enteros de la lista.

    Raises: None

    Examples:
            mcd([4,10,14])=2
    """
    # Opcional
    if not nlist:
        return 0  # si la lista está vacía, devolvemos 0 por convención
    # Inicializamos el resultado con el primer elemento
    res = nlist[0]
    # Iteramos sobre el resto de elementos
    for num in nlist[1:]:
        res = mcd(res, num)
        if res == 1:  # corte temprano: si el MCD llega a 1, ya no puede disminuir más
            break

    return res


# Funcion 5.2: opcional bezout_n
def bezout_n(nlist: List[int]) -> Tuple[int, List[int]]:
    # Opcional
    """ Dada una lista de enteros [a_1,...,a_n], devuelve el máximo divisor común d a todos ellos y una
    lista de coeficientes [x_1,...,x_n] tal que
            d=a_1*x_1+...a_n*x_n

    Args:
            nList (List[int]): Lista de enteros.        

    Returns: (d,X)
            d (int): Máximo entero que divide a todos los enteros de la lista.
            X (List[int]): Lista de coeficientes [x_1,...,x_n].

    Raises: None

    Examples
            bezout_n([4,10,14])=(2,[-2,1,0])
    """
    if not nlist:
        return 0, []
    # Inicializamos con el primer número
    d = nlist[0]
    coefs = [1]  # coeficiente del primer número
    # Iteramos sobre el resto de números
    for i in range(1, len(nlist)):
        d_next = nlist[i]
        # Calculamos el MCD extendido entre d (acumulado) y el siguiente número
        g, x, y = bezout(d, d_next)
        # Actualizamos los coeficientes acumulados
        coefs = [c * x for c in coefs] + [y]
        d = g  # actualizamos el MCD acumulado

    return d, coefs


# Funcion 6
def coprimos(n: int, m: int) -> bool:
    """ Determina si dos enteros son coprimos.
    Args:
            a (int): Primer entero.
            b (int): Segundo entero.

    Returns:
            bool: Verdadero si son coprimos y falso si no.

    Raises: None

    Examples:
            coprimos(14,20)=False
            coprimos(14,15)=True
    """

    # Dos numeros son coprimos si su máximo común divisor es 1
    return mcd(n, m) == 1  # Retornamos directamente la comparación, si es True o False


# Funcion 7 - CORREGIDA
def potencia_mod_p(base: int, exp: int, p: int) -> int:
    """ Calcula potencias módulo p.

    Args:
            base (int): Base de la potencia.
            exp (int): Exponente al que se eleva la base.
            p (int): Módulo.

    Returns:
            int: Resto de dividir base^exp módulo p.

    Raises:
            ZeroDivisionError: Si el módulo es 0 o si la base y el exponente
            son ambos 0 al mismo tiempo.

    Examples:
            potencia_mod_p(2,3,7)=1
    """
    if p == 0 or (base == 0 and exp == 0):
        raise ZeroDivisionError("Módulo 0 o 0^0 no definido.")

    # CORRECCIÓN: Manejo de módulos negativos
    # Según el informe, no funcionaba correctamente para módulos negativos
    p = abs(p)  # Convertimos a valor absoluto para manejar módulos negativos
    if p == 0:
        raise ZeroDivisionError("Módulo 0 no definido.")

    # Manejar exponentes negativos
    if exp < 0:
        # a^(-n) ≡ (a^(-1))^n mod p
        base_inv = inversa_mod_p(base, p)
        return potencia_mod_p(base_inv, -exp, p)

    result = 1 % p
    base = base % p

    # Algoritmo de exponenciación rápida
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % p
        base = (base * base) % p
        exp //= 2

    return result


# Funcion 8 - CORREGIDA
def inversa_mod_p(n: int, p: int) -> int:
    """ Calcula la inversa de un número n módulo p.

    Args:
            n (int): Número que se desea invertir
            p (int): Módulo.

    Returns:
            int: Entero x entre 0 y p-1 tal que n*x es congruente con 1 módulo p.

    Raises:
            ZeroDivisionError: Si el módulo es 0 o si n no es invertible módulo p.

    Examples:
            inversa_mod_p(2,7)=4
    """
    if p == 0:
        # No se puede calcular módulo 0
        raise ZeroDivisionError("El módulo no puede ser 0.")

    # CORRECCIÓN: Manejo de módulos negativos
    # Según el informe, no funcionaba correctamente para módulos negativos
    p = abs(p)  # Convertimos a valor absoluto para manejar módulos negativos
    if p == 0:
        raise ZeroDivisionError("El módulo no puede ser 0.")

    # Inicializamos variables para el algoritmo extendido de Euclides iterativo
    a, b = n, p      # a = n, b = p
    x0, x1 = 1, 0    # coeficientes de Bezout iniciales: x0*a + x1*b = a

    # Bucle iterativo hasta que el residuo sea 0
    while b != 0:
        q = a // b         # cociente de la división entera
        a, b = b, a % b    # actualizamos a y b al residuo
        x0, x1 = x1, x0 - q * x1  # actualizamos los coeficientes de Bezout

    # Si el MCD no es 1, n no es invertible módulo p
    if a != 1:
        raise ZeroDivisionError(f"{n} no es invertible módulo {p}.")

    # x0 es la inversa modular, aseguramos que esté en el rango [0, p-1]
    return x0 % p


# Funcion 9
def euler(n: int) -> int:
    """ Calcula la función phi de Euler de un entero positivo n, es decir, cuenta cúantos enteros positivos
    menores que n son coprimos con n.

    Args:
            n (int): Número entero positivo.

    Returns:
            int: Función phi de Euler de n.

    Raises: None

    Examples:
            euler(7)=6
            euler(15)=8
    """
    '''La función φ(n) se define como el número de enteros k en el rango 1 ≤ k ≤ n para los cuales 
	el máximo común divisor gcd(n, k) = 1.
	
	Utiliza la fórmula de Euler: φ(n) = n × ∏(1 - 1/p) para todos los factores primos p de n.
	'''

    # Caso especial: si n es no positivo, retornamos 0, ya que analizamos enteros positivos
    if n <= 0:
        return 0
    # Comenzamos con la fórmula completa y luego aplicaremos los factores primos
    result = n
    # Manejar el factor primo 2 por separado, para eliminar pares y solo iterar sobre impares
    if n % 2 == 0:
        # φ(n) se multiplica por (1 - 1/2) = 1/2, equivalente a restar n/2
        result -= result // 2
        # Eliminamos todos los pares
        while n % 2 == 0:
            n //= 2

    # Comenzamos en 3 y avanzamos de 2 en 2 (para solo procesar números impares)
    p = 3
    # Solo necesitamos verificar factores hasta √n porque:
    # - Si n tiene un factor mayor que √n, debe tener uno menor que √n (el algoritmo que usamos para primos)
    while p * p <= n:
        # Verificamos si p es un factor primo de n
        if n % p == 0:
            # Si p es un factor primo, aplicamos la fórmula de Euler:
            # Multiplicamos result por (1 - 1/p), equivalente a restar result/p
            result -= result // p

            # Eliminamos todas las ocurrencias del factor primo p, procesando solo una vez
            while n % p == 0:
                n //= p
        # Avanzamos al siguiente número impar
        p += 2

    # CASO FINAL: Si después de la factorización n > 1, entonces n es primo
    # Esto ocurre cuando el n restante es un número primo mayor que √n original
    if n > 1:
        # Aplicamos la fórmula de Euler para este factor primo final
        result -= result // n

    # Retornamos el resultado final de φ(n)
    return result


# Funcion 10 - CORREGIDA
def legendre(n: int, p: int) -> int:
    """ Dado un entero n y un número primo p, calcula el símbolo de Legendre de n módulo p.

    Args:
            n (int): Número entero.
            p (int): Número primo.

    Returns:
            int: Símbolo de Legendre de Euler de n módulo p:
                    0 si es múltiplo de p
                    1 si es un cuadrado perfecto (distinto de 0), módulo p
                    -1 en caso contrario.

    Raises:
            ZeroDivisionError: Si el módulo p es 0.

    Examples:
            legendre(2,5)=-1
            legendre(2,7)=1
            legendre(10,5)=0
    """
    # Validación rápida de p
    if p <= 0:
        raise ZeroDivisionError(f"p debe ser positivo, se recibió p={p}")

    # CORRECCIÓN: Caso p=2 manejado correctamente
    # La versión anterior tenía un error en el caso p=2
    if p == 2:
        n_mod_2 = n % 2
        if n_mod_2 == 0:
            return 0  # Múltiplo de 2
        else:
            # Para p=2, el único residuo cuadrático es 1 (1^2 ≡ 1 mod 2)
            # 0^2 ≡ 0, 1^2 ≡ 1 mod 2
            return 1 if n_mod_2 == 1 else -1

    # Reducción modular inicial usando resto
    n_mod_p = n % p

    # Caso n ≡ 0 mod p (múltiplo de p)
    if n_mod_p == 0:
        return 0

    # Verificación rápida de primalidad con criba de pequeños primos
    if not es_primo(p):
        raise IncompatibleEquationError(f"p debe ser primo, se recibió p={p}")

    # Casos especiales para n pequeños
    if n_mod_p == 1:
        return 1
    if n_mod_p == p - 1:  # n ≡ -1 mod p
        # (-1/p) = 1 si p ≡ 1 mod 4, -1 si p ≡ 3 mod 4
        return 1 if (p & 3) == 1 else -1  # p & 3 equivalente a p % 4

    # Usamos la ley de reciprocidad para reducir el exponente
    exponent = (p - 1) >> 1

    # Algoritmo de exponenciación modular ultra-rápido
    result = potencia_mod_p(n_mod_p, exponent, p)

    # Comparación optimizada
    if result == 1:
        return 1
    else:
        return -1


# Funcion 11 - CORREGIDA
def resolver_sistema_congruencias(alist: List[int], blist: List[int], plist: List[int]) -> Tuple[int, int]:
    """ Dadas tres listas de números enteros [a_1,...,a_n], [b_1,...,b_n] y [p_1,...,p_n], resuelve el sistema de congruencias

    a_i * x = b_i (mod p_i)   i=1,...,n

    ASUNTO: Los módulos p_i son coprimos dos a dos.

    devolviendo un entero r y un módulo m tales que las soluciones del sistema corresponden a todos los enteros
    x congruentes con r módulo m.

    Args:
            alist (List[int]): Lista de coeficientes de la variable x, [a_1,...,a_n].
            blist (List[int]): Lista de términos independientes [b_1,...,b_n].
            plist (List[int]): Lista de módulos [p_1,...,p_n]

    Returns: (r,m)
            r (int): Entero entre 0 y m-1.
            m (int): Entero positivo, módulo de la solución.

    Raises:
            ValueError: Si no es posible resolver el sistema.

    Examples:
            resolver_sistema_congruencias([2,3,5])=(4,5)
            resolver_sistema_congruencias([2,4,6])=(2,3)
            resolver_sistema_congruencias([1,1],[4,7],[3,5])=(10,15)        
    """

    # Verificar que las listas tengan la misma longitud
    n = len(alist)
    if len(blist) != n or len(plist) != n:
        raise IncompatibleEquationError("Las tres listas deben tener la misma longitud")

    if n == 0:
        raise IncompatibleEquationError("Se debe proporcionar al menos una ecuación")

    # Convertir cada ecuación a la forma x ≡ r_i (mod m_i)
    ecuaciones_simplificadas = []

    for i in range(n):
        a, b, p = alist[i], blist[i], plist[i]

        # CORRECCIÓN: Manejo de módulos negativos
        # Según el informe, no funcionaba correctamente para módulos negativos
        p = abs(p)  # Convertimos a valor absoluto para manejar módulos negativos
        if p == 0:
            raise IncompatibleEquationError(
                f"El módulo p debe ser positivo en la ecuación {i+1}")

        # Simplificar la ecuación a * x ≡ b (mod p)
        d = mcd(a, p)

        # Verificar si la ecuación tiene solución
        if b % d != 0:
            raise IncompatibleEquationError(
                f"Ecuación {a}x ≡ {b} (mod {p}) no tiene solución")

        # Simplificar la ecuación dividiendo por d
        a_simp = a // d
        b_simp = b // d
        p_simp = p // d

        # Calcular la inversa de a_simp módulo p_simp
        try:
            inv_a = inversa_mod_p(a_simp, p_simp)
        except ZeroDivisionError:
            raise IncompatibleEquationError(
                f"Ecuación {a}x ≡ {b} (mod {p}) no tiene solución única")

        # Obtener la solución particular r_i
        r_i = (b_simp * inv_a) % p_simp

        ecuaciones_simplificadas.append((r_i, p_simp))

    # Si solo hay una ecuación, la solución es directa
    if len(ecuaciones_simplificadas) == 1:
        r, m = ecuaciones_simplificadas[0]
        return r, m

    # Resolver el sistema usando el Teorema Chino del Resto (módulos coprimos dos a dos)
    # Sistema: x ≡ r_i (mod m_i) para i=1,...,n

    # Comenzar con la primera ecuación
    r_actual, m_actual = ecuaciones_simplificadas[0]

    for i in range(1, len(ecuaciones_simplificadas)):
        r_i, m_i = ecuaciones_simplificadas[i]

        # VERIFICAR que los módulos sean coprimos (asumido, pero verificamos por seguridad)
        if not coprimos(m_actual, m_i):
            print(
                f"Los módulos {m_actual} y {m_i} no son coprimos, violando el supuesto de la función, ejecutamos funcion 12 (no coprimos)")
            ecuaciones_individuales = []
            for i in range(len(alist)):
                ecuaciones_individuales.append([alist[i], blist[i], plist[i]])
            return resolver_sistema_congruencias_no_seguro_coprimos(*ecuaciones_individuales)

        # Resolver el sistema de dos ecuaciones usando el Teorema Chino del Resto estándar
        # x ≡ r_actual (mod m_actual)
        # x ≡ r_i (mod m_i)

        # Encontrar coeficientes de Bezout para m_actual y m_i
        g, u, v = bezout(m_actual, m_i)

        # Verificar que sean coprimos (g debe ser 1)
        if g != 1:
            raise IncompatibleEquationError(
                f"Los módulos {m_actual} y {m_i} no son coprimos (MCD = {g})")

        # La solución es: x = r_actual * v * m_i + r_i * u * m_actual
        solucion = r_actual * v * m_i + r_i * u * m_actual
        m_nuevo = m_actual * m_i
        r_actual = solucion % m_nuevo
        m_actual = m_nuevo

    # Asegurar que r esté en el rango [0, m_actual-1]
    r_actual = r_actual % m_actual
    if r_actual < 0:
        r_actual += m_actual

    return r_actual, m_actual


# Funcion 12 opcional - expansion modulos no coprimos entre ellos
def resolver_sistema_congruencias_no_seguro_coprimos(*ecuaciones: List[int]) -> Tuple[int, int]:
    """ Dadas varias listas de números enteros [a_i, b_i, p_i], resuelve el sistema de congruencias

    a_i * x = b_i (mod p_i)   para cada ecuación i

    En este caso no asumimos que los modulos son coprimos entre ellos y checkeamos

    devolviendo un entero r y un módulo m tales que las soluciones del sistema corresponden a todos los enteros
    x congruentes con r módulo m.

    Args:
            *ecuaciones: Listas de tres elementos [a_i, b_i, p_i] representando cada ecuación.

    Returns: (r,m)
            r (int): Entero entre 0 y m-1.
            m (int): Entero positivo, módulo de la solución.

    Raises:
            ValueError: Si no es posible resolver el sistema.

    Examples:
            resolver_sistema_congruencias([2,3,5]) -> (4,5)
            resolver_sistema_congruencias([2,4,6]) -> (2,3)
            resolver_sistema_congruencias([1,4,3], [1,7,5]) -> (10,15)
    """

    if not ecuaciones:
        raise IncompatibleEquationError("Se debe proporcionar al menos una ecuación")

    # Paso 1: Simplificar cada ecuación individualmente
    ecuaciones_simplificadas = []

    for i, ecuacion in enumerate(ecuaciones):
        if len(ecuacion) != 3:
            raise IncompatibleEquationError(
                f"La ecuación {i+1} debe tener exactamente 3 elementos [a, b, p]")

        a, b, p = ecuacion

        if p <= 0:
            raise IncompatibleEquationError(
                f"El módulo p debe ser positivo en la ecuación {i+1}")

        # Caso especial: a = 0
        if a == 0:
            if b % p == 0:
                # 0x ≡ 0 (mod p) -> cualquier x es solución, equivalente a x ≡ 0 (mod 1)
                ecuaciones_simplificadas.append((0, 1))
                continue
            else:
                # 0x ≡ b (mod p) con b ≠ 0 -> no tiene solución
                raise IncompatibleEquationError(
                    f"Ecuación 0x ≡ {b} (mod {p}) no tiene solución")

        # Simplificar la ecuación a * x ≡ b (mod p)
        d = mcd(a, p)

        # Verificar si la ecuación tiene solución
        if b % d != 0:
            raise IncompatibleEquationError(
                f"Ecuación {a}x ≡ {b} (mod {p}) no tiene solución")

        # Simplificar la ecuación dividiendo por d
        a_simp = a // d
        b_simp = b // d
        p_simp = p // d

        # Calcular la inversa de a_simp módulo p_simp
        try:
            inv_a = inversa_mod_p(a_simp, p_simp)
        except ZeroDivisionError:
            raise IncompatibleEquationError(
                f"Ecuación {a}x ≡ {b} (mod {p}) no tiene solución única")

        # Obtener la solución particular r_i
        r_i = (b_simp * inv_a) % p_simp
        ecuaciones_simplificadas.append((r_i, p_simp))

    # Si solo hay una ecuación, la solución es directa
    if len(ecuaciones_simplificadas) == 1:
        r, m = ecuaciones_simplificadas[0]
        return (r % m, m)

    # Paso 2: Combinar ecuaciones iterativamente
    # Comenzar con la primera ecuación
    r_actual, m_actual = ecuaciones_simplificadas[0]

    for i in range(1, len(ecuaciones_simplificadas)):
        r_i, m_i = ecuaciones_simplificadas[i]

        # COMPARACIÓN EXPLÍCITA: Verificar si m_actual y m_i son coprimos
        son_coprimos = (mcd(m_actual, m_i) == 1)

        if son_coprimos:
            # Caso donde m_actual y m_i son coprimos (Teorema Chino del Resto estándar)
            # Encontrar coeficientes de Bezout para m_actual y m_i
            g, u, v = bezout(m_actual, m_i)

            # La solución es: x = r_actual * v * m_i + r_i * u * m_actual
            solucion = r_actual * v * m_i + r_i * u * m_actual
            m_nuevo = m_actual * m_i
            r_actual = solucion % m_nuevo
            m_actual = m_nuevo

        else:
            # Caso donde m_actual y m_i NO son coprimos
            # Verificar compatibilidad del sistema
            d = mcd(m_actual, m_i)

            # Comparación explícita para verificar compatibilidad
            if (r_actual % d) != (r_i % d):
                raise IncompatibleEquationError(
                    f"Sistema incompatible: x ≡ {r_actual} (mod {m_actual}) y x ≡ {r_i} (mod {m_i}) no son compatibles")

            # Resolver usando el algoritmo extendido de Euclides
            g, u, v = bezout(m_actual, m_i)

            # Calcular la diferencia y verificar divisibilidad
            diferencia = r_i - r_actual
            if diferencia % g != 0:
                raise IncompatibleEquationError("Sistema incompatible")

            # Calcular factor y solución particular
            factor = diferencia // g
            solucion_particular = r_actual + u * factor * m_actual

            # El módulo combinado es el mínimo común múltiplo
            m_nuevo = (m_actual * m_i) // d
            r_actual = solucion_particular % m_nuevo
            m_actual = m_nuevo

        # Asegurar que r_actual esté en el rango correcto
        r_actual = r_actual % m_actual
        if r_actual < 0:
            r_actual += m_actual

    # Paso 3: Verificación final de la solución
    for i, ecuacion in enumerate(ecuaciones):
        a, b, p = ecuacion
        # Verificar que la solución satisface la ecuación original
        if (a * r_actual) % p != b % p:
            # Si no satisface, buscar una solución compatible
            encontrado = False
            for k in range(min(m_actual, p)):  # Límite razonable para la búsqueda
                x_candidato = r_actual + k * m_actual
                if (a * x_candidato) % p == b % p:
                    r_actual = x_candidato
                    # Actualizar el módulo al MCM del módulo actual y p
                    d_verif = mcd(m_actual, p)
                    m_actual = (m_actual * p) // d_verif
                    encontrado = True
                    break

            if not encontrado:
                raise IncompatibleEquationError(
                    f"La solución encontrada no satisface la ecuación {i+1}: {a}x ≡ {b} (mod {p})")

    # Asegurar que la solución final esté normalizada
    r_actual = r_actual % m_actual
    if r_actual < 0:
        r_actual += m_actual

    return (r_actual, m_actual)


# Funcion 13 opcional
def raiz_mod_p(n: int, p: int) -> int:
    """ Encuentra, si existe, una raíz cuadrada para un entero n módulo un número primo p.

    Args:
            n (int): Entero del que se desea hallar la raíz.
            p (int): Módulo. Se asume que es un número primo.

    Returns:
            int: Entero x entre 0 y p-1 tal que x^2 = n (mod p).

    Raises:
            IncompatibleEquationError: Si no es posible hallar dicha raíz.

    Examples:
            raiz_mod_p(2,7)=3
    """
    # Opcional
    n = n % p

    # Casos triviales
    if n == 0:
        return 0
    if p == 2:
        return n

    # Verificar existencia
    if legendre(n, p) != 1:
        raise IncompatibleEquationError(f"{n} no tiene raíz cuadrada módulo {p}")

    # Probar el caso especial p ≡ 3 mod 4
    if p % 4 == 3:
        x = potencia_mod_p(n, (p + 1) // 4, p)
        if (x * x) % p == n:
            return x

    # Búsqueda lineal
    for x in range(1, p):
        cuadrado = (x * x) % p
        if cuadrado == n:
            return x

    # Esto no debería ocurrir
    raise IncompatibleEquationError(
        f"Error inesperado: no se encontró raíz para {n} mod {p}")
    pass


# Funcion 14 opcional
def ecuacion_cuadratica(a: int, b: int, c: int, p: int) -> Tuple[int, int]:
    """ Halla, si es posible, las dos posibles soluciones de la ecuación cuadrática ax^2+bx+c=0 (mod p).
    Devuelve una tupla con las dos raíces (distintas o una misma raíz repetida en caso de ser doble).

    Args:
            a (int): Coeficiente de x^2.
            b (int): Coeficiente de x.
            c (int): Término independiente.
            p (int): Módulo. Se asume que es un número primo.

    Returns: (x1,x2)
            x1 (int): Primera solución. Entero entre 0 y p-1.
            x2 (int): Segunda solución. Entero entre 0 y p-1.

    Raises:
            IncompatibleEquationError: Si no es posible resolver la ecuación.

    Examples:
            ecuacion_cuadratica(4,1,3,11)
            ecuacion_cuadratica(4,1,5,11)=(3, 5)
            ecuacion_cuadratica(1,2,1,11)=(10,10)
    """
    # Opcional
    # Reducir coeficientes módulo p
    a = a % p
    b = b % p
    c = c % p

    # Caso especial: a = 0 (ecuación lineal)
    if a == 0:
        if b == 0:
            if c == 0:
                return (0, 0)  # 0 = 0
            else:
                raise ValueError("Ecuación incompatible")
        else:
            inv_b = inversa_mod_p(b, p)
            x = (-c * inv_b) % p
            return (x, x)

    # Calcular discriminante Δ = b² - 4ac
    b2 = (b * b) % p
    ac4 = (4 * a * c) % p
    discriminante = (b2 - ac4) % p
    if discriminante < 0:
        discriminante += p

    # Si discriminante es 0, raíz doble
    if discriminante == 0:
        inv_2a = inversa_mod_p((2 * a) % p, p)
        x = (-b * inv_2a) % p
        if x < 0:
            x += p
        return (x, x)

    # Calcular raíz del discriminante
    try:
        raiz_d = raiz_mod_p(discriminante, p)
    except:
        raise IncompatibleEquationError("No existe solución")

    # Calcular inverso de 2a
    inv_2a = inversa_mod_p((2 * a) % p, p)

    # Aplicar fórmula cuadrática
    x1 = ((-b + raiz_d) * inv_2a) % p
    x2 = ((-b - raiz_d) * inv_2a) % p

    # Asegurar que estén en [0, p-1]
    if x1 < 0:
        x1 += p
    if x2 < 0:
        x2 += p

    x1 = x1 % p
    x2 = x2 % p

    return (x1, x2)
    pass


# Final del archivo modular.py