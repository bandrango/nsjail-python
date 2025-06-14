import sys
import os
import pytest
from flask import Flask

# Asegúrate de que pytest encuentre tu código fuente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from adapters.http.execute import bp as execute_bp
from domain.exceptions import ExecutionError

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(execute_bp)
    app.testing = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def stub_validator_and_executor(monkeypatch):
    # 1) Stub ImportValidator.validate para que siempre pase
    from adapters.validator.import_validator import ImportValidator
    monkeypatch.setattr(ImportValidator, 'validate', lambda self, script: None)

    # 2) Stub NsJailExecutor.execute para un caso por defecto
    from adapters.executor.nsjail_executor import NsJailExecutor
    monkeypatch.setattr(
        NsJailExecutor,
        'execute',
        lambda self, script: ({"stub": True}, "stdout stub")
    )

def test_execute_success(client):
    resp = client.post('/execute', json={'script': 'print("ok"); return_value = {"x":1}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == {
        'result': {'stub': True},    # viene del stub
        'stdout': 'stdout stub'
    }

def test_execute_validation_error(client, monkeypatch):
    # Forzamos que la validación lance ExecutionError
    from adapters.validator.import_validator import ImportValidator
    def bad_validate(self, script):
        raise ExecutionError("invalid import", stdout="err_out")
    monkeypatch.setattr(ImportValidator, 'validate', bad_validate)

    resp = client.post('/execute', json={'script': 'any'})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data['error'] == 'invalid import'
    assert data['stdout'] == 'err_out'

def test_execute_execution_error(client, monkeypatch):
    # Forzamos que la ejecución lance ExecutionError
    from adapters.executor.nsjail_executor import NsJailExecutor
    def bad_execute(self, script):
        e = ExecutionError("exec failed")
        e.stdout = "traceback data"
        raise e
    monkeypatch.setattr(NsJailExecutor, 'execute', bad_execute)

    resp = client.post('/execute', json={'script': 'any'})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data['error'] == 'exec failed'
    assert data['stdout'] == 'traceback data'