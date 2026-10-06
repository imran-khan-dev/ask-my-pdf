from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.documents.model import Document
from app.modules.rag.service import ask_document as run_rag
from app.modules.documents.schemas import (
    AskResponse,
)

router = APIRouter()

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