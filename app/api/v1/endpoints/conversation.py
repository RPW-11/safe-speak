from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.dependency import get_user_id
from app.schemas.conversation_schema import Conversation, ConversationUpdate
from app.schemas.base_response_schema import BaseResponse
from app.core.database import get_db
from app.services.conversation_service import ConversationService


router = APIRouter(tags=["Conversation"])


@router.get("/", response_model=List[Conversation])
async def get_user_conversations(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    conversation_service = ConversationService(db, user_id)

    return conversation_service.get_user_conversations()


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    conversation_service = ConversationService(db, user_id)

    return conversation_service.get_conversation(conversation_id)


@router.post("/create", response_model=Conversation)
async def message(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    conversation_service = ConversationService(db, user_id)

    return conversation_service.create_conversation()


@router.patch("/{conversation_id}", response_model=Conversation)
async def update_conversation(
    update_data: ConversationUpdate,
    conversation_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    conversation_service = ConversationService(db, user_id)

    return conversation_service.update_conversation(conversation_id, update_data)


@router.delete("/{conversation_id}", response_model=BaseResponse)
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    conversation_service = ConversationService(db, user_id)

    return conversation_service.delete_conversation(conversation_id)