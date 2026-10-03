from pydantic import BaseModel
from datetime import datetime


class DocumentResponse(BaseModel):
    id: int
    filename: str
    storage_path: str
    extracted_text: str
    processing_status: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class DocumentCreate(BaseModel):
    filename: str
    storage_path: str