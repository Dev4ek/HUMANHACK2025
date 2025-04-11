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
