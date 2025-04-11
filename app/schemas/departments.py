from pydantic import BaseModel

class DepartmentCreate(BaseModel):
    enterprise_id: int
    name: str

class DepartmentResponse(BaseModel):
    department_id: int
    enterprise_id: int
    name: str
