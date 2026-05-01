# test_excepciones.py
import pytest
from callejero import AdressNotFoundError, ServiceNotAvailableError

class TestExcepciones:
    """Tests para las excepciones personalizadas"""
    
    def test_adress_not_found_error(self):
        """Test para AdressNotFoundError"""
        mensaje = "Dirección no encontrada"
        error = AdressNotFoundError(mensaje)
        
        assert str(error) == mensaje
        assert isinstance(error, Exception)
    
    def test_service_not_available_error(self):
        """Test para ServiceNotAvailableError"""
        mensaje = "Servicio no disponible"
        error = ServiceNotAvailableError(mensaje)
        
        assert str(error) == mensaje
        assert isinstance(error, Exception)
    
    def test_excepciones_herencia(self):
        """Test que verifica la jerarquía de herencia"""
        assert issubclass(AdressNotFoundError, Exception)
        assert issubclass(ServiceNotAvailableError, Exception)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])