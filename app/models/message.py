from sqlalchemy import Column, Text, DateTime, ForeignKey, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Message(Base):
    __tablename__ = "Message"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("Conversation.id", ondelete="CASCADE"), nullable=False)
    role = Column(Text, nullable=False)
    agent_model = Column(Text, nullable=False)
    model = Column(Text, nullable=True)
    rag_enabled = Column(Boolean, nullable=False, default=False)
    type = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    img_url = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages", passive_deletes=True)
    threat_indicator = relationship("ThreatIndicator", back_populates="message", uselist=False, cascade="all, delete-orphan")