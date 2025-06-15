import pytest
from interfaces.schemas import (
    ScriptRequestSchema,
    ExecutionResponseSchema,
    ExecutionResponseError
)

class TestScriptRequestSchema:
    
    def test_valid_script_request(self):
        data = {"script": "def main():\n    return 'hello'"}
        request = ScriptRequestSchema(**data)
        assert request.script == data["script"]
    
    def test_missing_script_field(self):
        with pytest.raises(ValueError):
            ScriptRequestSchema(**{})
    
    def test_script_not_string(self):
        with pytest.raises(ValueError):
            ScriptRequestSchema(script=123)

class TestExecutionResponseSchema:
    
    @pytest.mark.parametrize("result", [
        {"key": "value"}, 
        ["item1", "item2"],  
        "string",  
        123,  
        None,  
        True  
    ])
    def test_valid_responses(self, result):
        data = {
            "result": result,
            "stdout": "output text"
        }
        response = ExecutionResponseSchema(**data)
        assert response.result == result
        assert response.stdout == data["stdout"]
    
    def test_missing_fields(self):
        with pytest.raises(ValueError):
            ExecutionResponseSchema(**{"result": None})
        
        with pytest.raises(ValueError):
            ExecutionResponseSchema(**{"stdout": "output"})

class TestExecutionResponseError:
    
    def test_valid_error(self):
        error_msg = "Error message"
        error = ExecutionResponseError(error=error_msg)
        assert error.error == error_msg
    
    def test_missing_error_field(self):
        with pytest.raises(ValueError):
            ExecutionResponseError(**{})
    
    def test_error_not_string(self):
        with pytest.raises(ValueError):
            ExecutionResponseError(error=123)