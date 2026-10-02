from sqlalchemy import Column, Integer, Text, ForeignKey
from pgvector.sqlalchemy import VECTOR
from app.core.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False,
    )

    chunk_index = Column(Integer, nullable=False)

    content = Column(Text, nullable=False)

    embedding = Column(VECTOR(384), nullable=True)
    page_number = Column(Integer, nullable=False)