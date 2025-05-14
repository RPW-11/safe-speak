from datetime import datetime
from pydantic import BaseModel, UUID4
from typing import Optional


class ConversationBase(BaseModel):
    user_id: UUID4
    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: Optional[str] = None


class ConversationInDB(ConversationBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Conversation(ConversationInDB):
    pass