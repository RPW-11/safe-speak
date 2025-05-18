from sqlalchemy import Column, Text, DateTime, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class User(Base):
    __tablename__ = "User"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    oauth_id = Column(Text, nullable=True)
    oauth_provider = Column(Text, nullable=True)
    username = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    img_url = Column(Text, nullable=True)
    hashed_password = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index('user_oauth_id_index', 'oauth_id'),
    )