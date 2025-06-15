import pytest
from usecases.execute_script import ExecuteScriptUseCase, ExecutionError

class DummyExecutor:
    def execute(self, script):
        local_vars = {}
        try:
            exec(script, {}, local_vars)
            return local_vars["main"](), "stdout_dummy"
        except Exception as e:
            raise ExecutionError("Execution failed", str(e))


class DummyValidator:
    def validate(self, script):
        if "def main" not in script:
            raise ExecutionError("Missing main function", "No main")


class DummyLogger:
    def info(self, msg): pass
    def error(self, msg): pass


@pytest.fixture
def usecase():
    return ExecuteScriptUseCase(
        executor=DummyExecutor(),
        validator=DummyValidator(),
        logger=DummyLogger()
    )


def test_execute_valid_script(usecase):
    script = """
def main():
    return {"message": "Hello World"}
"""
    result = usecase.execute(script)
    assert result.result == {"message": "Hello World"}


def test_execute_invalid_script_syntax(usecase):
    script = "def main(: return 'bad'"
    with pytest.raises(ExecutionError) as exc:
        usecase.execute(script)
    assert "Execution failed" in str(exc.value)


def test_execute_without_main_function(usecase):
    script = """
def not_main():
    return "hello"
"""
    with pytest.raises(ExecutionError) as exc:
        usecase.execute(script)
    assert "Missing main function" in str(exc.value)