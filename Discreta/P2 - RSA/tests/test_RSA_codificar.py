import pytest
import rsa


def test_codificar_cadena() -> None:
    assert(rsa.codificar_cadena("¡Hola mundo!")==[161, 72, 111, 108, 97, 32, 109, 117, 110, 100, 111, 33])

def test_decodificar_cadena() -> None:
    assert(rsa.decodificar_cadena([161, 72, 111, 108, 97, 32, 109, 117, 110, 100, 111, 33])=="¡Hola mundo!")