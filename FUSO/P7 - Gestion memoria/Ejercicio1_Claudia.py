import numpy as np
import sys
# Apartado 1

# Declaramos las variables para luego estudiar su tamano real

a_bool = np.bool_("True")
b_int8 = np.int8(5)
c_int16 = np.int16(300)
d_int32 = np.int32(70000)
e_int64 = np.int64(5000000000)
f_float16 = np.float16(3.14)
g_float32 = np.float32(2.71828)
h_float64 = np.float64(1.6180339887)
i_complex64 = np.complex64(1 + 2j)
j_complex128 = np.complex128(3 + 4j)

# Imprimimos el tamaño en bytes de cada variable
print(f"Tamaño de a_bool (bool): {a_bool.nbytes} bytes")
print(f"Tamaño de b_int8 (int8): {b_int8.nbytes} bytes")
print(f"Tamaño de c_int16 (int16): {c_int16.nbytes} bytes")
print(f"Tamaño de d_int32 (int32): {d_int32.nbytes} bytes")
print(f"Tamaño de e_int64 (int64): {e_int64.nbytes} bytes")
print(f"Tamaño de f_float16 (float16): {f_float16.nbytes} bytes")
print(f"Tamaño de g_float32 (float32): {g_float32.nbytes} bytes")
print(f"Tamaño de h_float64 (float64): {h_float64.nbytes} bytes")
print(f"Tamaño de i_complex64 (complex64): {i_complex64.nbytes} bytes")
print(f"Tamaño de j_complex128 (complex128): {j_complex128.nbytes} bytes")

# Apartado 2

# Unicode ('U') suele usar 4 bytes por carácter en numpy
arr_u1 = np.array(['a'], dtype='U1')
arr_u5 = np.array(['abcde'], dtype='U5')
print(f"U1: itemsize = {arr_u1.dtype.itemsize} bytes ; nbytes = {arr_u1.nbytes}")
print(f"U5: itemsize = {arr_u5.dtype.itemsize} bytes ; nbytes = {arr_u5.nbytes}")

# Bytes ('S') usa 1 byte por carácter.
arr_s1 = np.array([b'a'], dtype='S1')
arr_s5 = np.array([b'abcde'], dtype='S5')
print(f"S1: itemsize = {arr_s1.dtype.itemsize} bytes ; nbytes = {arr_s1.nbytes}")
print(f"S5: itemsize = {arr_s5.dtype.itemsize} bytes ; nbytes = {arr_s5.nbytes}")

# Comparación rápida con dtype=object (apunta a objetos python, la memoria real de la cadena no está incluida en array.nbytes)
arr_obj1 = np.array(['a'], dtype=object)
arr_obj5 = np.array(['abcde'], dtype=object)
print(f"object (1): array.nbytes = {arr_obj1.nbytes}")
print(f"object (5): array.nbytes = {arr_obj5.nbytes}")

# ¿Cuál crees que será el mejor tipo para crear un array de strings?
# 
# - Con dtype='U' (Unicode) numpy suele usar 4 bytes por carácter: U1 ≈ 4 bytes, U5 ≈ 20 bytes.
# - Con dtype='S' (bytes) numpy usa 1 byte por carácter: S1 = 1 byte, S5 = 5 bytes.
# - dtype='S' es más eficiente en memoria para texto, quiza sea mejro usarlo para ocupar menos espacio en la memoria.

# Apartado 3

# getsizeof: python vs numpy escalares
py_int = 5
print(f"Python int sys.getsizeof:", sys.getsizeof(py_int))
print(f"np.int32 itemsize:", np.int32(5).nbytes)
print(f"np.int64 itemsize:", np.int64(5).nbytes)

py_float = 3.14
print(f"Python float sys.getsizeof:", sys.getsizeof(py_float))
print(f"np.float32 itemsize:", np.float32(py_float).nbytes)
print(f"np.float64 itemsize:", np.float64(py_float).nbytes)

# strings en python
s1_py = 'a'
s5_py = 'abcde'
print(f"Python str 'a' sys.getsizeof:", sys.getsizeof(s1_py))
print(f"Python str 'abcde' sys.getsizeof:", sys.getsizeof(s5_py))

# Utilizando ahora getsizeof de la librería de sys, comprueba con qué tipo
# de entero de numpy se corresponde un entero de Python. Repite lo mismo
# para un float. ¿Cuánto ocupa en Python un string de 1 carácter y un
# string de 5 caracteres?
#
# - Un int de python es un objeto de precisión arbitraria (en CPython 64-bit suele ocupar ~28 bytes),
#   mientras que los tipos numpy tienen tamaños fijos: int32 = 4 bytes, int64 = 8 bytes.
#   No hay equivalencia exacta; si necesitamos fijar un tipo de intbit debemos usar numpy para fijar el tipo.
# - Un float de python (CPython) ocupa ~24 bytes como objeto; np.float32 ocupa 4 bytes y np.float64 8 bytes.
# - Un str en python tiene overhead: 'a' y 'abcde' ocupan decenas de bytes (por ejemplo ~42 y ~46 bytes en este caso),
#   mucho más que 1 y 5 bytes en un array numpy dtype='S'. Uso dtype='S' para ahorrar memoria.
