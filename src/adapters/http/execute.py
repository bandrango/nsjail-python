import logging
from flask import Blueprint, request, jsonify

from adapters.executor.nsjail_executor import NsjailExecutor
from adapters.validator.import_validator import ImportValidator
from domain.exceptions import ExecutionError
from interfaces.schemas import (
    ScriptRequestSchema,
    ExecutionResponseSchema,
    ExecutionResponseError
)

executor = NsjailExecutor()
bp = Blueprint("execute", __name__)

# Loggers
request_logger = logging.getLogger("request_logger")
result_logger = logging.getLogger("result_logger")
error_logger = logging.getLogger("error_logger")
cloud_logger = logging.getLogger("cloud_logger")

@bp.route("/execute", methods=["POST"])
def execute_script():
    payload = request.get_json() or {}
    request_logger.info("Received execution request", extra={"payload": payload})

    try:
        validated_request = ScriptRequestSchema(**payload)
        script = validated_request.script

        request_logger.debug("Validating imports")
        ImportValidator().validate(script)
        request_logger.info("Import validation successful")

        request_logger.debug("Starting script execution")
        result = executor.execute(script)
        result_logger.info("Script executed successfully", extra={"result": result})
        cloud_logger.info("Script executed successfully", extra={"result": result})

        if hasattr(result, "error") and result.error:
            return jsonify(error=result.error), 400

        return jsonify(result=result.result, stdout=result.stdout), 200

    except ExecutionError as ex:
        error_logger.error("Execution error", exc_info=True)
        cloud_logger.error("Execution error", exc_info=True)
        error_response = ExecutionResponseError(
            message=str(ex),
            stdout=ex.stdout,
            stderr=ex.stderr
        )
        return jsonify(error_response.error), 400

    except Exception as e:
        error_logger.exception("Unexpected error during execution")
        cloud_logger.exception("Unexpected error during execution")
        return jsonify({"error": "Unexpected error occurred"}), 500
