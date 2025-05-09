from typing import Dict, Type
from app.infrastructures.protection_agent.base import ProtectionAgentBase
from app.infrastructures.protection_agent.gemini import GeminiProtectionAgent
from app.core.config import settings


class ProtectionAgentProvider:
    def __init__(self):
        self._agents: Dict[str, Type[ProtectionAgentBase]] = {
            "gemini": self._create_gemini_agent,
        }
    
    def get_agent(self, agent_name: str) -> ProtectionAgentBase:
        agent_class = self._agents.get(agent_name)
        if not agent_class:
            raise ValueError(f"Unknown protection agent: {agent_name}")
        return agent_class() 
    
    def _create_gemini_agent(self) -> ProtectionAgentBase:
        return GeminiProtectionAgent(name="gemini", api_key=settings.GEMINI_API_KEY)

