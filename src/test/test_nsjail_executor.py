import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from adapters.executor.nsjail_executor import NsJailExecutor
from domain.exceptions import ExecutionError

@pytest.fixture
def executor():
    return NsJailExecutor()

def test_execute_returns_result_and_stdout(executor):
    script = """
def main():
    print("hello")
    return {"a": 1}
"""
    result, stdout = executor.execute(script)
    assert result == {"a": 1}
    assert stdout.strip() == "hello"

def test_execute_print_only_raises_error_with_stdout(executor):
    script = """
def main():
    print("just a print")
"""
    with pytest.raises(ExecutionError) as exc:
        executor.execute(script)
    err = exc.value
    # stdout debe contener lo impreso
    assert "just a print" in err.stdout

def test_execute_non_json_serializable_raises(executor):
    script = """
def main():
    return set([1,2,3])
"""
    with pytest.raises(ExecutionError):
        executor.execute(script)

def test_execute_multiline_string_in_return_raises(executor):
    script = r'''
def main():
    return "line1\nline2"
'''
    with pytest.raises(ExecutionError):
        executor.execute(script)