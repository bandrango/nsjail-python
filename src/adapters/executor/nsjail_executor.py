import os
import tempfile
import importlib.util
import contextlib
import io
import json

from domain.exceptions import ExecutionError
from adapters.validator.import_validator import ImportValidator
from adapters.logging_manager import request_logger, result_logger, error_logger

class NsJailExecutor:
    """
    Adapter: executes the user script safely using importlib (in-memory sandbox).
    Validates imports dynamically, runs main(), captures stdout and result.
    """

    def _contains_newline(self, obj):
        """
        Recursively check for any string containing a newline.
        """
        if isinstance(obj, str):
            return '\n' in obj
        if isinstance(obj, dict):
            return any(self._contains_newline(v) for v in obj.values())
        if isinstance(obj, (list, tuple, set)):
            return any(self._contains_newline(v) for v in obj)
        return False

    def execute(self, script_str: str):
        # 1. Log start
        request_logger.info("Starting script execution via NsJailExecutor")
        request_logger.debug("Script content: %s", script_str)

        # 2. Validate imports
        ImportValidator().validate(script_str)

        # 3. Write to temp file
        fd, path = tempfile.mkstemp(suffix='.py')
        try:
            with os.fdopen(fd, 'w') as tmp:
                tmp.write(script_str)

            spec = importlib.util.spec_from_file_location('user_module', path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 4. Capture stdout & run main()
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                try:
                    result = module.main()
                except Exception:
                    # Log the stacktrace
                    error_logger.error("Exception in user main()", exc_info=True)
                    # Attach whatever was printed so far
                    err = ExecutionError("Execution failed")
                    err.stdout = buf.getvalue()
                    raise err
            stdout = buf.getvalue()

            # 5. Disallow prints without return (e.g. directory-listings)
            if result is None and stdout:
                error_logger.error(
                    "Disallowed stdout with no return value",
                    extra={"captured_stdout": stdout}
                )
                err = ExecutionError("Execution failed")
                err.stdout = stdout
                raise err

            # 6. Ensure result is JSON-serializable
            try:
                json.dumps(result)
            except Exception:
                error_logger.error("Result not JSON-serializable", exc_info=True)
                err = ExecutionError("Execution failed")
                err.stdout = stdout
                raise err

            # 7. Disallow any multi-line strings in the returned value
            if self._contains_newline(result):
                error_logger.error(
                    "Disallowed multiline content in return value",
                    extra={"result": result}
                )
                err = ExecutionError("Execution failed")
                err.stdout = stdout
                raise err

            # 8. Log success and return both result and stdout
            result_logger.info("Script run complete", extra={"result": result, "stdout": stdout})
            return result, stdout

        finally:
            try:
                os.remove(path)
            except Exception:
                error_logger.warning("Failed to remove temp file", extra={"temp_path": path})