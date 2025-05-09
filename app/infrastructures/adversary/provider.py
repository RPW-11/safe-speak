from typing import Dict, Type
from app.infrastructures.adversary.base import AdversaryBase
from app.infrastructures.adversary.gemini import GeminiAdversary
from app.core.config import settings
from .persona import JULIA_PERSONA


class AdversaryAgentProvider:
    def __init__(self):
        self._agents: Dict[str, Type[AdversaryBase]] = {
            "julia": self._create_julia_agent,
        }
    
    def get_agent(self, agent_name: str) -> AdversaryBase:
        agent_class = self._agents.get(agent_name)
        if not agent_class:
            raise ValueError(f"Unknown protection agent: {agent_name}")
        return agent_class() 
    
    def _create_gemini_agent(self, name: str, persona: str) -> AdversaryBase:
        return GeminiAdversary(name=name, persona=persona, api_key=settings.GEMINI_API_KEY)
    
    def _create_julia_agent(self) -> AdversaryBase:
        return self._create_gemini_agent(name="julia", persona=JULIA_PERSONA)