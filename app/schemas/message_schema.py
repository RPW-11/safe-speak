from datetime import datetime
from pydantic import BaseModel, UUID4
from typing import Optional, List
from app.schemas.protection_schema import ThreatResponse


class MessageBase(BaseModel):
    conversation_id: Optional[UUID4] = None
    agent_model: str
    model: str
    type: str
    content: str
    img_url: Optional[str] = None


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    content: Optional[str] = None
    img_url: Optional[str] = None


class MessageInDB(MessageBase):
    id: UUID4
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Message(MessageInDB):
    threat_indicator: Optional[ThreatResponse]