from .base import ProtectionAgentBase
from app.schemas.protection_schema import ProtectionResponse
from google import genai
from google.genai import types

import textwrap


class GeminiProtectionAgent(ProtectionAgentBase):
    def __init__(self, name: str, api_key: str):
        super().__init__(name=name)
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-2.0-flash'
        self.tool_calling_prompt = textwrap.dedent("""
            Use the appropriate tool functions based on the given message below.
            If there are image urls, pick one of them and use the analyze_image_api to analyze the content of the image.
            Message: {message}
        """)

    def process_message(self, message, conversation, relevant_messages: str=None) -> ProtectionResponse:
        system_prompt = self.get_system_prompt(conversation, message)

        response = self.client.models.generate_content(
            model=self.model,
            contents=self.tool_calling_prompt.format(message=message),
            config={
                'tools': [types.Tool(function_declarations=[self.image_analysis_function_declaration()])]
            }
        )

        tool_call = response.candidates[0].content.parts[0].function_call

        image_desc = None
        if tool_call and tool_call.name == "analyze_image_api":
            image_desc = self.analyze_image_api(**tool_call.args)
            print(image_desc)

        content = system_prompt if not image_desc else f"{system_prompt}\n{image_desc}"

        if relevant_messages and relevant_messages != "":
            content += f"\n\n{relevant_messages}"

        print(f"{content}")

        response = self.client.models.generate_content(
            model=self.model,
            contents=content,
            config={
                'response_mime_type': 'application/json',
                'response_schema': ProtectionResponse,
            }
        )

        return response.parsed
    
    def generate_conversation_title(self, user_prompt):
        title = self.client.models.generate_content(
            model=self.model,
            contents=f"Generate a single descriptive conversation title based on the following user prompt:\nUser: {user_prompt}\nRETURN THE TITLE ONLY!"
        )
        return title.text
    
    def image_analysis_function_declaration(self):
        return {
            "name": "analyze_image_api",
            "description": "Generate a description of a given image (from an url)",
            "parameters": {
                "type": "object",
                "properties": {
                    "img_url": {
                        "type": "string",
                        "description": "The image's URL",
                    },
                },
                "required": ["img_url"],
            },
        }

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
