from typing import Optional
from pydantic import BaseModel

class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str

class EmployeeResponse(BaseModel):
    employee_id: int
    first_name: str
    last_name: str
    email: str
    phone: str

class EmployeeEnterpriseInvite(BaseModel):
    employee_id: int
    enterprise_id: int
    role: Optional[str] = "employee" 

class EmployeeDepartmentAssign(BaseModel):
    employee_id: int
    department_id: int
    role: Optional[str] = "staff"
    
class EmployeeEnterpriseUpdate(BaseModel):
    role: Optional[str] = None

class EmployeeDepartmentUpdate(BaseModel):
    role: Optional[str] = None

