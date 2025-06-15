import pytest
import json
import logging
import subprocess
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from src.adapters.executor.nsjail_executor import NsjailExecutor
from src.utils.config_loader import AppConfigLoader

@pytest.fixture
def mock_config_loader():
    mock_loader = MagicMock(spec=AppConfigLoader)
    mock_loader.get_nsjail_config.return_value = {
        "binary_path": "/usr/bin/nsjail",
        "config_path": "/etc/nsjail.cfg",
        "python_path": "/usr/bin/python3",
        "time_limit": "10"
    }
    return mock_loader

@pytest.fixture
def nsjail_executor(mock_config_loader):
    with patch('src.adapters.executor.nsjail_executor.AppConfigLoader', return_value=mock_config_loader):
        executor = NsjailExecutor()
        executor.logger = MagicMock()
        return executor

def test_init_with_valid_config(nsjail_executor, mock_config_loader):
    mock_config_loader.get_nsjail_config.assert_called_once()
    assert nsjail_executor.nsjail_config["binary_path"] == "/usr/bin/nsjail"

def test_wrap_script(nsjail_executor):
    user_script = "def main():\n    return {'key': 'value'}"
    result_path = "/tmp/result.json"
    wrapped = nsjail_executor._wrap_script(user_script, result_path)
    assert user_script in wrapped
    assert "json.dump(result, f)" in wrapped