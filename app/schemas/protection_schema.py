from pydantic import BaseModel, UUID4
from typing import Optional


class ProtectionResponse(BaseModel):
    """Schema for protection response"""
    is_malicious: bool
    explanation: str


class ThreatResponse(BaseModel):
    """Schema for threat response to client"""
    id: UUID4
    message_id: UUID4
    is_threat: bool
    description: str = ""
    user_description: Optional[str] = None

    class Config:
        from_attributes = True

    
