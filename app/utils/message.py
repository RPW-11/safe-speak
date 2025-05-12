from app.schemas.message_schema import Message
from typing import List


def format_messages_to_history(messages: List[Message]):
    history_str = ""
    for message in messages[::-1]:
        history_str += f"User: {message.content}\n" if message.role == "user" else f"{message.model.capitalize()}: {message.content}"
    return history_str