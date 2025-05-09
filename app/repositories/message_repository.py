from uuid import UUID
from sqlalchemy.orm import Session

from app.models.message import Message
from app.schemas.message_schema import MessageCreate


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_messages(self, message_1: MessageCreate, message_2: MessageCreate):
        db_message_1 = Message(
            conversation_id=message_1.conversation_id,
            agent_id=message_1.agent_id,
            model=message_1.model,
            type=message_1.type,
            content=message_1.content,
            img_url=message_1.img_url
        )

        db_message_2 = Message(
            conversation_id=message_2.conversation_id,
            agent_id=message_2.agent_id,
            model=message_2.model,
            type=message_2.type,
            content=message_2.content,
            img_url=message_2.img_url
        )

        self.db.add_all([db_message_1, db_message_2])
        self.db.commit()

    def load_messages(self, conversation_id: UUID):
        return self.db.query(Message).filter(Message.conversation_id == conversation_id).all()
    