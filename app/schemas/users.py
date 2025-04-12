from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserInfo(BaseModel):
    id: int
    phone: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None