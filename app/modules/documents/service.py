from pypdf import PdfReader
import logging
from app.core.database import SessionLocal
from app.modules.rag.chunk_model import DocumentChunk
from app.modules.rag.chunking import chunk_text
from app.modules.ai.embedding import generate_embedding
from app.modules.documents.model import Document

logger = logging.getLogger(__name__)

def extract_text(file_path: str) -> str:
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    # Remove NUL characters
    text = text.replace("\x00", "")

    return text

def extract_pages(file_path: str) -> list[dict]:
    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        if page_text:
            page_text = page_text.replace("\x00", "")

            pages.append(
                {
                    "page_number": page_number,
                    "text": page_text,
                }
            )

    return pages

def process_document(document_id: int):
    db = SessionLocal()

    try:
        # Fetch the document using the background task's own DB session
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if document is None:
            logger.warning(
                "Document not found during processing: document_id=%s",
                document_id,
            )
            return

        if document.processing_status != "processing":
            logger.info(
                "Skipping document processing: document_id=%s, status=%s",
                document_id,
                document.processing_status,
            )
            return

        logger.info(
            "Starting document processing: document_id=%s",
            document_id,
        )

        # Extract text page by page
        pages = extract_pages(document.storage_path)

        if not pages:
            raise ValueError("No readable text found in document")

        logger.info(
            "Extracted %s pages: document_id=%s",
            len(pages),
            document_id,
        )

        # Keep the complete extracted text in the document
        extracted_text = "\n".join(
            page["text"]
            for page in pages
        )

        document.extracted_text = extracted_text

        # Create chunks while preserving page numbers
        chunks = []

        for page in pages:
            page_chunks = chunk_text(page["text"])

            for chunk in page_chunks:
                chunks.append(
                    {
                        "page_number": page["page_number"],
                        "content": chunk,
                    }
                )

        logger.info(
            "Created %s chunks: document_id=%s",
            len(chunks),
            document_id,
        )

        # Generate embeddings and save chunks
        for index, chunk_data in enumerate(chunks):
            content = chunk_data["content"]

            embedding = generate_embedding(content)

            document_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                page_number=chunk_data["page_number"],
                content=content,
                embedding=embedding,
            )

            db.add(document_chunk)

        # Everything succeeded
        document.processing_status = "completed"

        db.commit()
        db.refresh(document)

        logger.info(
            "Document processing completed: document_id=%s, chunks=%s",
            document_id,
            len(chunks),
        )

    except Exception:
        logger.exception(
            "Document processing failed: document_id=%s",
            document_id,
        )

        # Remove any uncommitted database changes
        db.rollback()

        # Mark the document as failed
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if document is not None:
            document.processing_status = "failed"
            db.commit()

        raise

    finally:
        # Always close this background task's DB session
        db.close()