from typing import Optional
from pydantic import BaseModel

class EnterpriseCreate(BaseModel):
    name: str
    address: Optional[str] = None

class EnterpriseResponse(BaseModel):
    enterprise_id: int
    name: str
    address: Optional[str] = None