from typing import Dict, Any
from app.mcp.base import BaseMCPProvider

class MCPProviderInterface(BaseMCPProvider):
    def __init__(self, name: str):
        self._name = name

    @property
    def provider_id(self) -> str:
        return self._name

    def list_tools(self):
        return []

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]):
        raise NotImplementedError("MCP Tool execution abstract placeholder.")
