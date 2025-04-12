from typing import Optional
from pydantic import BaseModel

class EnterpriseCreate(BaseModel):
    name: str

class EnterpriseResponse(BaseModel):
    enterprise_id: int
    name: str
    
class BossAssign(BaseModel):
    boss_id: int
    