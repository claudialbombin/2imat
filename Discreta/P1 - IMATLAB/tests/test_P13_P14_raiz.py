import pytest
import modular
from test_imatlab import try_command

@pytest.mark.parametrize("n,p,salida_esperada1,salida_esperada2",[
    (2,7,3,4),
    #COMPLETAR    
])
def test_raiz_mod_p_basico(n: int, p:int, salida_esperada1: int, salida_esperada2: int) -> None:
    assert(modular.raiz_mod_p(n,p)%p==salida_esperada1 or modular.raiz_mod_p(n,p)%p==salida_esperada2)


def test_raiz_mod_p_no_existe():
    """ Este test comprueba que, en los casos esperados,
    realmente se lanza la excepción esperada"""
    with pytest.raises(modular.IncompatibleEquationError):
        modular.raiz_mod_p(2,5)
    #COMPLETAR con otros casos en que n no tenga raíz mod p

@pytest.mark.parametrize("n,p,salida_esperada",[    
    (2,5,"NE"),
    (2,7,"3, 4"),
    (9,3,"0, 0"),
    #COMPLETAR 
])
def test_inversa_imatlab(n: int, p:int, salida_esperada: str) -> None:
    try_command(f"raiz({n},{p})",salida_esperada)



@pytest.mark.parametrize("a,b,c,p,salida_esperada1,salida_esperada2",[
    (4,1,5,11, 3,5),
    (1,2,1,11,10,10),
    #COMPLETAR    
])
def test_ecuacion_cuadratica_basico(a:int, b:int, c: int, p:int, salida_esperada1: int, salida_esperada2: int) -> None:
    assert(modular.ecuacion_cuadratica(a,b,c,p)==(salida_esperada1,salida_esperada2) or modular.ecuacion_cuadratica(a,b,c,p)==(salida_esperada2,salida_esperada1))

@pytest.mark.parametrize("a,b,c,p",[
    (4,1,3,11),
    #COMPLETAR con otros casos en que n no tenga solución mod p 
])
def test_ecuacion_cuadratica_no_existe(a:int, b:int, c: int, p:int) -> None:
    """ Este test comprueba que, en los casos esperados,
    realmente se lanza la excepción esperada"""
    with pytest.raises(modular.IncompatibleEquationError):
        modular.ecuacion_cuadratica(a,b,c,p)

@pytest.mark.parametrize("a,b,c,p,salida_esperada",[    
    (4,1,5,11, "3, 5"),
    (1,2,1,11,"10"),
    (4,1,3,11,"NE"),
    #COMPLETAR 
])
def test_inversa_imatlab(a:int, b:int, c: int, p:int, salida_esperada: str) -> None:
    try_command(f"ecCuadratica({a},{b},{c},{p})",salida_esperada)
