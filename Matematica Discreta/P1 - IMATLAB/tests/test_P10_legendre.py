import pytest
import modular
from test_imatlab import try_command

@pytest.mark.parametrize("n,p,salida_esperada",[
    (2,5,-1),
    (2,7,1),
    (10,5,0),
    #COMPLETAR    
])
def test_legendre_basico(n: int, p:int, salida_esperada: int) -> None:
    assert(modular.legendre(n,p)==salida_esperada)


def test_legendre_cero():
    """ Este test comprueba que, en los casos esperados,
    realmente se lanza la excepción esperada"""
    with pytest.raises(ZeroDivisionError):
        modular.legendre(2,0)
    #COMPLETAR con un caso en que n no sea invertible mod p

@pytest.mark.parametrize("n,p,salida_esperada",[    
    (2,5,"-1"),
    (2,7,"1"),
    (10,5,"0"),
    (2,0,"NE"),
    #COMPLETAR 
])
def test_inversa_imatlab(n: int, p:int, salida_esperada: str) -> None:
    try_command(f"legendre({n},{p})",salida_esperada)