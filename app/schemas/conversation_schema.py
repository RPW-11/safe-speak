from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class Conversation(BaseModel):
    id: UUID
    user_id: UUID
    agent_id: UUID
    title: str = Field(..., min_length=3, max_length=50)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True