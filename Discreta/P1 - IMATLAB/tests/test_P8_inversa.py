import pytest
import modular
from test_imatlab import try_command

@pytest.mark.parametrize("n,p,salida_esperada",[
    (2,7,4),
    #COMPLETAR    
])
def test_inversa_mod_p_basico(n: int, p:int, salida_esperada: int) -> None:
    assert(modular.inversa_mod_p(n,p)==salida_esperada)


def test_potencia_mod_p_cero():
    """ Este test comprueba que, en los casos esperados,
    realmente se lanza la excepción esperada"""
    with pytest.raises(ZeroDivisionError):
        modular.inversa_mod_p(2,0)
    #COMPLETAR con un caso en que n no sea invertible mod p

@pytest.mark.parametrize("n,p,salida_esperada",[    
    (2,7,"4"),
    (2,0,"NE")
    #COMPLETAR 
])
def test_inversa_imatlab(n: int, p:int, salida_esperada: str) -> None:
    try_command(f"inv({n},{p})",salida_esperada)