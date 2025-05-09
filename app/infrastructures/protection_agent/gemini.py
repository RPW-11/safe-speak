from .base import ProtectionAgentBase
from app.schemas.protection_schema import ProtectionResponse
from google import genai


class GeminiProtectionAgent(ProtectionAgentBase):
    def __init__(self, name: str, api_key: str):
        super().__init__(name=name)
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-2.0-flash'

    def process_message(self, message, conversation):
        system_prompt = self.get_system_prompt(conversation, message)

        response = self.client.models.generate_content(
            model=self.model,
            contents=system_prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': ProtectionResponse,
            }
        )
        
        return response.parsed

    def heartbeat(self) -> bool:
        try:
            self.client.models.generate_content(
                model=self.model,
                contents="Are you working?"
            )
            return True
        except Exception as e:
            print(f"Gemini heartbeat failed: {e}")
            return False
