from google import genai
from google.genai import types
from typing import List
from app.core.config import settings


client = genai.Client(api_key=settings.GEMINI_API_KEY)


def embed_texts(texts: List[str]) -> List[float]:
    result = client.models.embed_content(
            model="gemini-embedding-exp-03-07",
            contents=texts,
            config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY", output_dimensionality=settings.EMBEDDING_DIM)
    )

    return result.embeddings[0].values