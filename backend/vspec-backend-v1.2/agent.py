from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Agent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str, capabilities: List[str]):
        self.name = name
        self.capabilities = capabilities
        self.tools = []
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task"""
        pass
    
    def add_tool(self, tool: Any) -> None:
        """Add a tool to the agent's toolkit"""
        self.tools.append(tool)
    
    def get_tools(self) -> List[Any]:
        """Get all tools available to this agent"""
        return self.tools
    
    def has_capability(self, capability: str) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.capabilities
    
    def get_capabilities(self) -> List[str]:
        """Get all capabilities of this agent"""
        return self.capabilities
