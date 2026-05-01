import pytest
import imatlab
from io import StringIO

def try_command(command:str, expected_output: str) -> None:
    input=StringIO(command+"\n")
    output=StringIO()
    imatlab.run_commands(input,output)
    assert(output.getvalue()==expected_output+"\n")

@pytest.mark.parametrize("command,expected_output",[
    ("primo(7)", "Sí"),
    ("primo(12)", "No"),
    ("primo(-2)", "No"),
    ("primos(5,100)", "5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97"),
    ("factorizar(8)", "2: 3"),
    ("mcd(1,20)", "1"),
    ("coprimos(5,3)", "Sí"),
    ("coprimos(6,9)", "No"),
    ("pow(2,5,3)", "2"),
    ("pow(-3,-8,7)", "4"),
    ("pow(100,100,3)", "1"),
    ("inv(3,7)", "5"),
    ("inv(3,9)", "NE"),
    ("euler(10)", "4"),
    ("legendre(10,3)", "1"),
    ("Legendre(10,3)", "NOP"),
    ("resolverSistema([1;1;3],[4;7;11])", "10 (mod 33)"),
    ("raiz(-1,5)", "2, 3"),
    ("ecCuadratica(4,1,3,11)", "NE"),
    ("ecCuadratica(4,1,5,11)", "3, 5"),
    ("ecCuadratica(1,2,1,11)", "10"),
])
def test_imatlab_basico(command:str,expected_output:str)-> None:
    try_command(command,expected_output)