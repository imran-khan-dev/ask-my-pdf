from sqlalchemy.orm import Session

from app.modules.documents.embedding import generate_embedding
from app.modules.documents.search import search_similar_chunks
from app.modules.documents.llm import generate_answer


def ask_document(
    db: Session,
    document_id: int,
    question: str,
):
    # 1. Generate embedding for the question
    query_embedding = generate_embedding(question)

    # 2. Retrieve relevant chunks
    results = search_similar_chunks(
        db=db,
        query_embedding=query_embedding,
        document_id=document_id,
        limit=5,
    )

    # 3. No relevant chunks found
    if not results:
        return {
            "document_id": document_id,
            "question": question,
            "answer": "I couldn't find the answer in the document.",
            "sources": [],
        }

    # 4. Prepare chunks for the LLM
    chunks = []

    for chunk, distance in results:
        chunks.append(
            {
                "page_number": chunk.page_number,
                "content": chunk.content,
            }
        )

    # 5. Generate grounded answer
    answer = generate_answer(
        question=question,
        chunks=chunks,
    )

    # 6. Build unique page sources
    sources = []
    seen_pages = set()

    for chunk, distance in results:
        if chunk.page_number in seen_pages:
            continue

        seen_pages.add(chunk.page_number)

        sources.append(
            {
                "page_number": chunk.page_number,
                "distance": float(distance),
            }
        )

    return {
        "document_id": document_id,
        "question": question,
        "answer": answer,
        "sources": sources,
        
    }