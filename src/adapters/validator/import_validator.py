import ast
import importlib
from domain.exceptions import ExecutionError
from adapters.logging_manager import request_logger, error_logger

class ImportValidator(ast.NodeVisitor):
    """
    AST Visitor that validates import statements in a given Python script.
    """

    def validate(self, script_str: str):
        # Log start of the validation process
        request_logger.info("Starting import validation for script")
        tree = ast.parse(script_str)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                module_name = node.names[0].name
                request_logger.debug(f"Checking import: {module_name}")
                self._check_module(module_name)
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module
                request_logger.debug(f"Checking from-import: {module_name}")
                self._check_module(module_name)

        return True  # All modules loaded successfully

    def _check_module(self, module_name: str):
        """
        Try importing the module; raise ExecutionError if it fails.
        """
        try:
            importlib.import_module(module_name)
        except ImportError:
            # Log the missing module error
            error_logger.error(f"ImportError for module '{module_name}'", exc_info=True)
            raise ExecutionError(f"Module not found or not installed: {module_name}")
        except Exception as e:
            # Log any other import-related exception
            error_logger.error(f"Unexpected error importing module '{module_name}'", exc_info=True)
            raise ExecutionError(f"Error importing module {module_name}: {e}")