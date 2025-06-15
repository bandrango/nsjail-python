"""
Pydantic schemas for request validation and response serialization.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any

class ScriptRequestSchema(BaseModel):
    script: str  # Multiline Python script containing a main() function

class ExecutionResponseSchema(BaseModel):
     result: Any   # Return value of main(), must be JSON-serializable
     stdout: str   # Captured standard output from print() calls


class ExecutionResponseError(BaseModel):
    error: str