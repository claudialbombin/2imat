# test_carga_callejero.py
import pytest
import pandas as pd
import os
from callejero import carga_callejero

class TestCargaCallejero:
    """Tests para la función carga_callejero"""
    
    def test_carga_callejero_estructura(self):
        """Test que verifica la estructura del DataFrame devuelto"""
        df = carga_callejero()
        
        # Verificar que se devuelve un DataFrame
        assert isinstance(df, pd.DataFrame)
        
        # Verificar las columnas esperadas
        columnas_esperadas = ["VIA_CLASE", "VIA_PAR", "VIA_NOMBRE", "NUMERO", "LATITUD", "LONGITUD"]
        for columna in columnas_esperadas:
            assert columna in df.columns
    
    def test_carga_callejero_no_vacio(self):
        """Test que verifica que el DataFrame no está vacío"""
        df = carga_callejero()
        assert len(df) > 0
    
    def test_carga_callejero_coordenadas_numericas(self):
        """Test que verifica que las coordenadas son numéricas"""
        df = carga_callejero()
        
        assert pd.api.types.is_numeric_dtype(df['LATITUD'])
        assert pd.api.types.is_numeric_dtype(df['LONGITUD'])
    
    def test_carga_callejero_rangos_coordenadas(self):
        """Test que verifica que las coordenadas están en rangos razonables para Madrid"""
        df = carga_callejero()
        
        # Madrid está aproximadamente entre 40.3 y 40.5 de latitud, y -3.9 y -3.5 de longitud
        assert df['LATITUD'].between(40.0, 41.0).all()
        assert df['LONGITUD'].between(-4.0, -3.0).all()
    
    def test_carga_callejero_tipos_datos(self):
        """Test que verifica los tipos de datos de las columnas"""
        df = carga_callejero()
        
        # Verificar tipos de datos básicos
        assert pd.api.types.is_string_dtype(df['VIA_CLASE'])
        assert pd.api.types.is_string_dtype(df['VIA_NOMBRE'])
        assert pd.api.types.is_numeric_dtype(df['NUMERO'])
    
    def test_carga_callejero_valores_no_nulos(self):
        """Test que verifica que las columnas críticas no tienen valores nulos"""
        df = carga_callejero()
        
        # Columnas que no deberían tener valores nulos
        columnas_criticas = ['VIA_NOMBRE', 'NUMERO', 'LATITUD', 'LONGITUD']
        for columna in columnas_criticas:
            assert not df[columna].isnull().all(), f"La columna {columna} no debería estar completamente vacía"
    
    def test_carga_callejero_ejemplos_concretos(self):
        """Test que verifica algunos ejemplos concretos del dataset"""
        df = carga_callejero()
        
        # Verificar que existen algunas calles conocidas
        calles_esperadas = ['A-1', 'A-2', 'A-3', 'ABAD JUAN CATALAN']
        calles_encontradas = df['VIA_NOMBRE'].unique()
        
        # Al menos algunas de las calles esperadas deberían estar presentes
        calles_presentes = [calle for calle in calles_esperadas if calle in calles_encontradas]
        assert len(calles_presentes) > 0, "No se encontraron calles esperadas en el dataset"
    
    def test_carga_callejero_archivo_inexistente(self):
        """Test que verifica el manejo de archivo inexistente"""
        # Guardar el nombre original
        from callejero import STREET_FILE_NAME
        nombre_original = STREET_FILE_NAME
        
        try:
            # Cambiar temporalmente el nombre para simular archivo no encontrado
            import callejero
            callejero.STREET_FILE_NAME = "archivo_inexistente.csv"
            
            # Debería lanzar FileNotFoundError
            with pytest.raises(FileNotFoundError):
                carga_callejero()
                
        finally:
            # Restaurar el nombre original
            import callejero
            callejero.STREET_FILE_NAME = nombre_original

if __name__ == "__main__":
    pytest.main([__file__, "-v"])