import datetime
from typing import Optional
from app.dependencies import SessionDep

from app.schemas import auth as auth_schemas
import bcrypt
import jwt
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings         
from app.database import get_session       
from app.models import Users               
from app.utils import auth as auth_utils

router_auth = APIRouter(prefix="/auth", tags=["Авторизация"])


# Эндпоинт для регистрации нового пользователя.
@router_auth.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: auth_schemas.UserRegister, session: SessionDep):
    result = await session.execute(select(Users).where(Users.email == user.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой email уже существует",
        )

    hashed_password = auth_utils.hash_password(user.password)
    new_user = Users(
        email=user.email,
        phone=user.phone,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    access_token = auth_utils.create_access_token(data={"sub": str(new_user.id)})

    return {"id": new_user.id, "email": new_user.email, "access_token": access_token, "token_type": "bearer"}


# Эндпоинт для авторизации (логина)
@router_auth.post("/login")
async def login(user: auth_schemas.UserLogin, session: SessionDep):
    result = await session.execute(select(Users).where(Users.email == user.email))
    existing_user = result.scalars().first()
    if not existing_user or not auth_utils.verify_password(user.password, existing_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    # Генерируем JWT токен, в payload кладём идентификатор пользователя ("sub").
    access_token = auth_utils.create_access_token(data={"sub": str(existing_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}