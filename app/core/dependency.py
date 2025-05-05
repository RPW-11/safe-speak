from fastapi import Request
from jose import JWTError

from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException


async def get_user_id(
    request: Request
) -> str:
    credentials_exception = UnauthorizedException("Could not validate credentials")
    token = request.cookies.get("accessToken")

    try:
        if not token:
            raise credentials_exception

        payload = decode_token(token)
        if payload is None or payload.get("refresh"):
            raise credentials_exception
        
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        return user_id
    
    except JWTError:
        raise credentials_exception