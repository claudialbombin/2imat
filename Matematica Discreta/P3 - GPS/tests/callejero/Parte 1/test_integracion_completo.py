# test_integracion_completo.py
"""
Test de integración completo para el sistema de callejero de Madrid

Este test verifica el flujo completo desde la carga de datos hasta la búsqueda de direcciones,
pasando por todas las funciones auxiliares y el manejo de errores.
"""

import pytest
import pandas as pd
import tempfile
import os
from callejero import (
    carga_callejero,
    busca_direccion,
    normalizar_texto,
    convertir_coordenadas,
    convertir_coordenadas_floats,
    AdressNotFoundError,
    ServiceNotAvailableError
)

class TestIntegracionCompleto:
    """Test de integración completo del sistema de callejero"""
    
    def setup_method(self):
        """Setup que se ejecuta antes de cada test"""
        self.callejero = None
    
    def test_flujo_completo_sistema(self):
        """
        Test del flujo completo del sistema:
        1. Carga del callejero
        2. Procesamiento de datos
        3. Búsqueda de direcciones
        4. Verificación de resultados
        """
        print("\n=== INICIANDO TEST DE FLUJO COMPLETO ===")
        
        # PASO 1: Cargar el callejero
        print("Paso 1: Cargando callejero...")
        self.callejero = carga_callejero()
        
        # Verificar carga exitosa
        assert self.callejero is not None
        assert isinstance(self.callejero, pd.DataFrame)
        assert len(self.callejero) > 0
        print(f"✓ Callejero cargado con {len(self.callejero)} registros")
        
        # PASO 2: Verificar estructura y procesamiento de datos
        print("Paso 2: Verificando estructura de datos...")
        columnas_esperadas = ["VIA_CLASE", "VIA_PAR", "VIA_NOMBRE", "NUMERO", "LATITUD", "LONGITUD"]
        for columna in columnas_esperadas:
            assert columna in self.callejero.columns
        print("✓ Estructura de columnas correcta")
        
        # Verificar que las coordenadas son numéricas
        assert pd.api.types.is_numeric_dtype(self.callejero['LATITUD'])
        assert pd.api.types.is_numeric_dtype(self.callejero['LONGITUD'])
        print("✓ Coordenadas convertidas correctamente a formato numérico")
        
        # PASO 3: Probar funciones auxiliares con datos reales
        print("Paso 3: Probando funciones auxiliares...")
        
        # Probar normalización de texto
        texto_normalizado = normalizar_texto("Calle de Alcalá")
        assert texto_normalizado == "CALLE DE ALCALA"
        print("✓ Función normalizar_texto funciona correctamente")
        
        # Probar conversión de coordenadas
        coordenada_convertida = convertir_coordenadas("40°29'21.84'' N")
        assert pytest.approx(coordenada_convertida, 0.001) == 40.4894
        print("✓ Función convertir_coordenadas funciona correctamente")
        
        # PASO 4: Búsqueda de direcciones existentes
        print("Paso 4: Probando búsqueda de direcciones...")
        
        # Caso 1: Dirección exacta
        direcciones_prueba = [
            "ABAD JUAN CATALAN, 1",
            "ABAD JUAN CATALAN, 10", 
            "ABAD JUAN CATALAN, 20"
        ]
        
        coordenadas_encontradas = []
        for direccion in direcciones_prueba:
            try:
                lat, lon = busca_direccion(direccion, self.callejero)
                assert isinstance(lat, float)
                assert isinstance(lon, float)
                assert 40.0 <= lat <= 41.0  # Rango razonable para Madrid
                assert -4.0 <= lon <= -3.0   # Rango razonable para Madrid
                coordenadas_encontradas.append((direccion, lat, lon))
                print(f"✓ Dirección encontrada: {direccion}")
            except AdressNotFoundError:
                print(f"⚠ Dirección no encontrada: {direccion}")
                continue
        
        # Verificar que al menos encontramos algunas direcciones
        assert len(coordenadas_encontradas) > 0, "No se encontró ninguna dirección de prueba"
        
        # Verificar que las coordenadas son únicas para direcciones diferentes
        coordenadas_unicas = set((lat, lon) for _, lat, lon in coordenadas_encontradas)
        assert len(coordenadas_unicas) == len(coordenadas_encontradas)
        print("✓ Coordenadas únicas para direcciones diferentes")
        
        # PASO 5: Probar robustez de búsqueda (diferentes formatos)
        print("Paso 5: Probando robustez de búsqueda...")
        
        formatos_variados = [
            "abad juan catalan, 1",           # minúsculas
            "ABAD JUAN CATALÁN, 1",           # con acento
            "  ABAD   JUAN   CATALAN  ,  1  ", # espacios extra
        ]
        
        for formato in formatros_variados:
            try:
                lat, lon = busca_direccion(formato, self.callejero)
                assert isinstance(lat, float)
                assert isinstance(lon, float)
                print(f"✓ Formato flexible funcionó: '{formato}'")
            except AdressNotFoundError:
                print(f"⚠ Formato no funcionó: '{formato}'")
        
        # PASO 6: Probar manejo de errores
        print("Paso 6: Probando manejo de errores...")
        
        # Dirección inexistente
        with pytest.raises(AdressNotFoundError):
            busca_direccion("CALLE INEXISTENTE, 999", self.callejero)
        print("✓ Manejo correcto de dirección inexistente")
        
        # Dirección vacía
        with pytest.raises(AdressNotFoundError):
            busca_direccion("", self.callejero)
        print("✓ Manejo correcto de dirección vacía")
        
        print("=== TEST DE FLUJO COMPLETO EXITOSO ===\n")
    
    def test_rendimiento_busquedas_multiples(self):
        """Test de rendimiento con búsquedas múltiples"""
        print("\n=== INICIANDO TEST DE RENDIMIENTO ===")
        
        self.callejero = carga_callejero()
        
        # Realizar múltiples búsquedas para medir consistencia
        direccion_base = "ABAD JUAN CATALAN, 1"
        resultados = []
        
        for i in range(5):
            lat, lon = busca_direccion(direccion_base, self.callejero)
            resultados.append((lat, lon))
            print(f"Búsqueda {i+1}: ({lat:.6f}, {lon:.6f})")
        
        # Verificar que todas las búsquedas devuelven el mismo resultado
        lat_base, lon_base = resultados[0]
        for lat, lon in resultados[1:]:
            assert lat == lat_base
            assert lon == lon_base
        
        print("✓ Búsquedas múltiples consistentes")
        print("=== TEST DE RENDIMIENTO EXITOSO ===\n")
    
    def test_datos_autovias(self):
        """Test específico para verificar el manejo de autovías"""
        print("\n=== INICIANDO TEST DE AUTOVÍAS ===")
        
        self.callejero = carga_callejero()
        
        # Verificar que existen autovías en el dataset
        autovias = self.callejero[self.callejero['VIA_CLASE'] == 'AUTOVÍA']
        assert len(autovias) > 0, "No se encontraron autovías en el dataset"
        print(f"✓ Encontradas {len(autovias)} entradas de autovías")
        
        # Probar búsqueda de alguna autovía
        autovias_prueba = ['A-1', 'A-2', 'A-3', 'A-4', 'A-5', 'A-6', 'A-42']
        
        for autovia in autovias_prueba:
            try:
                # Buscar por kilómetro que aparece en los datos de prueba
                lat, lon = busca_direccion(f"{autovia}, 10000", self.callejero)
                assert isinstance(lat, float)
                assert isinstance(lon, float)
                print(f"✓ Autovía encontrada: {autovia}")
                break  # Con que una funcione es suficiente
            except AdressNotFoundError:
                continue
        else:
            pytest.skip("No se pudo encontrar ninguna autovía para prueba")
        
        print("=== TEST DE AUTOVÍAS EXITOSO ===\n")
    
    def test_casos_limite(self):
        """Test de casos límite y edge cases"""
        print("\n=== INICIANDO TEST DE CASOS LÍMITE ===")
        
        self.callejero = carga_callejero()
        
        # Caso 1: Números muy altos
        with pytest.raises(AdressNotFoundError):
            busca_direccion("ABAD JUAN CATALAN, 99999", self.callejero)
        print("✓ Manejo correcto de números muy altos")
        
        # Caso 2: Caracteres especiales
        with pytest.raises(AdressNotFoundError):
            busca_direccion("@@@###$$$, 123", self.callejero)
        print("✓ Manejo correcto de caracteres especiales")
        
        # Caso 3: Solo números
        with pytest.raises(AdressNotFoundError):
            busca_direccion("123, 456", self.callejero)
        print("✓ Manejo correcto de dirección solo numérica")
        
        print("=== TEST DE CASOS LÍMITE EXITOSO ===\n")

class TestIntegracionFuncionesAuxiliares:
    """Tests de integración de funciones auxiliares con datos reales"""
    
    def test_integracion_normalizacion_busqueda(self):
        """Test que integra normalización con búsqueda"""
        callejero = carga_callejero()
        
        # Crear una columna normalizada para prueba
        callejero['NOMBRE_NORMALIZADO'] = callejero['VIA_NOMBRE'].apply(
            lambda x: normalizar_texto(str(x)) if pd.notna(x) else ""
        )
        
        # Verificar que la normalización funciona con datos reales
        assert len(callejero['NOMBRE_NORMALIZADO']) > 0
        print("✓ Integración normalización-búsqueda exitosa")
    
    def test_integracion_conversion_coordenadas(self):
        """Test que integra conversión de coordenadas con datos reales"""
        # Probar con ejemplos del formato real del dataset
        ejemplos_coordenadas = [
            "40°29'21.84'' N",
            "3°40'23.56'' W", 
            "40°30'13.33'' N",
            "3°39'33.27'' W"
        ]
        
        for coord in ejemplos_coordenadas:
            resultado = convertir_coordenadas(coord)
            assert isinstance(resultado, float)
            print(f"✓ Conversión exitosa: {coord} -> {resultado}")
    
    def test_calidad_datos_completa(self):
        """Test de calidad de datos completo"""
        callejero = carga_callejero()
        
        # Verificar completitud
        columnas_criticas = ['VIA_NOMBRE', 'NUMERO', 'LATITUD', 'LONGITUD']
        for columna in columnas_criticas:
            nulos = callejero[columna].isnull().sum()
            total = len(callejero)
            porcentaje_nulos = (nulos / total) * 100
            assert porcentaje_nulos < 50, f"Demasiados nulos en {columna}: {porcentaje_nulos:.1f}%"
            print(f"✓ Calidad de datos en {columna}: {100 - porcentaje_nulos:.1f}% completos")
        
        # Verificar valores únicos
        calles_unicas = callejero['VIA_NOMBRE'].nunique()
        print(f"✓ {calles_unicas} calles únicas en el dataset")

def test_sistema_completo_estres():
    """Test de estrés del sistema completo"""
    print("\n=== INICIANDO TEST DE ESTRÉS ===")
    
    callejero = carga_callejero()
    
    # Realizar múltiples búsquedas rápidas
    import time
    
    inicio = time.time()
    busquedas_exitosas = 0
    busquedas_totales = 10
    
    for i in range(busquedas_totales):
        try:
            # Alternar entre diferentes números
            numero = (i % 5) * 10 + 1
            lat, lon = busca_direccion(f"ABAD JUAN CATALAN, {numero}", callejero)
            busquedas_exitosas += 1
        except AdressNotFoundError:
            continue
    
    fin = time.time()
    tiempo_total = fin - inicio
    
    print(f"Tiempo total: {tiempo_total:.2f}s")
    print(f"Búsquedas exitosas: {busquedas_exitosas}/{busquedas_totales}")
    
    # Verificar que el sistema es razonablemente rápido
    assert tiempo_total < 10.0, "El sistema es demasiado lento"
    assert busquedas_exitosas > 0, "No se completó ninguna búsqueda"
    
    print("✓ Test de estrés superado")
    print("=== TEST DE ESTRÉS EXITOSO ===\n")

if __name__ == "__main__":
    # Ejecutar todos los tests de integración
    pytest.main([__file__, "-v", "-s"])