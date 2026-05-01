import pytest
import modular
from test_imatlab import try_command

@pytest.mark.parametrize("n,salida_esperada",[
    (2,True),
    (3,True),
    (4,False),
    (5,True),
    #(0,COMPLETAR),
    #(1,COMPLETAR),
    #(-1,COMPLETAR),
    #COMPLETAR
])
def test_es_primo_basico(n: int, salida_esperada: bool) -> None:
    assert(modular.es_primo(n)==salida_esperada)

@pytest.mark.parametrize("n,salida_esperada",[
    (4,"No"),
    (5,"Sí"),
    #(0,COMPLETAR),
    #(1,COMPLETAR),
    #(-1,COMPLETAR),
    #COMPLETAR
])
def test_es_primo_imatlab(n: int, salida_esperada: str) -> None:
    try_command(f"primo({n})",salida_esperada)