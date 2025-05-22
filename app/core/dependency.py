from fastapi import Request, Depends
from jose import JWTError

from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, NotFoundException
from app.infrastructures.protection_agent.provider import ProtectionAgentProvider
from app.infrastructures.adversary.provider import AdversaryAgentProvider
from app.infrastructures.protection_agent.base import ProtectionAgentBase
from app.infrastructures.adversary.base import AdversaryBase
from app.infrastructures.vdb.qdrant_vdb import QdrantVDB
from app.schemas.message_schema import MessageCreate

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
    

async def get_protection_agent(
    message_data: MessageCreate,
    provider: ProtectionAgentProvider = Depends()
) -> ProtectionAgentBase:
    try:
        return provider.get_agent(message_data.model)
    except ValueError as e:
        raise NotFoundException(detail=str(e))
    

async def get_adversary_agent(
    message_data: MessageCreate,
    provider: AdversaryAgentProvider = Depends()
) -> AdversaryBase:
    try:
        return provider.get_agent(message_data.agent_model)
    except ValueError as e:
        raise NotFoundException(detail=str(e))


def initialize_dependencies():
    qdrant_vdb = QdrantVDB()
    qdrant_vdb.initialize()
    qdrant_vdb.close()
    

