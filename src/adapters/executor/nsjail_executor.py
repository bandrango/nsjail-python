import subprocess
import logging
import tempfile
import json
from pathlib import Path

from src.utils.config_loader import AppConfigLoader
from interfaces.schemas import ExecutionResponseSchema, ExecutionResponseError


class NsjailExecutor:
    def __init__(self):
        self.logger = logging.getLogger("request_logger")
        self.config = AppConfigLoader().get_nsjail_config()

        self.binary_path = self._require_config("binary_path")
        self.config_path = self._require_config("config_path")
        self.python_path = self._require_config("python_path")
        self.timeout = int(self.config.get("timeout", 10))

    def _require_config(self, key: str) -> str:
        value = self.config.get(key)
        if not value:
            raise ValueError(f"Missing NSJail config value for: '{key}'")
        return value

    def _wrap_script(self, user_script: str, result_path: str) -> str:
        return f"""{user_script}

if __name__ == "__main__":
    try:
        result = main()
        if isinstance(result, dict):
            import json
            with open("{result_path}", "w") as f:
                json.dump(result, f)
        else:
            raise ValueError("Function 'main' must return a dictionary (JSON serializable)")
    except Exception as e:
        print("ERROR:", e)
"""

    def execute(self, user_script: str):
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as script_file:
                script_path = Path(script_file.name)
                result_path = script_path.with_suffix(".json")

                wrapped_script = self._wrap_script(user_script, str(result_path))
                script_file.write(wrapped_script)

            command = [
                self.binary_path,
                "--config", self.config_path,
                "--", self.python_path,
                str(script_path)
            ]

            self.logger.debug(f"Running NSJail command: {' '.join(command)}")

            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if process.returncode == 0 and result_path.exists():
                with open(result_path) as f:
                    result_data = json.load(f)

                return ExecutionResponseSchema(
                    result=result_data,
                    stdout=process.stdout
                )
            else:
                error_message = (
                    f"Script exited with code {process.returncode}. "
                    f"Stderr: {process.stderr.strip()}"
                )
                self.logger.exception(error_message)
                return ExecutionResponseError(
                    error="Unable to execute the submitted command. Please verify the structure and content of the script."
                    )

        except Exception as e:
            self.logger.exception("NSJail execution error")
            return ExecutionResponseError(error=f"Execution error: {str(e)}")

        finally:
            if 'script_path' in locals() and script_path.exists():
                script_path.unlink()
            if 'result_path' in locals() and result_path.exists():
                result_path.unlink()
