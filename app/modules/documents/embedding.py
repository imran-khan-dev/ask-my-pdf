from sentence_transformers import SentenceTransformer
from app.core.config import EMBEDDING_MODEL

model = SentenceTransformer(EMBEDDING_MODEL)


def generate_embedding(text: str) -> list[float]:
    embedding = model.encode(text)

    return embedding.tolist()


if __name__ == "__main__":
    embedding = generate_embedding(
        "This document is about tax registration."
    )

    print("Number of dimensions:", len(embedding))
    print("First 5 numbers:", embedding[:5])