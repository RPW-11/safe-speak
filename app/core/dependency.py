from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.core.exceptions import UnauthorizedException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = UnauthorizedException("Could not validate credentials")
    
    try:
        payload = decode_token(token)
        if payload is None or payload.get("refresh"):
            raise credentials_exception
        
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        user = UserRepository(db).get_user_by_id(user_id)
        if user is None:
            raise credentials_exception
        
        return user
    except JWTError:
        raise credentials_exception