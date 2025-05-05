from uuid import UUID
from datetime import date
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
            title=conversation.title,
            created_at=date.today(),
            updated_at=date.today()
        )
        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)
        return db_conversation

    def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def get_user_conversations(self, user_id: UUID) -> List[Conversation]:
        return self.db.query(Conversation).filter(Conversation.user_id == user_id).all()

    def update_conversation(
        self, 
        conversation_id: UUID, 
        conversation: ConversationUpdate
    ) -> Optional[Conversation]:
        db_conversation = self.get_conversation(conversation_id)
        if db_conversation is None:
            return None
            
        update_data = conversation.model_dump(exclude_unset=True)
        if "title" in update_data:
            db_conversation.title = update_data["title"]
        if "updated_at" in update_data:
            db_conversation.updated_at = update_data["updated_at"]
        else:
            db_conversation.updated_at = date.today()
            
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

    # def get_conversation_by_user_and_agent(
    #     self, 
    #     user_id: UUID, 
    #     agent_id: UUID
    # ) -> Optional[Conversation]:
    #     return self.db.query(Conversation).filter(
    #         Conversation.user_id == user_id,
    #         Conversation.agent_id == agent_id
    #     ).first()