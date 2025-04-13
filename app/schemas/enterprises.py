from typing import Optional
from pydantic import BaseModel
from .employees import EmployeeResponse

class EnterpriseCreate(BaseModel):
    name: str
    boss_id: Optional[int] = None

class EnterpriseResponse(BaseModel):
    id: int
    name: str
    boss_id: Optional[int]
    
class BossAssign(BaseModel):
    boss_id: int
    
    
class EnterprisesEmployees(BaseModel):
    id: int
    employee_id: int
    enterprise_id: int
    
class EnterpriseUpdate(BaseModel):
    name: Optional[str] = None
    boss_id: Optional[int] = None
    
class EnterprisesEmployeesOut(BaseModel):
    id: int
    employee: EmployeeResponse
    enterprise: EnterpriseResponse