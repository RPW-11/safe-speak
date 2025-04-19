from datetime import timedelta
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.repositories.user_repository import UserRepository
from app.schemas.token_schema import Token
from app.schemas.user_schema import UserLogin, UserCreate, User
from app.core.exceptions import UnauthorizedException, DuplicateEntryException


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
        payload = decode_token(refresh_token)
        if not payload or not payload.get("refresh"):
            raise UnauthorizedException("Invalid refresh token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid refresh token")
        
        # Verify user still exists
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UnauthorizedException("User no longer exists")

        return self.create_tokens(user_id)