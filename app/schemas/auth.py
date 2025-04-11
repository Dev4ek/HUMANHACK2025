from typing import Optional
from pydantic import BaseModel, EmailStr



class AuthRegister(BaseModel):
    email: EmailStr
    phone: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class AuthLogin(BaseModel):
    email: EmailStr
    password: str
    
    
class AuthOut(BaseModel):
    access_token: str
    token_type: str
    
