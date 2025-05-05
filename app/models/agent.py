from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Agent(Base):
    __tablename__ = "Agent"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)

    # relationship
    messages = relationship("Message", back_populates="agent")