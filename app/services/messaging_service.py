from uuid import UUID
from sqlalchemy.orm import Session
from typing import Iterator
from fastapi import HTTPException, status

from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.message_schema import MessageCreate, Message
from app.infrastructures.protection_agent.base import ProtectionAgentBase
from app.infrastructures.adversary.base import AdversaryBase


class MessagingService:
    def __init__(self, db: Session, user_id: str):
        self.user_id = user_id
        self.conversation_repository = ConversationRepository(db)
        self.message_repository = MessageRepository(db)
    
    def send_message(
        self,
        message_data: MessageCreate,
        protection_agent: ProtectionAgentBase,
        adversary_agent: AdversaryBase
    ) -> Iterator[str]:
        try:
            message = message_data.content
            dummy_conversation = f"{adversary_agent.name}: Helloooo\n"

            response_iterator = adversary_agent.respond(message, dummy_conversation)
            response_text = ""
            for chunk in response_iterator:
                response_text += chunk
                yield chunk

            dummy_conversation += f"user: {message}\n"

            verdict = protection_agent.process_message(response_text, dummy_conversation)

            # Save the messages to the database
            adversary_message = MessageCreate(
                conversation_id=message_data.conversation_id,
                agent_id=message_data.agent_id,
                model = adversary_agent.name,
                type="text",
                content=response_text,
                img_url=None
            )
            user_message = message_data

            return self.message_repository.create_messages(user_message, adversary_message)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create message: {str(e)}"
            )
    

