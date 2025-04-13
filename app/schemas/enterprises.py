from typing import Optional
from pydantic import BaseModel
from .employees import EmployeeResponse

class EnterpriseCreate(BaseModel):
    name: str

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
    name: str
    
class EnterprisesEmployeesOut(BaseModel):
    id: int
    employee: EmployeeResponse
    enterprise: EnterpriseResponse