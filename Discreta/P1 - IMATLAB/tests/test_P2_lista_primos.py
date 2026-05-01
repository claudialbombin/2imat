from typing import List
import pytest
import modular
from test_imatlab import try_command

@pytest.mark.parametrize("a,b,salida_esperada",[
    (1,11,[2,3,5,7]),
    (8,10,[]),
    #COMPLETAR
])
def test_lista_primos_basico(a: int, b:int, salida_esperada: List[int]) -> None:
    assert(modular.lista_primos(a,b)==salida_esperada)

@pytest.mark.parametrize("a,b,salida_esperada",[
    (1,11,"2, 3, 5, 7"),
    (8,10,"NE"),
    #COMPLETAR
])
def test_lista_primos_imatlab(a:int, b:int, salida_esperada: str) -> None:
    try_command(f"primos({a},{b})",salida_esperada)