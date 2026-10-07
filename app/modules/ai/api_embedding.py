from openai import OpenAI

from app.core.config import (
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
)


def generate_embedding(text: str) -> list[float]:
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding