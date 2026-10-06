from sentence_transformers import SentenceTransformer

from app.core.config import EMBEDDING_MODEL


model = SentenceTransformer(EMBEDDING_MODEL)


def generate_embedding(text: str) -> list[float]:
    embedding = model.encode(text)

    return embedding.tolist()