from pydantic import BaseModel


class ProtectionResponse(BaseModel):
    """Schema for protection response"""
    is_malicious: bool
    reason: str