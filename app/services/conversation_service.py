from uuid import UUID
from typing import Optional, List
from fastapi import HTTPException, status
from app.core.exceptions import UnauthorizedException, NotFoundException
from app.schemas.conversation_schema import ConversationCreate, ConversationUpdate, Conversation
from app.schemas.base_response_schema import BaseResponse
from app.repositories.conversation_repository import ConversationRepository
from sqlalchemy.orm import Session


class ConversationService:
    def __init__(self, db: Session, user_id: str):
        self.repository = ConversationRepository(db)
        self.user_id = user_id

    def create_conversation(self) -> Conversation:
        try:
            conversation_data = ConversationCreate(
                user_id=self.user_id,
            )
            
            return self.repository.create_conversation(conversation_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create conversation: {str(e)}"
            )

    def update_conversation(
        self, 
        conversation_id: UUID, 
        update_data: ConversationUpdate
    ) -> Optional[Conversation]:
                
        try:
            existing = self.repository.get_conversation(conversation_id)
            if not existing:
                raise NotFoundException(detail="Conversation not found")
            
            if str(existing.user_id) != self.user_id:
                raise UnauthorizedException("Invalid owner of the conversation")
                
            return self.repository.update_conversation(conversation_id, update_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update conversation: {str(e)}"
            )

    def delete_conversation(self, conversation_id: UUID) -> bool:
        existing = self.repository.get_conversation(conversation_id)
        if not existing:
            raise NotFoundException(detail="Conversation not found")
        
        if str(existing.user_id) != self.user_id:
            raise UnauthorizedException("Invalid owner of the conversation") 
           
        try:
            self.repository.delete_conversation(conversation_id)
            return BaseResponse(detail="Conversation has been deleted")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete conversation: {str(e)}"
            )

    def get_user_conversations(self) -> List[Conversation]:
        """
        Gets all conversations for a specific user.
        """
        return self.repository.get_user_conversations(self.user_id)

    def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """
        Gets a single conversation by ID.
        """
        conversation = self.repository.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        return conversation