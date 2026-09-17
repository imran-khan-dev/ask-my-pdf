from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = None


class DocumentResponse(BaseModel):
    id: int
    title: str
    description: str | None = None


@router.post("/", response_model=DocumentResponse)
def create_document(document: DocumentCreate):
    return {
        "id": 1,
        "title": document.title,
        "description": document.description
    }


@router.get("/search")
def get_documents(q: str, limit: int = 10):
    return {
        "query": q,
        "limit": limit
    }


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int):
    return {
        "id": document_id,
        "title": "My PDF",
        "description": "FastAPI notes"
    }