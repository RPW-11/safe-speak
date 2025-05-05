from datetime import date
from pydantic import BaseModel, UUID4
from typing import Optional


class ConversationBase(BaseModel):
    user_id: UUID4
    title: str


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: str


class ConversationInDB(ConversationBase):
    id: UUID4
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


class Conversation(ConversationInDB):
    pass