from fastapi import APIRouter, Depends,  UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.documents.model import Document
from app.modules.documents.schemas import (
    DocumentResponse,
)
from app.modules.documents.pdf import extract_text
from app.modules.documents.chunk_model import DocumentChunk
from app.modules.documents.chunking import chunk_text
from app.modules.documents.embedding import generate_embedding
from app.modules.documents.search import search_similar_chunks
from app.modules.documents.llm import generate_answer

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    extracted_text = extract_text(file_path)

    new_document = Document(
        filename=file.filename,
        storage_path=file_path,
        extracted_text=extracted_text,
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    chunks = chunk_text(extracted_text)

    for index, chunk in enumerate(chunks):
        embedding = generate_embedding(chunk)

        document_chunk = DocumentChunk(
            document_id=new_document.id,
            chunk_index=index,
            content=chunk,
            embedding=embedding
        )

        db.add(document_chunk)

    db.commit()

    return new_document

def get_current_user():
    return {
        "id": 1,
        "name": "Imran"
    }

@router.get("/me")
def get_me(user = Depends(get_current_user)):
    return {
        "user": user
    }


# @router.get("/search")
# def get_documents(q: str, limit: int = 10):
#     return {
#         "query": q,
#         "limit": limit
#     }

# @router.get("/ask")
# def ask_document(
#     q: str,
#     db: Session = Depends(get_db),
# ):
#     # 1. Convert the question into an embedding
#     query_embedding = generate_embedding(q)

#     # 2. Find the most relevant chunks
#     results = search_similar_chunks(
#         db=db,
#         query_embedding=query_embedding,
#         limit=5,
#     )

#     # 3. Extract only the text from each chunk
#     chunks = []

#     for chunk, distance in results:
#         chunks.append(chunk.content)

#     # 4. Send the question + retrieved chunks to Qwen
#     answer = generate_answer(
#         question=q,
#         chunks=chunks,
#     )

#     return {
#         "question": q,
#         "answer": answer,
#     }

@router.get("/{document_id}/ask")
def ask_document(
    document_id: int,
    q: str,
    db: Session = Depends(get_db),
):
    query_embedding = generate_embedding(q)

    results = search_similar_chunks(
        db=db,
        query_embedding=query_embedding,
        document_id=document_id,
        limit=5,
    )

    chunks = []

    for chunk, distance in results:
        chunks.append(chunk.content)

    answer = generate_answer(
        question=q,
        chunks=chunks,
    )

    return {
        "document_id": document_id,
        "question": q,
        "answer": answer,
    }

@router.get("/search")
def search_documents(
    q: str,
    db: Session = Depends(get_db),
):
    query_embedding = generate_embedding(q)

    results = search_similar_chunks(
        db=db,
        query_embedding=query_embedding,
        limit=5,
    )

    return [
        {
            "id": chunk.id,
            "document_id": chunk.document_id,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "distance": distance,
        }
        for chunk, distance in results
    ]

@router.get("/", response_model=list[DocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).all()

    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int):
    return {
        "id": document_id,
        "title": "My PDF",
        "description": "FastAPI notes"
    }

