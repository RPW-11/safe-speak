from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.schemas.conversation_schema import ConversationCreate, ConversationUpdate
from typing import List, Optional

class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_conversation(self, conversation: ConversationCreate) -> Conversation:
        db_conversation = Conversation(
            user_id=conversation.user_id,
            title=conversation.title
        )
        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)
        return db_conversation

    def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def get_user_conversations(self, user_id: UUID) -> List[Conversation]:
        return self.db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc()).all()

    def update_conversation(
        self, 
        conversation_id: UUID, 
        conversation: ConversationUpdate
    ) -> Optional[Conversation]:
        db_conversation = self.get_conversation(conversation_id)
        if db_conversation is None:
            return None
            
        if conversation.title:
            db_conversation.title = conversation.title
        
        db_conversation.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(db_conversation)
        return db_conversation

    def delete_conversation(self, conversation_id: UUID) -> bool:
        db_conversation = self.get_conversation(conversation_id)
        if db_conversation is None:
            return False
            
        self.db.delete(db_conversation)
        self.db.commit()
        return True