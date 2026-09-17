from fastapi import FastAPI

app = FastAPI()

from pydantic import BaseModel, Field

class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = None

class DocumentResponse(BaseModel):
    id: int
    title: str
    description: str | None = None

@app.get("/")
def home():
    return {
        "message": "Ask My Document API is running"
    }


@app.post("/documents")
def create_document(document: DocumentCreate):
    return {
        "title": document.title,
        "description": document.description
    }

@app.get("/documents/search")
def get_documents(q: str, limit: int = 10):
    return {
        "query": q,
        "limit": limit
    }

@app.get(
    "/documents/{document_id}",
    response_model=DocumentResponse
)
def get_document(document_id: int):
    return {
        "id": document_id,
        "title": "FastAPI notes",
        "description": "FastAPI notes",
    }

