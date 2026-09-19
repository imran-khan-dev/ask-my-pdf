from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.documents.model import Document
from app.modules.documents.schemas import (
    DocumentCreate,
    DocumentResponse,
)


router = APIRouter()

@router.post("/", response_model=DocumentResponse)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
):
    new_document = Document(
        filename=document.filename,
        storage_path=document.storage_path,
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

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

@router.get("/search")
def get_documents(q: str, limit: int = 10):
    return {
        "query": q,
        "limit": limit
    }

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

