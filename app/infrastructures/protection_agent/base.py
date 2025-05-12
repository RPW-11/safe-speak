from abc import ABC, abstractmethod
import textwrap

from app.schemas.protection_schema import ProtectionResponse


class ProtectionAgentBase(ABC):
    """
    Base class for protection agents.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.guidelines = textwrap.dedent("""
        1. Look for any messages that contain personal information, such as addresses, phone numbers, or social security numbers.
        2. Identify any messages that contain threats of violence or self-harm.
        3. Be on the lookout for messages that contain hate speech or discriminatory language.
        4. Check for any messages that contain links to suspicious websites or downloads.
        5. Look for any messages that contain spam or phishing attempts.
        6. Identify any messages that contain explicit content or graphic images.
        7. Be aware of any messages that contain false information or conspiracy theories.
        8. Check for any messages that contain malware or viruses.
        9. Look for any messages that contain harassment or bullying behavior.
        10. Identify any messages that contain illegal activity or solicitation.
        """)
        self.protection_prompt = textwrap.dedent("""
        You are a protection agent. Your job is to protect the user from malicious messages sent by their chatting partner.
        You will receive a list of messages from the on going conversation and you need to determine if the current message is malicious or not.
        If the message is malicious, you need to mark it as true in is_malicious attribute and provide a reason for why it is malicious.
        If the message is not malicious, you need to mark it as false in is_malicious attribute and do not provide a reason.

        The following is the format you should use to respond if the message is malicious:
        {{
            "is_malicious": true,
            "reason": "reason for why the message is malicious"
        }}
        The following is the format you should use to respond if the message is not malicious:
        {{
            "is_malicious": false,
            "reason": ""
        }}

        Additionally, you should follow the following guidelines to determine if the message is malicious or not:
        {guidelines}
        
        ON GOING CONVERSATION:
        {conversation}

        CURRENT MESSAGE:
        {message}
        """)

    def modify_guidelines(self, new_guidelines: str):
        """
        Modify the guidelines for the protection agent.
        """
        self.guidelines = new_guidelines

    def get_system_prompt(self, conversation: str, current_message: str) -> str:
        """
        Get the system prompt for the protection agent.
        """
        return self.protection_prompt.format(
            guidelines=self.guidelines,
            conversation=conversation,
            message=current_message
        )

    @abstractmethod
    def process_message(self, message: str, conversation: str) -> ProtectionResponse:
        """
        Process the message and return the result in the following format:
        {
            "is_malicious": true,
            "reason": "reason for why the message is malicious"
        }
        """
        pass

    @abstractmethod
    def heartbeat(self) -> bool:
        """
        Check if the agent is alive.
        """
        pass
