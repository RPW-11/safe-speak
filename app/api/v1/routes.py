from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.conversation import router as conversation_router
from app.api.v1.endpoints.message import router as message_router


router = APIRouter()
router.include_router(auth_router, prefix="/auth")
router.include_router(conversation_router, prefix="/conversation")
router.include_router(message_router, prefix="/message")