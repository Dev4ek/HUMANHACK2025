from typing import Optional
from pydantic import BaseModel


class AuthRegister(BaseModel):
    phone: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class AuthLogin(BaseModel):
    phone: str


class AuthOut(BaseModel):
    access_token: str
    token_type: str
