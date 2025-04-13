from pydantic import BaseModel
from typing import Optional
from .employees import EmployeeResponse

class DepartmentCreate(BaseModel):
    name: str
    enterprise_id: int

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None

class DepartmentEmployeeUpdate(BaseModel):
    role: str

class DepartmentResponse(BaseModel):
    id: int
    name: str
    enterprise_id: int

class DepartmentEmployeeResponse(BaseModel):
    employee: EmployeeResponse
    department: DepartmentResponse
    role: Optional[str]
    
class DepartmentEmployeeCreate(BaseModel):
    employee_id: int