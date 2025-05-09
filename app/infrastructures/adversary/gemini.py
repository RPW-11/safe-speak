from .base import AdversaryBase
from typing import Iterator
from google import genai


class GeminiAdversary(AdversaryBase):
    def __init__(self, name: str, persona: str, api_key: str):
        super().__init__(name=name, persona=persona)
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-2.0-flash'

    def respond(self, message, conversation) -> Iterator[str]:
        system_prompt = self.get_attack_prompt(conversation, message)
        response = self.client.models.generate_content_stream(
            model=self.model,
            contents=system_prompt
        )

        for chunk in response:
            yield chunk.text

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
