from pydantic import BaseModel
from typing import Optional


class DepartmentCreate(BaseModel):
    name: str


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None


class DepartmentResponse(BaseModel):
    department_id: int
    name: str
    enterprise_id: int

    class Config:
        orm_mode = True
