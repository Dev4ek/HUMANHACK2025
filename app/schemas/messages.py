from pydantic import BaseModel
from datetime import datetime

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    message: str
    created_at: datetime
