from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.user_schema import UserCreate, UserLogin
from app.core.database import get_db
from app.services.authentication_service import AuthenticationService


router = APIRouter(tags=["Authentication"])


@router.post("/signup")
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    auth_service = AuthenticationService(db)

    user = auth_service.register_user(user_data)
    return auth_service.create_tokens(str(user.id))
