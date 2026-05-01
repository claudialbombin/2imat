import pytest
import modular
import rsa


@pytest.mark.parametrize("rnd",range(10))
def test_generar_claves(rnd:int) -> None:
    (n,e,d)=rsa.generar_claves(1000,10000)
    assert(e*d%modular.euler(n)==1)

@pytest.mark.parametrize("n,e,d",[
    (809570247883,77204266853,42840500717),
])
def test_romper_clave(n:int,e:int, d: int) -> None:
    assert(rsa.romper_clave(n,e)==d)

@pytest.mark.parametrize("rnd",range(10))
def test_generar_romper_claves(rnd:int) -> None:
    (n,e,d)=rsa.generar_claves(1000,10000)
    assert(rsa.romper_clave(n,e)==d)