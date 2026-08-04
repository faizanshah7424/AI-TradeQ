from typing import Dict, Optional
from app.mcp.base import BaseMCPProvider

class MCPRegistry:
    def __init__(self):
        self._providers: Dict[str, BaseMCPProvider] = {}

    def register_provider(self, provider: BaseMCPProvider):
        self._providers[provider.provider_id] = provider

    def get_provider(self, provider_id: str) -> Optional[BaseMCPProvider]:
        return self._providers.get(provider_id)

    def list_all_providers(self):
        return list(self._providers.keys())

mcp_registry = MCPRegistry()
