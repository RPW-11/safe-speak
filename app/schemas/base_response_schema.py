from pydantic import BaseModel


class BaseResponse(BaseModel):
    detail: str