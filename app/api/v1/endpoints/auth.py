from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import httpx

from app.schemas.token_schema import Token
from app.schemas.user_schema import UserCreate, UserLogin
from app.core.database import get_db
from app.services.authentication_service import AuthenticationService
from app.core.config import settings


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

@router.get("/login/oauth")
async def login_oauth(oauth_provider: str = "google"):
    print(f"Oauth redirect: {settings.GOOGLE_OAUTH_REDIRECT_URI}")
    params = {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = f"{settings.GOOGLE_OAUTH_AUTH_URI}?{httpx.QueryParams(params)}"
    return RedirectResponse(auth_url)


@router.get("/oauth/callback/{oauth_provider}")
async def login_oauth_callback(oauth_provider: str, code: str, db: Session = Depends(get_db)):
    auth_service = AuthenticationService(db)

    user = auth_service.authenticate_user_oauth(oauth_provider, code)
    return auth_service.create_tokens(str(user.id))


@router.post("/refresh", response_model=Token)
async def refresh(refresh_token: str, db: Session = Depends(get_db)):
    auth_service = AuthenticationService(db)

    return auth_service.refresh_access_token(refresh_token)