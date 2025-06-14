"""
Domain models for script execution.
"""
from typing import Any

class Script:
    """
    Represents a user-provided Python script.
    """
    def __init__(self, source: str):
        self.source = source

class ExecutionResult:
    """
    Encapsulates the result of script execution.
    Contains the JSON-serializable result and captured stdout.
    """
    def __init__(self, result: Any, stdout: str):
        self.result = result
        self.stdout = stdout