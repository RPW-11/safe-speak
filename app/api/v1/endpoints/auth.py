from fastapi import APIRouter, Depends, Response, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
import httpx

from app.schemas.base_response_schema import BaseResponse
from app.schemas.user_schema import UserCreate, UserLogin, User, UserUpdate
from app.core.database import get_db
from app.core.dependency import get_user_id
from app.services.authentication_service import AuthenticationService
from app.core.config import settings


router = APIRouter(tags=["Authentication"])


@router.post("/signup", response_model=User)
async def signup(response: Response, user_data: UserCreate, db: Session = Depends(get_db)):
    auth_service = AuthenticationService(db)

    user = auth_service.register_user(user_data)
    token = auth_service.create_tokens(str(user.id))

    response.set_cookie(
        key="accessToken",
        value=token.access_token,
        httponly=True,
        secure=True,
        samesite='none',
        max_age=int(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()),
        path="/",
    )

    response.set_cookie(
        key="refreshToken",
        value=token.refresh_token,
        httponly=True,
        secure=True,
        samesite='none',
        max_age=int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()),
        path="/",
    )

    return user


@router.post("/login", response_model=User)
async def login(response: Response, user_data: UserLogin, db: Session = Depends(get_db)):
    auth_service = AuthenticationService(db)

    user = auth_service.authenticate_user(user_data)
    token = auth_service.create_tokens(str(user.id))

    response.set_cookie(
        key="accessToken",
        value=token.access_token,
        httponly=True,
        secure=True,
        samesite='none',
        max_age=int(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()),
        path="/",
    )

    response.set_cookie(
        key="refreshToken",
        value=token.refresh_token,
        httponly=True,
        secure=True,
        samesite='none',
        max_age=int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()),
        path="/",
    )

    return user


@router.get("/login/oauth", response_class=RedirectResponse)
async def login_oauth(client_redirect_url: str, oauth_provider: str = "google"):
    params = {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
        "state": client_redirect_url
    }
    auth_url = f"{settings.GOOGLE_OAUTH_AUTH_URI}?{httpx.QueryParams(params)}"
    return RedirectResponse(auth_url)


@router.get("/oauth/callback/{oauth_provider}", response_class=RedirectResponse)
async def login_oauth_callback(oauth_provider: str, code: str, state:str, db: Session = Depends(get_db)):
    auth_service = AuthenticationService(db)

    user = auth_service.authenticate_user_oauth(oauth_provider, code)
    token = auth_service.create_tokens(str(user.id))

    response = RedirectResponse(state)

    response.set_cookie(
        key="accessToken",
        value=token.access_token,
        httponly=True,
        secure=True,
        samesite='none',
        max_age=int(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()),
        path="/",
    )

    response.set_cookie(
        key="refreshToken",
        value=token.refresh_token,
        httponly=True,
        secure=True,
        samesite='none',
        max_age=int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()),
        path="/",
    )

    return response


@router.post("/refresh", response_model=BaseResponse)
async def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    auth_service = AuthenticationService(db)
    refresh_token = request.cookies.get("refreshToken")

    token = auth_service.refresh_access_token(refresh_token)
    response.set_cookie(
        key="accessToken",
        value=token.access_token,
        httponly=True,
        secure=True,
        samesite='none',
        max_age=int(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()),
        path="/",
    )

    response.set_cookie(
        key="refreshToken",
        value=token.refresh_token,
        httponly=True,
        secure=True,
        samesite='none',
        max_age=int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()),
        path="/",
    )

    return BaseResponse(detail="Your token has been refreshed")


@router.get("/me", response_model=User)
async def get_user_details(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    auth_service = AuthenticationService(db)

    return auth_service.get_user_details_by_id(user_id)


@router.patch("/update-profile", response_model=BaseResponse)
async def update_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id)
):
    auth_service = AuthenticationService(db)

    return auth_service.update_user_img(user_update, user_id)


@router.post("/logout", response_model=BaseResponse)
async def logout(response: Response):
    response.delete_cookie("accessToken")
    response.delete_cookie("refreshToken")

    return BaseResponse(detail="You have logged out successfully")