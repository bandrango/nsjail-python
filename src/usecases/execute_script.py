"""
Use case: orchestrate validation, execution, and logging of a script.
"""
from domain.models import ExecutionResult
from domain.exceptions import ExecutionError

class ExecuteScriptUseCase:
    """
    Single Responsibility: only orchestrates the execution flow.
    Depends on abstractions: executor, validator, logger.
    """
    def __init__(self, executor, validator, logger):
        self.executor = executor
        self.validator = validator
        self.logger = logger

    def execute(self, script_str: str) -> ExecutionResult:
        # Validate imports
        self.validator.validate(script_str)
        # Execute script and capture result
        result, stdout = self.executor.execute(script_str)
        # Log the full JSON response
        self.logger.info({'result': result, 'stdout': stdout})
        return ExecutionResult(result=result, stdout=stdout)