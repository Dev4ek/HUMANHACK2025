from typing import Optional
import bcrypt
import jwt
from .main import get_moscow_time
from datetime import timedelta
from app.config import settings

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))



# Функция для создания JWT токена.
def create_access_token(data: dict, expires_minutes: int = 360) -> str:
    to_encode = data.copy()

    expire = get_moscow_time() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt
