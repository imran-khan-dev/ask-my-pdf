from pydantic import BaseModel

class SourceResponse(BaseModel):
    page_number: int
    distance: float

class AskResponse(BaseModel):
    document_id: int
    question: str
    answer: str
    sources: list[SourceResponse]
