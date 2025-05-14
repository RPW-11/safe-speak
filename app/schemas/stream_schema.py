from pydantic import BaseModel
from typing import Union
from app.schemas.protection_schema import ThreatResponse
from app.schemas.message_schema import Message
from app.schemas.conversation_schema import Conversation


class StreamResponseData(BaseModel):
    type: str
    data: Union[ThreatResponse, Message, Conversation, str]