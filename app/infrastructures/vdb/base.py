from abc import ABC, abstractmethod
from typing import List
from app.schemas.vdb_schema import PointSchema
from app.core.config import settings


class VectorDBBase(ABC):
    def __init__(self):
        self.vec_dim = settings.EMBEDDING_DIM
        self.collection_name = settings.COLLECTION_NAME
    
    @abstractmethod
    def insert_point(self, message_content: str, message_id: str):
        pass

    @abstractmethod
    def delete_points(self, message_id: str):
        pass

    @abstractmethod
    def search_points(self, query: str, k:int) -> str:
        pass

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def close(self):
        pass

