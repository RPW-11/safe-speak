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
from app.infrastructures.vdb.base import VectorDBBase
from app.core.exceptions import ForbiddenException, NotFoundException, AppExceptionBase
from app.utils.message import format_messages_to_history


class MessagingService:
    def __init__(self, db: Session, vdb: VectorDBBase, user_id: str):
        self.user_id = user_id
        self.conversation_repository = ConversationRepository(db)
        self.message_repository = MessageRepository(db)
        self.threat_repository = ThreatIndicatorRepository(db)
        self.vdb = vdb
    
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

            # agent stream response initialization
            response_iterator = adversary_agent.respond(user_msg_data.content, recent_messages)
            response_text = ""    

            for chunk in response_iterator:
                response_text += chunk
                yield StreamResponseData(
                    type="ai-response",
                    data=chunk
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
            
            # insert user msg
            inserted_user_msg = self.message_repository.create_message(user_msg_data, "user")
            schema_format_user_msg = Message.model_validate(inserted_user_msg)
            yield StreamResponseData(
                type="user-msg",
                data=schema_format_user_msg
            ).model_dump_json()

            adversary_message = MessageCreate(
                conversation_id=inserted_user_msg.conversation_id,
                agent_model=inserted_user_msg.agent_model,
                model = inserted_user_msg.model,
                rag_enabled=inserted_user_msg.rag_enabled,
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
            
            # check if rag is enabled
            relevant_msgs_str = None
            if user_msg_data.rag_enabled:
                relevant_msgs_str = self.vdb.search_points(response_text)
            
            verdict = protection_agent.process_message(response_text, recent_messages, relevant_msgs_str)

            message_to_vdb_thread = None
            if verdict.is_malicious: # if malicious, insert to vdb
                message_to_vdb_thread = to_thread(self.vdb.insert_point, inserted_adversary_msg.content, str(inserted_adversary_msg.id))

            threat = self.threat_repository.create_threat(inserted_adversary_msg.id, verdict.explanation)
            schema_format_threat = ThreatResponse.model_validate(threat)

            yield StreamResponseData(
                type="malicious-verdict",
                data=schema_format_threat
            ).model_dump_json()

            if message_to_vdb_thread:
                await message_to_vdb_thread

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create message: {str(e)}"
            )
    
    def load_messages_by_conversation(
        self,
        conversation_id: str
    ):
        try:
            # load the conversation
            curr_convo = self.conversation_repository.get_conversation(conversation_id)

            if not curr_convo:
                raise NotFoundException(detail="conversation does not exist")

            if str(curr_convo.user_id) != self.user_id:
                raise ForbiddenException("invalid conversation owner")
        
            return self.message_repository.load_messages_by_convo_id(curr_convo.id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load messages: {str(e)}"
            )

    def change_message_threat_status(
        self,
        message_id: str
    ):
        try:
            curr_msg = self.message_repository.get_message_by_id(message_id)
            if not curr_msg:
                raise NotFoundException(detail="message does not exist")

            curr_cnv = self.conversation_repository.get_conversation(curr_msg.conversation_id)
            if self.user_id != curr_cnv.user_id:
                raise ForbiddenException(detail="invalid owner of the message")
            
            # update the threat
            updated_threat = self.threat_repository.update_threat_status_by_msg_id(curr_msg.id)

            if not updated_threat.is_threat: # remove from vdb
                self.vdb.delete_points(updated_threat.message_id)
            
        except AppExceptionBase as e:
            raise e
        
        except Exception as e:
            print(f"Failed changing threat: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed changing threat: {str(e)}"
            )

