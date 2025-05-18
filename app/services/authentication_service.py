from datetime import timedelta
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import httpx

from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.repositories.user_repository import UserRepository
from app.schemas.token_schema import Token
from app.schemas.user_schema import UserLogin, UserCreate, UserCreateOAuth, User
from app.core.exceptions import UnauthorizedException, DuplicateEntryException, NotFoundException


class AuthenticationService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def register_user(self, user_create: UserCreate) -> User:
        if self.user_repository.get_user_by_email(user_create.email):
            raise DuplicateEntryException("Email already exists")
        if self.user_repository.get_user_by_username(user_create.username):
            raise DuplicateEntryException("Username already exists")
        
        hashed_password = get_password_hash(user_create.password)

        db_user = self.user_repository.create_user(
            UserCreate(
                username=user_create.username,
                email=user_create.email,
                password=hashed_password
            )
        )

        return User.model_validate(db_user)
    
    def authenticate_user(self, user_login: UserLogin) -> User:
        user = self.user_repository.get_user_by_email(user_login.email)
        if not user or not verify_password(user_login.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")
        
        return User.model_validate(user)
    
    def authenticate_user_oauth(self, oauth_provider: str, oauth_code: str) -> User:
        if oauth_provider not in settings.OAUTH_PROVIDERS:
            raise NotFoundException("OAuth provider not supported")
        
        # Google implementation for now
        with httpx.Client() as client:
            token_data = {
                "code": oauth_code,
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
                "grant_type": "authorization_code",
            }
            token_response = client.post(settings.GOOGLE_OAUTH_TOKEN_URI, data=token_data)
            token_json = token_response.json()

            if token_response.status_code != 200:
                raise UnauthorizedException("Invalid OAuth code")

            id_token_jwt = token_json.get("id_token")
            if not id_token_jwt:
                raise UnauthorizedException("No ID token received")

        try:
            user_info = id_token.verify_oauth2_token(
                id_token_jwt,
                google_requests.Request(),
                settings.GOOGLE_OAUTH_CLIENT_ID
            )
        except Exception as e:
            raise UnauthorizedException("Invalid ID token: " + str(e))
        
        email = user_info.get("email")
        username = user_info.get("name")
        oauth_id = user_info.get("sub")
        
        # check if user already exists
        user = self.user_repository.get_user_by_email(email)
        if not user:
            user = self.user_repository.create_user_oauth(
                UserCreateOAuth(
                    username=username,
                    email=email,
                    oauth_id=oauth_id,
                    oauth_provider=oauth_provider
                )
            )
        
        return User.model_validate(user)

    def create_tokens(self, user_id: str) -> Token:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            data={"sub": user_id},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": user_id},
            expires_delta=refresh_token_expires
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            refresh_token=refresh_token
        )
    
    def refresh_access_token(self, refresh_token: str) -> Token:
        token_exception = UnauthorizedException("Invalid refresh token")
        
        if not refresh_token:
            raise token_exception

        payload = decode_token(refresh_token)

        if not payload or not payload.get("refresh"):
            raise token_exception
        
        user_id = payload.get("sub")
        if not user_id:
            raise token_exception
        
        # Verify user still exists
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise token_exception

        return self.create_tokens(user_id)
    
    def get_user_details_by_id(self, user_id: str) -> User:
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user