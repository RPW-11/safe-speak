from pydantic import BaseModel
from typing import Union
from app.schemas.protection_schema import ThreatResponse
from app.schemas.message_schema import Message


class StreamResponseData(BaseModel):
    type: str
    data: Union[ThreatResponse, Message, str]