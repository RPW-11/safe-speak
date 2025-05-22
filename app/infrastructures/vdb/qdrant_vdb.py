from .base import VectorDBBase
from app.core.config import settings
from app.schemas.vdb_schema import PointPayloadSchema
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FilterSelector, FieldCondition, MatchValue
from app.infrastructures.embedding.gemini_embedding import embed_texts

from uuid import uuid4


class QdrantVDB(VectorDBBase):
    def __init__(self):
        super().__init__()
        self.client = QdrantClient(
            url=settings.QDRANT_HOST,
            api_key=settings.QDRANT_API_KEY,
            check_compatibility=False
        )

    def insert_point(self, message_content, message_id):
        text_embedding = embed_texts([message_content])
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=str(uuid4()),
                        vector=text_embedding,
                        payload=PointPayloadSchema(
                            message_id=message_id,
                            content=message_content
                        ).model_dump()
                    )
                ]
            )

        except Exception as e:
            print(f"An error has occured while inserting points to Qdrant: {e}")
    
    def delete_points(self, message_id):
        return self.client.delete(
            collection_name=self.collection_name,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="message_id",
                            match=MatchValue(value=message_id)
                        )
                    ]
                )
            )
        )
    
    def search_points(self, query, k=10) -> str:
        embedding_query = embed_texts([query])
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=embedding_query,
            limit=k,
            with_payload=True
        )

        formatted_str = "SIMILAR MESSAGES WITH SIMILARITY SCORE:\n"

        for i, res in enumerate(results.points):
            formatted_str += f"{i + 1}. {(res.payload['content'])}\nSimilarity score: {res.score}\n\n"

        return formatted_str
    
    def initialize(self):
        if not self.client.collection_exists(self.collection_name):
            print(f"Collection {self.collection_name} does not exist. Creating a new collection...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vec_dim, distance=Distance.COSINE),
            )
        print(f"Collection {self.collection_name} is ready!")

    
    def close(self):
        self.client.close()
        print(f"Qdrant connection has been closed")