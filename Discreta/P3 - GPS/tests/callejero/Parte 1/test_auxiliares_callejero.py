# test_auxiliares.py
import pytest
import pandas as pd
import re
from callejero import normalizar_texto, convertir_coordenadas, convertir_coordenadas_floats

class TestNormalizarTexto:
    """Tests para la función normalizar_texto"""
    
    def test_normalizar_texto_basico(self):
        assert normalizar_texto("Calle Mayor") == "CALLE MAYOR"
    
    def test_normalizar_texto_acentos(self):
        assert normalizar_texto("Calle de Alcalá") == "CALLE DE ALCALA"
        assert normalizar_texto("CÀLLÉ MÀYÖR") == "CALLE MAYOR"
    
    def test_normalizar_texto_espacios(self):
        assert normalizar_texto("  Calle   del  Prado  ") == "CALLE DEL PRADO"
    
    def test_normalizar_texto_varios_acentos(self):
        test_cases = [
            ("ÁÉÍÓÚ", "AEIOU"),
            ("ÀÈÌÒÙ", "AEIOU"),
            ("ÄËÏÖÜ", "AEIOU"),
            ("áéíóú", "AEIOU")
        ]
        for input_str, expected in test_cases:
            assert normalizar_texto(input_str) == expected

class TestConvertirCoordenadas:
    """Tests para la función convertir_coordenadas"""
    
    def test_convertir_coordenadas_latitud_norte(self):
        resultado = convertir_coordenadas("40°29'21.84'' N")
        assert pytest.approx(resultado, 0.001) == 40.4894
    
    def test_convertir_coordenadas_longitud_oeste(self):
        resultado = convertir_coordenadas("3°40'23.56'' W")
        assert pytest.approx(resultado, 0.001) == -3.6732
    
    def test_convertir_coordenadas_latitud_sur(self):
        resultado = convertir_coordenadas("40°29'21.84'' S")
        assert pytest.approx(resultado, 0.001) == -40.4894
    
    def test_convertir_coordenadas_longitud_este(self):
        resultado = convertir_coordenadas("3°40'23.56'' E")
        assert pytest.approx(resultado, 0.001) == 3.6732
    
    def test_convertir_coordenadas_ya_decimal(self):
        assert convertir_coordenadas(40.4894) == 40.4894
        assert convertir_coordenadas(-3.6732) == -3.6732
    
    def test_convertir_coordenadas_formato_alternativo(self):
        resultado = convertir_coordenadas("40º29'21.84\" N")
        assert pytest.approx(resultado, 0.001) == 40.4894
    
    def test_convertir_coordenadas_invalida(self):
        with pytest.raises(ValueError):
            convertir_coordenadas("formato_invalido")

class TestConvertirCoordenadasFloats:
    """Tests para la función convertir_coordenadas_floats"""
    
    def test_convertir_coordenadas_floats_latitud(self):
        series = pd.Series([
            "40°29'21.84'' N", 
            "40°30'00.00'' N", 
            "40°28'15.00'' S"
        ])
        resultado = convertir_coordenadas_floats(series, ['N', 'S'])
        expected = [40.4894, 40.5, -40.470833]
        
        for res, exp in zip(resultado, expected):
            assert pytest.approx(res, 0.001) == exp
    
    def test_convertir_coordenadas_floats_longitud(self):
        series = pd.Series([
            "3°40'23.56'' W", 
            "3°41'00.00'' E", 
            "3°39'15.00'' W"
        ])
        resultado = convertir_coordenadas_floats(series, ['E', 'W'])
        expected = [-3.6732, 3.683333, -3.654167]
        
        for res, exp in zip(resultado, expected):
            assert pytest.approx(res, 0.001) == exp
    
    def test_convertir_coordenadas_floats_vacios(self):
        series = pd.Series(["40°29'21.84'' N", "", "40°30'00.00'' N"])
        resultado = convertir_coordenadas_floats(series, ['N', 'S'])
        
        assert len(resultado) == 3
        assert resultado[1] is None
        assert pytest.approx(resultado[0], 0.001) == 40.4894
    
    def test_convertir_coordenadas_floats_formato_invalido(self):
        series = pd.Series(["40°29'21.84'' N", "formato_invalido", "40°30'00.00'' N"])
        
        with pytest.raises(ValueError, match="formato.*no es correcto"):
            convertir_coordenadas_floats(series, ['N', 'S'])

if __name__ == "__main__":
    pytest.main([__file__, "-v"])