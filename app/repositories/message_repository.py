from uuid import UUID
from sqlalchemy.orm import Session, joinedload

from app.models.message import Message
from app.schemas.message_schema import MessageCreate


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_message(self, message: MessageCreate, role: str):
        db_message = Message(
            conversation_id=message.conversation_id,
            role=role,
            agent_model = message.agent_model,
            model=message.model,
            rag_enabled=message.rag_enabled,
            type=message.type,
            content=message.content,
            img_url=message.img_url
        )

        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)

        return db_message

    def get_message_by_id(self, message_id: str) -> Message:
        return self.db.query(Message).filter(Message.id == message_id).first()

    def load_messages_by_convo_id(self, conversation_id: UUID):
        return self.db.query(Message).filter(Message.conversation_id == conversation_id).options(joinedload(Message.threat_indicator)).order_by(Message.created_at.asc()).all()
    
    def load_recent_messages(self, conversation_id: UUID, n_messages: int):
        return self.db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.desc()).limit(n_messages).all()
    