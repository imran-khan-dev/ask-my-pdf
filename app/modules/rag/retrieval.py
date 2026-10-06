from sqlalchemy.orm import Session
from app.modules.rag.chunk_model import DocumentChunk


def search_similar_chunks(
    db: Session,
    query_embedding: list[float],
    limit: int = 5,
    document_id: int | None = None,
    max_distance: float = 0.6,
):
    query = (
        db.query(
            DocumentChunk,
            DocumentChunk.embedding.cosine_distance(query_embedding).label(
                "distance"
            ),
        )
        .filter(DocumentChunk.embedding.is_not(None))
    )

    if document_id is not None:
        query = query.filter(
            DocumentChunk.document_id == document_id
        )

    query = query.filter(
        DocumentChunk.embedding.cosine_distance(query_embedding)
        <= max_distance
    )

    results = (
        query
        .order_by(
            DocumentChunk.embedding.cosine_distance(query_embedding)
        )
        .limit(limit)
        .all()
    )

    return results