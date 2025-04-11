from typing import Optional
from pydantic import BaseModel, EmailStr

# Pydantic-схемы для регистрации и авторизации
class UserRegister(BaseModel):
    email: EmailStr
    phone: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str