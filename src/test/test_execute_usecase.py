import pytest
from usecases.execute_script import ExecuteScriptUseCase
from domain.exceptions import ExecutionError
from domain.models import ExecutionResult

class DummyExecutor:
    def __init__(self, out):
        self.out = out
        self.called = False
    def execute(self, script):
        self.called = True
        return self.out

class DummyValidator:
    def __init__(self):
        self.called = False
    def validate(self, script):
        self.called = True

class DummyLogger:
    def __init__(self):
        self.logged = []
    def info(self, msg):
        self.logged.append(msg)

@pytest.fixture
def validator():
    return DummyValidator()

@pytest.fixture
def logger():
    return DummyLogger()

def test_usecase_success(validator, logger):
    dummy_exec = DummyExecutor(({"x": 42}, "out"))
    usecase = ExecuteScriptUseCase(dummy_exec, validator, logger)

    result_obj = usecase.execute("dummy script")
    # validator y executor fueron invocados
    assert validator.called is True
    assert dummy_exec.called is True

    # devolvió un ExecutionResult con los datos correctos
    assert isinstance(result_obj, ExecutionResult)
    assert result_obj.result == {"x": 42}
    assert result_obj.stdout == "out"

    # se hizo log de la respuesta completa
    assert {"result": {"x": 42}, "stdout": "out"} in logger.logged

def test_usecase_executor_raises(validator, logger):
    class BadExec:
        def execute(self, script):
            raise ExecutionError("boom")
    usecase = ExecuteScriptUseCase(BadExec(), validator, logger)
    with pytest.raises(ExecutionError):
        usecase.execute("whatever")