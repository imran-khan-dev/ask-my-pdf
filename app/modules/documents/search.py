from sqlalchemy.orm import Session

from app.modules.documents.chunk_model import DocumentChunk


def search_similar_chunks(
    db: Session,
    query_embedding: list[float],
    limit: int = 5,
):
    results = (
        db.query(
            DocumentChunk,
            DocumentChunk.embedding.cosine_distance(query_embedding).label(
                "distance"
            ),
        )
        .filter(DocumentChunk.embedding.is_not(None))
        .order_by(
            DocumentChunk.embedding.cosine_distance(query_embedding)
        )
        .limit(limit)
        .all()
    )

    return results