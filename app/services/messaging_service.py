from sqlalchemy.orm import Session
from typing import AsyncGenerator
from fastapi import HTTPException, status
from asyncio import to_thread

from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.threat_indicator_repository import ThreatIndicatorRepository
from app.schemas.message_schema import MessageCreate, Message
from app.schemas.stream_schema import StreamResponseData
from app.schemas.protection_schema import ThreatResponse
from app.schemas.conversation_schema import ConversationUpdate, Conversation
from app.infrastructures.protection_agent.base import ProtectionAgentBase
from app.infrastructures.adversary.base import AdversaryBase
from app.core.exceptions import ForbiddenException, NotFoundException
from app.utils.message import format_messages_to_history


class MessagingService:
    def __init__(self, db: Session, user_id: str):
        self.user_id = user_id
        self.conversation_repository = ConversationRepository(db)
        self.message_repository = MessageRepository(db)
        self.threat_repository = ThreatIndicatorRepository(db)
    
    async def send_message(
        self,
        user_msg_data: MessageCreate,
        protection_agent: ProtectionAgentBase,
        adversary_agent: AdversaryBase
    ) -> AsyncGenerator[str, None]:
        try:
            recent_messages = self.message_repository.load_recent_messages(user_msg_data.conversation_id, 20)
            new_conversation = len(recent_messages) == 0
            recent_messages = format_messages_to_history(recent_messages)

            # insert user msg 1st time
            inserted_user_msg = self.message_repository.create_message(user_msg_data, "user")
            schema_format_user_msg = Message.model_validate(inserted_user_msg)
            yield StreamResponseData(
                type="user-msg",
                data=schema_format_user_msg
            ).model_dump_json()
            
            # setup conversation update
            def update_conversation():
                update_attr = ConversationUpdate()
                if new_conversation:
                    update_attr.title = protection_agent.generate_conversation_title(user_msg_data.content)
                updated_conversation = self.conversation_repository.update_conversation(
                    user_msg_data.conversation_id,
                    update_attr
                )
                return  updated_conversation
            
            update_title_thread = to_thread(update_conversation)

            # agent stream response initialization
            response_iterator = adversary_agent.respond(user_msg_data.content, recent_messages)
            response_text = ""    

            for chunk in response_iterator:
                response_text += chunk
                yield StreamResponseData(
                    type="ai-response",
                    data=chunk
                ).model_dump_json()

            adversary_message = MessageCreate(
                conversation_id=inserted_user_msg.conversation_id,
                agent_model=inserted_user_msg.agent_model,
                model = adversary_agent.name,
                type="text",
                content=response_text,
                img_url=None
            )

            inserted_adversary_msg = self.message_repository.create_message(adversary_message, "assistant")
            schema_format_adversary_msg = Message.model_validate(inserted_adversary_msg)
            yield StreamResponseData(
                type="ai-msg",
                data=schema_format_adversary_msg
            ).model_dump_json()

            
            updated_conversation = await update_title_thread
            format_updated_conversation = Conversation.model_validate(updated_conversation)
            yield StreamResponseData(
                type="new-conversation",
                data=format_updated_conversation
            ).model_dump_json()

            recent_messages += f"User: {user_msg_data.content}\n"

            verdict = protection_agent.process_message(response_text, recent_messages)
            threat = self.threat_repository.create_threat(inserted_adversary_msg.id, verdict.explanation)
            schema_format_threat = ThreatResponse.model_validate(threat)

            yield StreamResponseData(
                type="malicious-verdict",
                data=schema_format_threat
            ).model_dump_json()

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

        if not curr_convo:
            raise NotFoundException(detail="conversation does not exist")

        if str(curr_convo.user_id) != self.user_id:
            raise ForbiddenException("invalid conversation owner")
        
        try:
            return self.message_repository.load_messages_by_convo_id(curr_convo.id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load messages: {str(e)}"
            )


