from fastapi import APIRouter, Depends, HTTPException,  UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.documents.model import Document
from app.modules.documents.schemas import (
    DocumentResponse,
)
from app.modules.documents.chunk_model import DocumentChunk
from app.modules.documents.chunking import chunk_text
from app.modules.documents.embedding import generate_embedding
from app.modules.documents.search import search_similar_chunks
from app.modules.documents.llm import generate_answer
from app.modules.documents.pdf import extract_pages
from app.modules.documents.processing import process_document


router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    file_path = f"uploads/{file.filename}"

    # Save the uploaded PDF
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Create the document record
    new_document = Document(
        filename=file.filename,
        storage_path=file_path,
        processing_status="processing",
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    # Process the document
    process_document(
        document=new_document,
        db=db,
    )

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

@router.get("/{document_id}/ask")
def ask_document(
    document_id: int,
    q: str,
    db: Session = Depends(get_db),
):
    # 1. Generate embedding for the question
    query_embedding = generate_embedding(q)

    # 2. Retrieve the most relevant chunks
    results = search_similar_chunks(
        db=db,
        query_embedding=query_embedding,
        document_id=document_id,
        limit=5,
    )

    # 3. Extract chunk text for the LLM
    chunks = []

    for chunk, distance in results:
        chunks.append({
            "page_number": chunk.page_number,
            "content": chunk.content,
        })

    # 4. Generate the answer
    answer = generate_answer(
        question=q,
        chunks=chunks,
    )

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
        "question": q,
        "answer": answer,
        "sources": sources,
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

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
    }