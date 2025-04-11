import datetime
from typing import List, Optional
from app.dependencies import SessionDep, UserTokenDep

from app.models import Employee
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

router_employees = APIRouter(prefix="/employees", tags=["Работники"])


@router_employees.get(
    "",
    response_model=List[employees_schemas.EmployeeResponse]
)
async def list_employees(
    session: SessionDep
):
    stmt = (
        select(Employee)
    )
    result = await session.execute(stmt)
    employees = result.scalars().all()
    return employees

@router_employees.post(
    "",
    response_model=employees_schemas.EmployeeResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_employee(
    employee: employees_schemas.EmployeeCreate,
    session: SessionDep
):
    new_employee = Employee(
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        phone=employee.phone,
    )
    session.add(new_employee)
    await session.commit()
    await session.refresh(new_employee)
    return new_employee
