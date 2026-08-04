from typing import Dict, Any, List
from app.mcp.base import BaseMCPProvider

class MockMCPProvider(BaseMCPProvider):
    @property
    def provider_id(self) -> str:
        return "mock_market_provider"

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "mock_fetch_ticker",
                "description": "Mock tool for testing MCP tool execution structure.",
                "parameters": {"symbol": "string"}
            }
        ]

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "result": f"Mock data for {arguments.get('symbol', 'UNKNOWN')}",
            "is_mock": True
        }
