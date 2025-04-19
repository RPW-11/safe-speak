from sqlalchemy import Column, Text, Date, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class User(Base):
    __tablename__ = "User"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    hashed_password = Column(Text, nullable=False)
    created_at = Column(Date, nullable=False, default=func.now())
    updated_at = Column(Date, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    conversations = relationship("Conversation", back_populates="user")