from typing import List, Optional
from pydantic import BaseModel


class EmployeeResponse(BaseModel):
    id: int
    
    phone: str
    first_name: str
    last_name: str
    
    
class EmployeeCreate(BaseModel):
    phone: str
    first_name: str
    last_name: str


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


class DepartmentInfo(BaseModel):
    id: int
    name: str
    role: Optional[str] = None

class EnterpriseInfo(BaseModel):
    id: int
    name: str
    boss_id: Optional[int] = None
    departments: List[DepartmentInfo] = []

class EmployeeInfo(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    big_boss: bool
    phone: str

class EmployeeFullInfoResponse(BaseModel):
    employee: EmployeeInfo
    enterprises: List[EnterpriseInfo]