from abc import ABC, abstractmethod
from typing import Iterator
import textwrap


class AdversaryBase(ABC):
    """
    Base class for adversaries.
    """

    def __init__(self, name: str, persona: str):
        self.name = name
        self.persona = persona
        self.attack_prompt = textwrap.dedent("""
        Your name is {name} and you are an adversary. Your job is to attack the user by sending them malicious messages.
        You have the following persona to follow:
        {persona}
        You will receive a list of messages from the on going conversation which you can use to determine the context of the conversation.
                                             
        ON GOING CONVERSATION:
        {conversation}
                                             
        CURRENT USER MESSAGE:
        {message}
        """)

    def get_attack_prompt(self, conversation: str, current_message: str) -> str:
        """
        Get the attack prompt for the adversary.
        """
        return self.attack_prompt.format(
            name=self.name,
            persona=self.persona,
            conversation=conversation,
            message=current_message
        )
    
    @abstractmethod
    def respond(self, message: str, conversation: str) -> Iterator[str]:
        """
        Generate a stream of responses to the given message.
        """
        pass

    @abstractmethod
    def heartbeat(self) -> bool:
        """
        Check if the agent is alive.
        """
        pass
        