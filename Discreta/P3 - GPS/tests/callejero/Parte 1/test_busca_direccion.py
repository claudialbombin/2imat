# test_busca_direccion.py
import pytest
import pandas as pd
from callejero import busca_direccion, carga_callejero, AdressNotFoundError

# Fixture para cargar el callejero una vez
@pytest.fixture(scope="module")
def callejero():
    return carga_callejero()

class TestBuscaDireccion:
    """Tests para la función busca_direccion"""
    
    def test_busca_direccion_existente(self, callejero):
        """Test que verifica la búsqueda de una dirección existente"""
        lat, lon = busca_direccion("ABAD JUAN CATALAN, 1", callejero)
        
        # Verificar que se devuelven coordenadas válidas
        assert isinstance(lat, float)
        assert isinstance(lon, float)
        
        # Verificar que están en rangos razonables para Madrid
        assert 40.0 <= lat <= 41.0
        assert -4.0 <= lon <= -3.0
    
    def test_busca_direccion_insensible_mayusculas(self, callejero):
        """Test que verifica que la búsqueda es insensible a mayúsculas/minúsculas"""
        lat1, lon1 = busca_direccion("abad juan catalan, 1", callejero)
        lat2, lon2 = busca_direccion("ABAD JUAN CATALAN, 1", callejero)
        
        # Deberían devolver las mismas coordenadas
        assert lat1 == lat2
        assert lon1 == lon2
    
    def test_busca_direccion_insensible_acentos(self, callejero):
        """Test que verifica que la búsqueda es insensible a acentos"""
        lat1, lon1 = busca_direccion("ABAD JUAN CATALAN, 1", callejero)
        lat2, lon2 = busca_direccion("ABAD JUAN CATALÁN, 1", callejero)
        
        # Deberían devolver las mismas coordenadas
        assert lat1 == lat2
        assert lon1 == lon2
    
    def test_busca_direccion_con_espacios(self, callejero):
        """Test que verifica que la búsqueda maneja correctamente los espacios"""
        lat1, lon1 = busca_direccion("ABAD JUAN CATALAN, 1", callejero)
        lat2, lon2 = busca_direccion("  ABAD   JUAN   CATALAN  ,  1  ", callejero)
        
        # Deberían devolver las mismas coordenadas
        assert lat1 == lat2
        assert lon1 == lon2
    
    def test_busca_direccion_no_existente(self, callejero):
        """Test que verifica que se lanza excepción para dirección no existente"""
        with pytest.raises(AdressNotFoundError):
            busca_direccion("CALLE INEXISTENTE, 999", callejero)
    
    def test_busca_direccion_multiple_numeros(self, callejero):
        """Test que verifica la búsqueda de diferentes números en la misma calle"""
        # Probar con varios números que deberían existir
        numeros_prueba = ["1", "10", "20"]
        coordenadas = []
        
        for numero in numeros_prueba:
            try:
                lat, lon = busca_direccion(f"ABAD JUAN CATALAN, {numero}", callejero)
                coordenadas.append((lat, lon))
            except AdressNotFoundError:
                # Algunos números pueden no existir, eso es aceptable
                continue
        
        # Verificar que al menos encontramos algunas coordenadas
        assert len(coordenadas) > 0
        
        # Verificar que todas las coordenadas son únicas (diferentes números)
        coordenadas_unicas = set(coordenadas)
        assert len(coordenadas_unicas) == len(coordenadas)
    
    def test_busca_direccion_diferentes_formatos(self, callejero):
        """Test que verifica diferentes formatos de entrada"""
        formatos_prueba = [
            "ABAD JUAN CATALAN, 1",
            "ABAD JUAN CATALAN 1",
            "CALLE ABAD JUAN CATALAN, 1",
        ]
        
        coordenadas_encontradas = []
        
        for formato in formatos_prueba:
            try:
                lat, lon = busca_direccion(formato, callejero)
                coordenadas_encontradas.append((lat, lon))
            except AdressNotFoundError:
                # Algunos formatos pueden no funcionar
                continue
        
        # Al menos un formato debería funcionar
        assert len(coordenadas_encontradas) > 0
    
    def test_busca_direccion_autovias(self, callejero):
        """Test que verifica la búsqueda de autovías"""
        # Probar con algunas autovías que deberían estar en el dataset
        autovias_prueba = ["A-1", "A-2", "A-3"]
        
        for autovia in autovias_prueba:
            try:
                # Buscar por kilómetro 10000 que aparece en los datos
                lat, lon = busca_direccion(f"{autovia}, 10000", callejero)
                assert isinstance(lat, float)
                assert isinstance(lon, float)
                break  # Si una funciona, es suficiente
            except AdressNotFoundError:
                continue
        else:
            pytest.skip("No se encontraron autovías en el dataset")

class TestBuscaDireccionErrores:
    """Tests de manejo de errores para busca_direccion"""
    
    def test_busca_direccion_vacia(self, callejero):
        """Test que verifica el manejo de dirección vacía"""
        with pytest.raises(AdressNotFoundError):
            busca_direccion("", callejero)
    
    def test_busca_direccion_solo_espacios(self, callejero):
        """Test que verifica el manejo de dirección con solo espacios"""
        with pytest.raises(AdressNotFoundError):
            busca_direccion("   ", callejero)
    
    def test_busca_direccion_sin_numero(self, callejero):
        """Test que verifica el manejo de dirección sin número"""
        with pytest.raises(AdressNotFoundError):
            busca_direccion("ABAD JUAN CATALAN", callejero)
    
    def test_busca_direccion_numero_invalido(self, callejero):
        """Test que verifica el manejo de número inválido"""
        with pytest.raises(AdressNotFoundError):
            busca_direccion("ABAD JUAN CATALAN, ABC", callejero)

class TestBuscaDireccionIntegracion:
    """Tests de integración para busca_direccion"""
    
    def test_consistencia_busquedas_multiples(self, callejero):
        """Test que verifica la consistencia en búsquedas múltiples"""
        # Buscar la misma dirección múltiples veces
        coordenadas = []
        for _ in range(3):
            lat, lon = busca_direccion("ABAD JUAN CATALAN, 1", callejero)
            coordenadas.append((lat, lon))
        
        # Todas las búsquedas deberían devolver las mismas coordenadas
        for i in range(1, len(coordenadas)):
            assert coordenadas[0] == coordenadas[i]
    
    def test_flujo_completo_carga_y_busqueda(self):
        """Test del flujo completo: carga + búsqueda"""
        # Cargar callejero
        callejero = carga_callejero()
        assert len(callejero) > 0
        
        # Buscar dirección
        lat, lon = busca_direccion("ABAD JUAN CATALAN, 1", callejero)
        
        # Verificar resultados
        assert isinstance(lat, float)
        assert isinstance(lon, float)
        assert 40.0 <= lat <= 41.0
        assert -4.0 <= lon <= -3.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])