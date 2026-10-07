# Ask My Document — Backend

A FastAPI backend for a **Retrieval-Augmented Generation (RAG)** application that allows users to upload PDF documents and ask questions about their contents.

The backend implements the core RAG pipeline directly:

> **PDF → Extraction → Chunking → Embeddings → Vector Search → Context → LLM → Answer + Sources**

The project is intentionally built without LangChain so the underlying RAG workflow remains explicit and easy to understand.

---

## Overview

The backend is responsible for the complete document intelligence pipeline.

It handles:

* PDF uploads
* PDF text extraction
* Page-aware processing
* Paragraph-aware chunking
* Embedding generation
* PostgreSQL + pgvector storage
* Semantic retrieval
* Context construction
* LLM answer generation
* Source/page attribution
* Document processing status

The frontend is maintained separately and communicates with this backend through HTTP APIs.

---

## RAG Pipeline

```text
                 PDF
                  │
                  ▼
          ┌───────────────┐
          │ PDF Extraction│
          └───────┬───────┘
                  │
                  ▼
          ┌───────────────┐
          │    Chunking   │
          └───────┬───────┘
                  │
                  ▼
          ┌───────────────┐
          │   Embeddings  │
          └───────┬───────┘
                  │
                  ▼
          ┌───────────────┐
          │ PostgreSQL +  │
          │   pgvector    │
          └───────────────┘


Question
    │
    ▼
Question Embedding
    │
    ▼
Vector Similarity Search
    │
    ▼
Relevant Chunks
    │
    ▼
Context Construction
    │
    ▼
LLM
    │
    ▼
Answer + Source Pages
```

---

## Features

### Document Processing

* PDF upload
* Page-aware text extraction
* Extracted text storage
* Paragraph-aware chunking
* Configurable chunk size and overlap
* Document processing status
* Document deletion
* Cascade deletion of document chunks

### Vector Retrieval

* Sentence Transformer embeddings
* 384-dimensional vectors
* PostgreSQL vector storage
* pgvector cosine-distance search
* Similarity threshold
* Top-K retrieval
* Document-specific retrieval

### RAG Answer Generation

* Question embedding
* Relevant chunk retrieval
* Context construction
* Local LLM support
* API-based LLM support
* Grounded answer generation
* Page-level source information

---

## Tech Stack

### API

* Python
* FastAPI
* Pydantic

### Database

* PostgreSQL 17
* SQLAlchemy
* pgvector

### PDF Processing

* pypdf

### Embeddings

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Embedding dimension:

```text
384
```

### Local LLM

```text
Ollama
Qwen3 4B
```

---

## Architecture

```text
backend/
│
├── main.py
├── .env
├── uploads/
│
└── app/
    │
    ├── core/
    │   ├── config.py
    │   ├── database.py
    │   └── init_db.py
    │
    └── modules/
        │
        ├── documents/
        │   ├── router.py
        │   ├── schemas.py
        │   ├── model.py
        │   ├── pdf.py
        │   ├── chunking.py
        │   └── service.py
        │
        ├── ai/
        │   ├── embedding.py
        │   ├── llm.py
        │   ├── local_embedding.py
        │   ├── api_embedding.py
        │   ├── local_llm.py
        │   └── api_llm.py
        │
        └── rag/
            ├── router.py
            ├── schemas.py
            ├── retrieval.py
            └── service.py
```

---

## Module Responsibilities

### `documents/`

Responsible for the document lifecycle:

* Upload
* Storage
* PDF extraction
* Chunking
* Processing state
* Document retrieval
* Document deletion

### `ai/`

Provides an abstraction between the RAG pipeline and AI providers.

It contains separate implementations for:

* Local embeddings
* API embeddings
* Local LLM
* API LLM

This allows the RAG pipeline to remain independent of the specific AI provider.

### `rag/`

Contains the actual question-answering pipeline:

* Question processing
* Retrieval
* Context construction
* LLM orchestration
* Answer and source generation

---

## Document Processing

When a PDF is uploaded, the backend processes it in several stages.

### 1. Extract pages

Text is extracted while preserving page numbers.

```python
{
    "page_number": 1,
    "text": "..."
}
```

Preserving page numbers makes source attribution possible later.

### 2. Create chunks

The text is divided into smaller chunks.

The current chunking strategy attempts to preserve paragraph boundaries.

Default configuration:

```text
Chunk size: 1000 characters
Overlap: 200 characters
```

If an individual paragraph exceeds the configured chunk size, the system falls back to character-based splitting with overlap.

### 3. Generate embeddings

Each chunk is converted into a 384-dimensional vector using:

```text
paraphrase-multilingual-MiniLM-L12-v2
```

### 4. Store chunks

Each chunk stores:

* Document ID
* Chunk index
* Page number
* Text content
* Embedding

---

## Retrieval

When a question is submitted, the backend first creates an embedding for the question.

It then compares the question vector against stored document chunk vectors using cosine distance.

```text
Question
   ↓
Embedding
   ↓
pgvector cosine distance
   ↓
Similarity threshold
   ↓
Sort by distance
   ↓
Top relevant chunks
```

Lower cosine distance indicates greater vector similarity.

The retrieval layer can also restrict the search to a specific document.

This prevents unrelated documents from being used as context when asking questions about a selected document.

---

## Context Construction

Retrieved chunks retain their original page numbers.

The context passed to the LLM can therefore conceptually look like:

```text
[Page 3]
Relevant paragraph...

[Page 7]
Another relevant paragraph...
```

This allows the final response to reference the source pages associated with the retrieved content.

---

## LLM Generation

The RAG service passes the question and retrieved chunks to the configured LLM provider.

The provider interface is intentionally independent of the RAG service.

Conceptually:

```text
RAG Service
     │
     ▼
generate_answer(question, chunks)
     │
     ├── Local LLM
     │
     └── API LLM
```

This makes it possible to change the generation provider without rewriting the retrieval pipeline.

---

## Local AI Setup

The project can run locally without requiring paid AI APIs.

### Embeddings

The local embedding model is loaded through Sentence Transformers:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

### LLM

Ollama is used for local generation.

Pull the model:

```bash
ollama pull qwen3:4b
```

The configured model can then be used by the local LLM provider.

---

## Environment Variables

Example:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/ask_my_document

OLLAMA_MODEL=qwen3:4b

EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

If using API-based providers, the corresponding provider configuration and API keys should be added to the environment rather than committed to the repository.

`.env` should remain excluded from version control.

---

## Database

The project uses PostgreSQL with the `pgvector` extension.

The main relationship is:

```text
Document
   │
   │ 1:N
   ▼
DocumentChunk
```

A document contains multiple chunks.

Each chunk contains its corresponding embedding.

The vector column currently uses:

```text
VECTOR(384)
```

because the selected local embedding model produces 384-dimensional vectors.

The embedding dimension must remain consistent between the embedding model and database schema.

---

## API

### Health Check

```http
GET /
```

Response:

```json
{
  "message": "Ask My Document API is running"
}
```

### Documents

The document router provides the document management endpoints, including upload, listing, retrieval, and deletion.

### Ask a Document

```http
POST /documents/{document_id}/ask
```

Example:

```json
{
  "question": "What is the cancellation policy?"
}
```

The RAG pipeline then:

1. Embeds the question.
2. Searches relevant chunks.
3. Builds context.
4. Generates an answer.
5. Returns the answer and source information.

---

## Local Development

### Prerequisites

Install:

* Python
* PostgreSQL 17
* pgvector
* Ollama

### Create virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure database

Create the PostgreSQL database:

```text
ask_my_document
```

Ensure the `vector` extension is available.

### Start the API

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Testing the RAG Pipeline

A dedicated multi-page test PDF is included for evaluating the retrieval pipeline.

The document contains:

* Multiple sections
* Tables
* Similar terminology
* Page-specific facts
* Operational scenarios
* Information intentionally distributed across pages
* Questions whose answers are not present in the document

Example questions:

```text
What is the example evening price?

What is the example Main Turf slot length?

Why can't payment amount alone identify a transaction?

What was the collected advance in September?

What happens if two customers try to book the same slot simultaneously?

What should happen if a document uploads successfully but isn't searchable?
```

### Grounding test

Ask:

```text
What is TurfTrack's monthly subscription price?
```

The test document does not contain this information.

A correctly grounded RAG system should not invent a subscription price. It should indicate that the information cannot be found in the document.

---

## Engineering Decisions

### Why PostgreSQL + pgvector?

The project uses PostgreSQL for both relational data and vector search instead of introducing a separate vector database.

This keeps:

* Documents
* Chunks
* Metadata
* Relationships
* Embeddings
* Retrieval

within the same database system.

### Why page-aware chunks?

Flattening the entire PDF into one text string would make source attribution difficult.

Keeping page numbers with each chunk allows retrieved content to be connected back to the original document.

### Why paragraph-aware chunking?

Blindly splitting every N characters can break related sentences and paragraphs.

The current strategy attempts to preserve paragraph boundaries while still enforcing a maximum chunk size.

### Why a similarity threshold?

The nearest vector is not necessarily a useful answer.

A similarity threshold allows weak matches to be rejected before they reach the LLM.

### Why avoid LangChain?

The initial implementation intentionally avoids LangChain.

The core RAG pipeline is implemented directly so the mechanics of:

```text
Extraction
→ Chunking
→ Embedding
→ Vector Search
→ Retrieval
→ Context Construction
→ Generation
```

remain explicit.

This makes the system easier to understand, debug, and evaluate.

---

## Production Direction

The intended production architecture separates the frontend, API, database, and AI providers:

```text
Next.js
   │
   ▼
Vercel
   │
   ▼
FastAPI
   │
   ├──────────────► Managed PostgreSQL + pgvector
   │
   └──────────────► AI API Provider
```

Local development uses Sentence Transformers and Ollama to avoid unnecessary API costs.

Production can use API-based embedding and LLM providers through the existing provider abstraction.

---

## Current Limitations

The current backend is intentionally focused on the core RAG workflow.

Known limitations include:

* PDF-focused ingestion
* No OCR pipeline for scanned PDFs
* No hybrid keyword + vector retrieval
* No reranking model
* No advanced automated RAG evaluation framework
* No multi-document reasoning
* No conversation memory
* Local processing is not optimized for very large document collections

These are potential areas for future development.

---

## Future Improvements

Possible next steps include:

* Hybrid BM25 + vector retrieval
* Reranking
* OCR support
* Multi-document retrieval
* Streaming responses
* Conversation history
* Automated retrieval evaluation
* Automated answer evaluation
* Improved citation rendering
* Background job queues
* Object storage for uploaded documents
* Authentication and user accounts
* Multi-tenant document isolation
* Observability and tracing

---

## Related Repository

**Frontend:** https://github.com/imran-khan-dev/ask-my-pdf-frontend

---

## Project Goal

Ask My Document was built to demonstrate practical understanding of the underlying components of a RAG application rather than simply connecting an LLM API to a document.

The project covers the complete path from raw document to grounded answer:

```text
PDF
 ↓
Text Extraction
 ↓
Chunking
 ↓
Embeddings
 ↓
Vector Storage
 ↓
Semantic Retrieval
 ↓
Context Construction
 ↓
LLM
 ↓
Grounded Answer
 ↓
Source Pages
```

The result is a small, complete, deployable AI application designed to be understood, tested, evaluated, and demonstrated as an AI engineering project.
