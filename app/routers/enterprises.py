import datetime
from typing import List, Optional
from app.dependencies import SessionDep, UserTokenDep

from app.models import Employee, Enterprise
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
from app.dependencies import SessionDep  
from app.models import Users               
from app.utils import auth as auth_utils
from app.schemas import employees as employees_schemas
from app.schemas import enterprises as enterprises_schemas

router_enterprises = APIRouter(prefix="/enterprises", tags=["Предприятия"])

@router_enterprises.get(
    "",
    response_model=List[enterprises_schemas.EnterpriseResponse]
)
async def list_enterprises(
    session: SessionDep
):
    stmt = (
        select(Enterprise)
    )
    result = await session.execute(stmt)
    enterprises = result.scalars().all()
    return enterprises

@router_enterprises.post(
    "",
    response_model=enterprises_schemas.EnterpriseResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_enterprise(
    enterprise: enterprises_schemas.EnterpriseCreate,
    session: SessionDep
):
    new_enterprise = Enterprise(
        name=enterprise.name,
        address=enterprise.address
    )
    session.add(new_enterprise)
    await session.commit()
    await session.refresh(new_enterprise)
    return new_enterprise
