import datetime
from typing import Optional
from app.dependencies import SessionDep, UserTokenDep1

from app.schemas import auth as auth_schemas
from app.schemas import users as users_schemas
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

router_users = APIRouter(prefix="/users", tags=["Пользователи"])


@router_users.get("/info/me", status_code=status.HTTP_200_OK, response_model=users_schemas.UserInfo)
async def info_me(current_user: UserTokenDep1, session: SessionDep):
    return current_user
