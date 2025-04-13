from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    file_path: str
    status: str
    created_at: datetime
    signed_at: Optional[datetime]

class DocumentSend(BaseModel):
    document_id: int
    recipient_ids: List[int]
    
class DocumentSignRequestCode(BaseModel):
    document_id: int

class DocumentSign(BaseModel):
    code: int 