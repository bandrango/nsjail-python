import logging

from flask import Blueprint, request
from adapters.executor.nsjail_executor import NsjailExecutor
from adapters.validator.import_validator import ImportValidator
from domain.exceptions import ExecutionError
from interfaces.schemas import ScriptRequestSchema, ExecutionResponseSchema,  ExecutionResponseError

executor = NsjailExecutor()
bp = Blueprint('execute', __name__)
request_logger = logging.getLogger("request_logger")
result_logger = logging.getLogger("result_logger")
error_logger = logging.getLogger("error_logger")

@bp.route('/execute', methods=['POST'])
def execute_script():
    payload = request.get_json() or {}
    validated = ScriptRequestSchema(**payload)
    request_logger.info("Received execution request", extra={"payload": payload})

    script = validated.script
    try:
        request_logger.debug("Starting import validation")
        ImportValidator().validate(script)
        request_logger.info("Import validation passed")

        request_logger.info("Executing script in sandbox")
        output = executor.execute(script)
        if output.get("error"):
            error_scheme = ExecutionResponseError(**output)
            error_logger.error("Execution failed", extra={"error": error_scheme.error})            
            return {"error": error_scheme.error}, 400

        # Build the response exactly as required
        scheme_result = ExecutionResponseSchema(**output)
        response = {"result": scheme_result.result, "stdout": scheme_result.stdout}

        # --- Updated line: log the full JSON under 'result' ---
        result_logger.info(f"Responding with execution output: {response}")

        return response, 200

    except Exception as e:
        stdout = getattr(e, 'stdout', '')
        error_logger.error("ExecutionError occurred", exc_info=True)
        return {"error": str(e), "stdout": stdout}, 400