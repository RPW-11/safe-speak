from uuid import UUID
from sqlalchemy.orm import Session

from app.models.message import Message
from app.schemas.message_schema import MessageCreate


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_message(self, message: MessageCreate):
        db_message = Message(
            conversation_id=message.conversation_id,
            agent_id=message.agent_id,
            model=message.model,
            type=message.type,
            content=message.content,
            img_url=message.img_url
        )

        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)

        return db_message

    def load_messages_by_convo_id(self, conversation_id: UUID):
        return self.db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    