from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.token_schema import Token
from app.schemas.user_schema import UserCreate, UserLogin
from app.core.database import get_db
from app.services.authentication_service import AuthenticationService


router = APIRouter(tags=["Authentication"])


@router.post("/signup", response_model=Token)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    auth_service = AuthenticationService(db)

    user = auth_service.register_user(user_data)
    return auth_service.create_tokens(str(user.id))


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    auth_service = AuthenticationService(db)

    user = auth_service.authenticate_user(user_data)
    return auth_service.create_tokens(str(user.id))


@router.post("/refresh", response_model=Token)
async def refresh(refresh_token: str, db: Session = Depends(get_db)):
    auth_service = AuthenticationService(db)

    return auth_service.refresh_access_token(refresh_token)