import pytest
from unittest.mock import patch, mock_open
import yaml
import logging
from pathlib import Path
from src.utils.config_loader import AppConfigLoader

@pytest.fixture
def sample_config():
    """Configuración YAML de ejemplo para pruebas"""
    return {
        "app": {
            "flask": {"DEBUG": True},
            "allowed_commands": ["ls", "pwd"]
        },
        "nsjail": {
            "binary_path": "/usr/bin/nsjail",
            "config_path": "/etc/nsjail.cfg"
        },
        "logging": {
            "version": 1,
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG"
                }
            }
        }
    }

@pytest.fixture
def mock_yaml_load(sample_config):
    """Mock para yaml.safe_load"""
    with patch('yaml.safe_load', return_value=sample_config) as mock:
        yield mock

@pytest.fixture
def mock_path_exists():
    """Mock para Path.exists()"""
    with patch('pathlib.Path.exists', return_value=True) as mock:
        yield mock

@pytest.fixture
def mock_logging_config():
    """Mock para logging.config.dictConfig"""
    with patch('logging.config.dictConfig') as mock:
        yield mock

def test_init_default_path(mock_yaml_load, mock_path_exists, mock_logging_config):
    """Prueba inicialización con path por defecto"""
    loader = AppConfigLoader()
    
    expected_path = Path(__file__).resolve().parent.parent.parent / "application.yaml"
    assert str(loader.config_path) == str(expected_path)
    mock_path_exists.assert_called_once()
    mock_yaml_load.assert_called_once()

def test_init_file_not_found(mock_path_exists):
    """Prueba cuando el archivo de configuración no existe"""
    mock_path_exists.return_value = False
    
    with pytest.raises(FileNotFoundError):
        AppConfigLoader()

def test_load_config(sample_config, mock_yaml_load, mock_path_exists):
    """Prueba carga de configuración"""
    loader = AppConfigLoader()
    
    assert loader.config == sample_config
    mock_yaml_load.assert_called_once()

def test_get_flask_config(sample_config):
    """Prueba obtención de configuración Flask"""
    loader = AppConfigLoader()
    loader.config = sample_config
    
    assert loader.get_flask_config() == sample_config["app"]["flask"]

def test_get_nsjail_config(sample_config):
    """Prueba obtención de configuración NSJail"""
    loader = AppConfigLoader()
    loader.config = sample_config
    
    assert loader.get_nsjail_config() == sample_config["nsjail"]

def test_get_allowed_commands(sample_config):
    """Prueba obtención de comandos permitidos"""
    loader = AppConfigLoader()
    loader.config = sample_config
    
    assert loader.get_allowed_commands() == sample_config["app"]["allowed_commands"]

def test_get_config(sample_config):
    """Prueba obtención de toda la configuración"""
    loader = AppConfigLoader()
    loader.config = sample_config
    
    assert loader.get_config() == sample_config

def test_invalid_yaml_format(mock_path_exists):
    """Prueba con formato YAML inválido"""
    with patch('yaml.safe_load', side_effect=yaml.YAMLError("Invalid YAML")):
        with pytest.raises(yaml.YAMLError):
            AppConfigLoader()