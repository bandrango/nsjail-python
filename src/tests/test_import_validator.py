import pytest
from unittest.mock import patch, MagicMock
import ast
import importlib
from domain.exceptions import ExecutionError
from adapters.validator.import_validator import ImportValidator

@pytest.fixture
def validator():
    """Fixture para crear una instancia de ImportValidator"""
    return ImportValidator()

@pytest.fixture
def mock_loggers():
    """Fixture para mockear los loggers"""
    with patch('adapters.validator.import_validator.request_logger') as mock_req_log, \
         patch('adapters.validator.import_validator.error_logger') as mock_err_log:
        yield {
            'request': mock_req_log,
            'error': mock_err_log
        }

@pytest.fixture
def mock_importlib():
    """Fixture para mockear importlib"""
    with patch('importlib.import_module') as mock_import:
        yield mock_import

def test_validate_success(validator, mock_loggers, mock_importlib):
    """Prueba validación exitosa de imports"""
    script = "import os\nimport sys\ndef main(): pass"
    
    result = validator.validate(script)
    
    assert result is True
    mock_loggers['request'].info.assert_called_once_with("Starting import validation for script")
    mock_loggers['request'].debug.assert_any_call("Checking import: os")
    mock_loggers['request'].debug.assert_any_call("Checking import: sys")
    mock_importlib.assert_any_call('os')
    mock_importlib.assert_any_call('sys')

def test_validate_import_error(validator, mock_loggers, mock_importlib):
    """Prueba detección de módulo no existente"""
    script = "import non_existent_module"
    mock_importlib.side_effect = ImportError("No module named 'non_existent_module'")
    
    with pytest.raises(ExecutionError) as exc_info:
        validator.validate(script)
    
    assert "Module not found" in str(exc_info.value)
    mock_loggers['error'].error.assert_called_once()
    mock_loggers['request'].debug.assert_called_once_with("Checking import: non_existent_module")

def test_validate_from_import(validator, mock_loggers, mock_importlib):
    """Prueba validación de from-import"""
    script = "from collections import defaultdict"
    
    result = validator.validate(script)
    
    assert result is True
    mock_loggers['request'].debug.assert_called_once_with("Checking from-import: collections")
    mock_importlib.assert_called_once_with('collections')

def test_validate_unexpected_error(validator, mock_loggers, mock_importlib):
    """Prueba manejo de errores inesperados durante importación"""
    script = "import problematic_module"
    mock_importlib.side_effect = Exception("Unexpected error")
    
    with pytest.raises(ExecutionError) as exc_info:
        validator.validate(script)
    
    assert "Error importing module" in str(exc_info.value)
    mock_loggers['error'].error.assert_called_once()

def test_validate_empty_script(validator, mock_loggers):
    """Prueba con script vacío"""
    script = ""
    
    result = validator.validate(script)
    
    assert result is True
    mock_loggers['request'].info.assert_called_once()
