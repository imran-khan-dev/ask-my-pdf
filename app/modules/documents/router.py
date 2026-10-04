from fastapi import APIRouter, Depends, HTTPException,  UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.documents.model import Document
from app.modules.documents.schemas import (
    DocumentResponse,
)
from app.modules.documents.embedding import generate_embedding
from app.modules.documents.search import search_similar_chunks
from app.modules.documents.processing import process_document
from pathlib import Path
import uuid
from app.modules.documents.rag import ask_document as run_rag
from app.modules.documents.schemas import AskResponse

UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # 1. Validate content type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed",
        )

    # 2. Read the uploaded file
    content = await file.read()

    # 3. Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must be 10 MB or less",
        )

    # 4. Validate PDF file signature
    if not content.startswith(b"%PDF"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file",
        )

    # 5. Generate a safe unique filename
    original_filename = Path(file.filename or "document.pdf").name

    unique_filename = (
        f"{uuid.uuid4()}_{original_filename}"
    )

    file_path = UPLOAD_DIR / unique_filename

    # 6. Save the file
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to save uploaded file",
        )

    # 7. Create document record
    new_document = Document(
        filename=original_filename,
        storage_path=str(file_path),
        processing_status="processing",
    )

    try:
        db.add(new_document)
        db.commit()
        db.refresh(new_document)

    except Exception:
        db.rollback()

        if file_path.exists():
            file_path.unlink()
        raise

    # 8. Process in background
    background_tasks.add_task(
        process_document,
        new_document.id,
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

@router.get("/{document_id}/ask", response_model=AskResponse)
def ask_document(
    document_id: int,
    q: str,
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

    if document.processing_status == "processing":
        raise HTTPException(
            status_code=409,
            detail="Document is still being processed",
        )

    if document.processing_status == "failed":
        raise HTTPException(
            status_code=500,
            detail="Document processing failed",
        )

    if not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty",
        )

    return run_rag(
        db=db,
        document_id=document_id,
        question=q,
    )

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
def get_document(
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

    return document

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

    file_path = Path(document.storage_path)

    try:
        db.delete(document)
        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete document",
        )

    # Delete physical file after DB deletion succeeds
    if file_path.exists():
        try:
            file_path.unlink()
        except OSError:
            pass

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
    }