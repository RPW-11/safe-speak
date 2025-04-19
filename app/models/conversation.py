from sqlalchemy import Column, Text, Date, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Conversation(Base):
    __tablename__ = "Conversation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("User.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("Agent.id"), nullable=False)
    title = Column(Text, nullable=False)
    created_at = Column(Date, nullable=False)
    updated_at = Column(Date, nullable=False)

    # Relationships
    user = relationship("User", back_populates="conversations")
    agent = relationship("Agent", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

    __table_args__ = (
        Index('conversation_user_id_index', 'user_id'),
    )