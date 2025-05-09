from uuid import UUID
from sqlalchemy.orm import Session
from typing import Iterator
from fastapi import HTTPException, status

from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.message_schema import MessageCreate, Message
from app.infrastructures.protection_agent.base import ProtectionAgentBase
from app.infrastructures.adversary.base import AdversaryBase
from app.core.exceptions import ForbiddenException


class MessagingService:
    def __init__(self, db: Session, user_id: str):
        self.user_id = user_id
        self.conversation_repository = ConversationRepository(db)
        self.message_repository = MessageRepository(db)
    
    def send_message(
        self,
        user_msg_data: MessageCreate,
        protection_agent: ProtectionAgentBase,
        adversary_agent: AdversaryBase
    ) -> Iterator[str]:
        try:
            dummy_conversation = f"{adversary_agent.name}: Helloooo\n"

            response_iterator = adversary_agent.respond(user_msg_data.content, dummy_conversation)
            response_text = ""
            for chunk in response_iterator:
                response_text += chunk
                yield chunk

            dummy_conversation += f"user: {user_msg_data.content}\n"

            verdict = protection_agent.process_message(response_text, dummy_conversation)

            inserted_user_msg = self.message_repository.create_message(user_msg_data)

            adversary_message = MessageCreate(
                conversation_id=inserted_user_msg.conversation_id,
                agent_id=inserted_user_msg.agent_id,
                model = adversary_agent.name,
                type="text",
                content=response_text,
                img_url=None
            )

            inserted_adversary_msg = self.message_repository.create_message(adversary_message)

            yield str(inserted_adversary_msg.id)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create message: {str(e)}"
            )
    
    def load_messages_by_conversation(
        self,
        conversation_id: str
    ):
        # load the conversation
        curr_convo = self.conversation_repository.get_conversation(conversation_id)

        if str(curr_convo.user_id) != self.user_id:
            raise ForbiddenException("invalid conversation owner")
        
        try:
            return self.message_repository.load_messages_by_convo_id(curr_convo.id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load messages: {str(e)}"
            )


