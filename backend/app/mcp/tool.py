from typing import Dict, Any, Callable
from pydantic import BaseModel

class MCPToolDefinition(BaseModel):
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    provider: str
