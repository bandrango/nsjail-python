import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from interfaces.schemas import ScriptRequestSchema, ExecutionResponseSchema
from pydantic import ValidationError

def test_script_request_schema_valid():
    data = {"script": "def main(): return 1"}
    schema = ScriptRequestSchema(**data)
    assert schema.script == data["script"]

def test_script_request_schema_missing_field():
    with pytest.raises(ValidationError):
        ScriptRequestSchema()

def test_execution_response_schema_valid():
    data = {"result": [1, 2, 3], "stdout": "ok"}
    schema = ExecutionResponseSchema(**data)
    assert schema.result == [1, 2, 3]
    assert schema.stdout == "ok"

def test_execution_response_schema_missing_stdout():
    with pytest.raises(ValidationError):
        ExecutionResponseSchema(result="foo")