from flask import Blueprint, request
from adapters.executor.nsjail_executor import NsJailExecutor
from adapters.validator.import_validator import ImportValidator
from domain.exceptions import ExecutionError
from adapters.logging_manager import request_logger, result_logger, error_logger

executor = NsJailExecutor()
bp = Blueprint('execute', __name__)

@bp.route('/execute', methods=['POST'])
def execute_script():
    """
    POST /execute
    Expects JSON: {"script": "<python code>"}
    Success -> {"result": <return of main()>, "stdout": "<captured stdout>"}
    Error   -> {"error": "<message>",      "stdout": "<captured stdout>"}
    """
    payload = request.get_json() or {}
    request_logger.info("Received execution request", extra={"payload": payload})

    script = payload.get('script', '')
    try:
        request_logger.debug("Starting import validation")
        ImportValidator().validate(script)
        request_logger.info("Import validation passed")

        request_logger.info("Executing script in sandbox")
        result, stdout = executor.execute(script)

        # Build the response exactly as required
        response = {"result": result, "stdout": stdout}

        # --- Updated line: log the full JSON under 'result' ---
        result_logger.info(f"Responding with execution output: {response}")

        return response, 200

    except ExecutionError as e:
        stdout = getattr(e, 'stdout', '')
        error_logger.error("ExecutionError occurred", exc_info=True)
        return {"error": str(e), "stdout": stdout}, 400