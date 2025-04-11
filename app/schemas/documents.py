from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class DocumentCreate(BaseModel):
    sender_id: int
    title: str
    content: Optional[str] = None
    status: str

class DocumentResponse(BaseModel):
    document_id: int
    sender_id: int
    title: str
    content: Optional[str]
    created_at: datetime
    status: str

class DocumentSend(BaseModel):
    document_id: int
    recipient_ids: List[int]

class DocumentSign(BaseModel):
    document_id: int
    employee_id: int
    signature: str             
    confirmation_method: str 