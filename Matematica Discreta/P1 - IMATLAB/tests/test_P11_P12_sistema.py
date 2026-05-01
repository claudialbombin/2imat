from typing import List, Tuple
import pytest
import modular
from test_imatlab import try_command

@pytest.mark.parametrize("alist,blist,plist,salida_esperada",[
    ([2],[3],[5],(4,5)),
    ([2],[4],[6],(2,3)),
    ([1,4],[1,7],[3,11],(10,33)),
    #COMPLETAR
])
def test_factorizar_basico(alist:List[int],blist:List[int],plist:List[int], salida_esperada: Tuple[int,int]) -> None:
    assert(modular.resolver_sistema_congruencias(alist,blist,plist)==salida_esperada)


@pytest.mark.parametrize("alist,blist,plist,salida_esperada",[
    ([2],[4],[6],(2,3)),
    ([1,4],[1,7],[3,11],(10,33)),
    #COMPLETAR
])
def test_factorizar_no_coprimo(alist:List[int],blist:List[int],plist:List[int], salida_esperada: Tuple[int,int]) -> None:
    assert(modular.resolver_sistema_congruencias(alist,blist,plist)==salida_esperada)


@pytest.mark.parametrize("alist,blist,plist",[
    ([2],[3],[4]),
    ([1,1],[1,2],[5,5]),
    #COMPLETAR
])
def test_sistema_incompatible(alist:List[int],blist:List[int],plist:List[int]):
    """ Este test comprueba que, en los casos esperados,
    realmente se lanza la excepción esperada"""
    with pytest.raises(modular.IncompatibleEquationError):
        modular.resolver_sistema_congruencias(alist,blist,plist)
    #COMPLETAR con un caso en que n no sea invertible mod p

@pytest.mark.parametrize("comando,salida_esperada",[
    ("resolverSistema([2;4;6])", "2 (mod 3)"),
    ("resolverSistema([1;1;3],[4;7;11])", "10 (mod 33)")
    #COMPLETAR
])
def test_resolverSistema_imatlab(comando:str, salida_esperada: str) -> None:
    try_command(comando,salida_esperada)