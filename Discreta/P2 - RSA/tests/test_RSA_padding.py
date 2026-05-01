import pytest
import rsa

@pytest.mark.parametrize("m,digitos_padding,salida_esperada",[
    (2454,1,245),
    (2454,2,24),
    (2454,3,2),
    (2432,2,24),
    (2432,0,2432),
])
def test_eliminar_padding(m:int,digitos_padding:int, salida_esperada: int) -> None:
    assert(rsa.eliminar_padding(m,digitos_padding)==salida_esperada)

@pytest.mark.parametrize("m,digitos_padding",[
    (m,digitos_padding) for m in range(10) for digitos_padding in range(3)
])
def test_aplicar_padding(m:int,digitos_padding:int) -> None:
    assert(rsa.eliminar_padding(rsa.aplicar_padding(m,digitos_padding),digitos_padding)==m)