from sqlalchemy import Column, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class ThreatIndicator(Base):
    __tablename__ = "ThreatIndicator"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("Message.id", ondelete="CASCADE"), nullable=False)
    is_threat = Column(Boolean, nullable=False)
    description = Column(Text, nullable=False)
    user_description = Column(Text, nullable=True)

    # Relationships
    message = relationship("Message", back_populates="threat_indicator", passive_deletes=True)