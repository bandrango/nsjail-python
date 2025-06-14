# File: src/adapters/http/execute.py

from flask import Blueprint, request
from adapters.executor.nsjail_executor import NsJailExecutor
from adapters.validator.import_validator import ImportValidator
from domain.exceptions import ExecutionError
from adapters.logging_manager import request_logger, result_logger, error_logger

executor = NsJailExecutor()
bp = Blueprint('execute', __name__)

@bp.route('/execute', methods=['POST'])
def execute_script():
    # Log receipt of incoming HTTP payload
    payload = request.get_json()
    request_logger.info("Received execution request", extra={"payload": payload})

    script = payload.get('script')
    try:
        # 1. Validate imports dynamically
        request_logger.debug("Starting import validation")
        validator = ImportValidator()
        validator.validate(script)
        request_logger.info("Import validation passed")

        # 2. Execute the script via NsJail
        request_logger.info("Executing script in sandbox")
        result, stdout = executor.execute(script)
        result_logger.info("Script executed successfully", extra={"result": result})
        if stdout:
            result_logger.warning("Stdout captured during execution", extra={"stdout": stdout})

        return {'result': result}, 200

    except ExecutionError as e:
        # 3. Log the error with full stack trace
        error_logger.error("ExecutionError occurred", exc_info=True)
        return {'error': str(e)}, 400