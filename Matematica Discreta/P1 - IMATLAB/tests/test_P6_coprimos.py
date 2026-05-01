import pytest
import modular
from test_imatlab import try_command

@pytest.mark.parametrize("a,b,salida_esperada",[
    (14,20,False),
    (14,15,True),
    #COMPLETAR    
])
def test_coprimos_basico(a: int, b:int, salida_esperada: bool) -> None:
    assert(modular.coprimos(a,b)==salida_esperada)


@pytest.mark.parametrize("a,b,salida_esperada",[    
    (14,20,"No"),
    (14,15,"Sí"),
    #COMPLETAR
])
def test_coprimos_imatlab(a:int, b: int, salida_esperada: str) -> None:
    try_command(f"coprimos({a},{b})",salida_esperada)