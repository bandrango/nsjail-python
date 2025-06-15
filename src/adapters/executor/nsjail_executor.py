import subprocess
import logging
import tempfile
import json
from pathlib import Path
from src.utils.config_loader import AppConfigLoader


class NsjailExecutor:
    def __init__(self):
        self.config_loader = AppConfigLoader()
        self.nsjail_config = self.config_loader.get_nsjail_config()
        self.logger = logging.getLogger("request_logger")

        for key in ["binary_path", "config_path", "python_path"]:
            if key not in self.nsjail_config or not self.nsjail_config[key]:
                raise ValueError(f"Missing NSJail config: {key}")

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

    def execute(self, user_script: str) -> dict:
        response = {
            "result": None,
            "stdout": "",
            "error": None
        }

        try:
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as script_file:
                script_path = Path(script_file.name)
                result_path = Path(script_file.name.replace(".py", ".json"))

                wrapped_script = self._wrap_script(user_script, str(result_path))
                script_file.write(wrapped_script)

            self.logger.info(f"Temp script created at: {script_path}")

            cmd = [
                self.nsjail_config["binary_path"],
                "--config", self.nsjail_config["config_path"],
                "--",
                self.nsjail_config["python_path"],
                str(script_path)
            ]

            self.logger.info(f"Executing command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=int(self.nsjail_config.get("time_limit", 10))
            )

            response["stdout"] = result.stdout.strip()

            if result.returncode != 0 or "ERROR:" in result.stdout:
                response["error"] = result.stdout.strip() or result.stderr.strip()
                return response

            if result_path.exists():
                with open(result_path) as f:
                    response["result"] = json.load(f)
            else:
                response["error"] = "main() did not return a result or result file missing."

            return response

        except subprocess.TimeoutExpired:
            self.logger.error("Execution timed out")
            response["error"] = "Execution timed out"
            return response

        except Exception as ex:
            self.logger.exception("Unexpected error during execution")
            response["error"] = str(ex)
            return response

        finally:
            for path in [script_path, result_path]:
                try:
                    if path.exists():
                        path.unlink()
                        self.logger.info(f"Deleted temp file: {path}")
                except Exception:
                    self.logger.warning(f"Could not delete temp file: {path}")
                    