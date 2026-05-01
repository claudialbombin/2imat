# conftest.py (configuración global de pytest)
import pytest
import sys
import os

# Añadir el directorio actual al path para importar los módulos
sys.path.insert(0, os.path.dirname(__file__))

def pytest_configure(config):
    """Configuración global de pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modificar tests según etiquetas"""
    skip_slow = pytest.mark.skip(reason="slow test - use -m \"not slow\" to run")
    skip_integration = pytest.mark.skip(reason="integration test - requires data")
    
    for item in items:
        if "slow" in item.keywords and config.getoption("--runslow") is None:
            item.add_marker(skip_slow)
        if "integration" in item.keywords and config.getoption("--runintegration") is None:
            item.add_marker(skip_integration)

# Opciones de línea de comandos
def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )
    parser.addoption(
        "--runintegration", action="store_true", default=False, help="run integration tests"
    )