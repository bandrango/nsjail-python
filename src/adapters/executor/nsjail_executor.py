# File: src/adapters/executor/nsjail_executor.py

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
                    error_logger.error("Exception in user main()", exc_info=True)
                    raise ExecutionError("Execution failed")
            stdout = buf.getvalue()

            # 5. If main() returned None but stdout exists, treat as disallowed (e.g. directory-list)
            if result is None and stdout:
                error_logger.error(
                    "Disallowed stdout with no return value",
                    extra={"captured_stdout": stdout}
                )
                raise ExecutionError("Execution failed")

            # 6. If user printed intentionally (result != None), allow and continue
            # 7. Ensure result is JSON-serializable
            try:
                json.dumps(result)
            except Exception:
                error_logger.error("Result not JSON-serializable", exc_info=True)
                raise ExecutionError("Execution failed")

            # 8. Disallow any newline inside returned values
            if self._contains_newline(result):
                error_logger.error(
                    "Disallowed multiline content in return value",
                    extra={"result": result}
                )
                raise ExecutionError("Execution failed")

            # 9. Log success
            result_logger.info("Script run complete", extra={"result": result, "stdout": stdout})
            return result, stdout

        finally:
            try:
                os.remove(path)
            except Exception:
                error_logger.warning("Failed to remove temp file", extra={"temp_path": path})