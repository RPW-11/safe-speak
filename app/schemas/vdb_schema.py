from pydantic import BaseModel
from typing import List


class PointPayloadSchema(BaseModel):
    message_id: str
    content: str


class PointSchema(BaseModel):
    id: str
    vector: List[float]
    payload: PointPayloadSchema