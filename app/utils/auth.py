from typing import Optional
import bcrypt
import jwt
from .main import get_moscow_time
from datetime import timedelta
from app.config import settings


SECRET_KEY = "super_secret_key"
ALGORITHM = "HS256"




def create_access_token(data: dict, expires_minutes: int = 720) -> str:
    to_encode = data.copy()

    expire = get_moscow_time() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt
