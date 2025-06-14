from flask import request
from flask_restx import Namespace, Resource, fields
from src.usecases.execute_script import ExecuteScriptUseCase
from adapters.validator.import_validator import ImportValidator
from domain.exceptions import ExecutionError

# Create the namespace for the execute endpoint
execute_ns = Namespace(
    'execute',
    description='Endpoint for dynamic execution of Python scripts'
)

# Define the request model
script_model = execute_ns.model('ScriptPayload', {
    'script': fields.String(
        required=True,
        description='Python code to execute'
    )
})

# Define the response model
result_model = execute_ns.model('ExecutionResult', {
    'result': fields.Raw(
        description='Result returned by main()'
    )
})

@execute_ns.route('/')
class Execute(Resource):
    @execute_ns.expect(script_model, validate=True)
    @execute_ns.response(200, 'Success', result_model)
    @execute_ns.response(400, 'Execution error')
    def post(self):
        """Execute the provided Python script and return main()’s result"""
        payload = request.get_json()
        script = payload['script']
        validator = ImportValidator()
        try:
            validator.validate(script)
            result = ExecuteScriptUseCase().execute(script)
            return {'result': result}, 200
        except ExecutionError as e:
            execute_ns.abort(400, str(e))