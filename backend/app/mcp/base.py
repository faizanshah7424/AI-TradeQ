from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseMCPProvider(ABC):
    @property
    @abstractmethod
    def provider_id(self) -> str:
        pass

    @abstractmethod
    def list_tools(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        pass
