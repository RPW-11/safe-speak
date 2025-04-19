from sqlalchemy import Column, Text, Date, ForeignKey, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Message(Base):
    __tablename__ = "Message"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("Conversation.id"), nullable=False)
    is_assistant = Column(Boolean, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(Date, nullable=False, default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    threat_indicators = relationship("ThreatIndicator", back_populates="message")