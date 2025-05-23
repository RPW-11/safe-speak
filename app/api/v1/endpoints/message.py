from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List

from app.core.dependency import get_user_id, get_protection_agent, get_adversary_agent
from app.schemas.message_schema import MessageCreate, Message
from app.schemas.base_response_schema import BaseResponse
from app.core.database import get_db
from app.services.messaging_service import MessagingService
from app.infrastructures.protection_agent.base import ProtectionAgentBase
from app.infrastructures.adversary.base import AdversaryBase
from app.infrastructures.vdb.base import VectorDBBase
from app.infrastructures.vdb.qdrant_vdb import QdrantVDB


router = APIRouter(tags=["Message"])


@router.post("/send", response_class=StreamingResponse)
async def send_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    vdb: VectorDBBase = Depends(QdrantVDB),
    user_id: str = Depends(get_user_id),
    protection_agent: ProtectionAgentBase = Depends(get_protection_agent),
    adversary_agent: AdversaryBase = Depends(get_adversary_agent)
):
    messaging_service = MessagingService(db, vdb, user_id)
    
    return StreamingResponse(
        messaging_service.send_message(message_data, protection_agent, adversary_agent),
        media_type="application/json"
    )


@router.get("/", response_model=List[Message])
async def load_messages_from_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    vdb: VectorDBBase = Depends(QdrantVDB),
    user_id: str = Depends(get_user_id)
):
    messaging_service = MessagingService(db, vdb, user_id)

    return messaging_service.load_messages_by_conversation(conversation_id)


@router.patch("/threat-status", response_model=BaseResponse)
async def test_embedding(
    message_id: str,
    vdb: VectorDBBase = Depends(QdrantVDB)
):

    return BaseResponse(detail="Threat status has been updated")