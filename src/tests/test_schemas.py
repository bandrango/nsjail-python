import pytest
from interfaces.schemas import (
    ScriptRequestSchema,
    ExecutionResponseSchema,
    ExecutionResponseError
)

class TestScriptRequestSchema:
    """Pruebas para ScriptRequestSchema"""
    
    def test_valid_script_request(self):
        """Debe aceptar un script válido"""
        data = {"script": "def main():\n    return 'hello'"}
        request = ScriptRequestSchema(**data)
        assert request.script == data["script"]
    
    def test_missing_script_field(self):
        """Debe fallar si falta el campo script"""
        with pytest.raises(ValueError):
            ScriptRequestSchema(**{})
    
    def test_script_not_string(self):
        """Debe fallar si script no es string"""
        with pytest.raises(ValueError):
            ScriptRequestSchema(script=123)

class TestExecutionResponseSchema:
    """Pruebas para ExecutionResponseSchema"""
    
    @pytest.mark.parametrize("result", [
        {"key": "value"},  # Dict
        ["item1", "item2"],  # List
        "string",  # String
        123,  # Número
        None,  # None
        True  # Booleano
    ])
    def test_valid_responses(self, result):
        """Debe aceptar diferentes tipos de resultados válidos"""
        data = {
            "result": result,
            "stdout": "output text"
        }
        response = ExecutionResponseSchema(**data)
        assert response.result == result
        assert response.stdout == data["stdout"]
    
    def test_missing_fields(self):
        """Debe fallar si faltan campos requeridos"""
        with pytest.raises(ValueError):
            ExecutionResponseSchema(**{"result": None})
        
        with pytest.raises(ValueError):
            ExecutionResponseSchema(**{"stdout": "output"})

class TestExecutionResponseError:
    """Pruebas para ExecutionResponseError"""
    
    def test_valid_error(self):
        """Debe aceptar un mensaje de error válido"""
        error_msg = "Error message"
        error = ExecutionResponseError(error=error_msg)
        assert error.error == error_msg
    
    def test_missing_error_field(self):
        """Debe fallar si falta el campo error"""
        with pytest.raises(ValueError):
            ExecutionResponseError(**{})
    
    def test_error_not_string(self):
        """Debe fallar si error no es string"""
        with pytest.raises(ValueError):
            ExecutionResponseError(error=123)