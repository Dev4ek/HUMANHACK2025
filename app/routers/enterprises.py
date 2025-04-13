import datetime
from typing import List, Optional
from app.dependencies import SessionDep, UserTokenDep

from app.models import Employees, Enterprises, EnterprisesEmployees
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
from app.models import Employees               
from app.utils import auth as auth_utils
from app.schemas import employees as employees_schemas
from app.schemas import enterprises as enterprises_schemas

router_enterprises = APIRouter(prefix="/enterprises", tags=["Предприятия"])


@router_enterprises.get(
    "/me",
    response_model=List[enterprises_schemas.EnterprisesEmployeesOut],
    summary="Получить мои предприятия"
)
async def list_enterprises_me(
    session: SessionDep,
    current_user: UserTokenDep
):
    res = await EnterprisesEmployees.get_all_by_employee_id(session, current_user.id)
    return res


@router_enterprises.get(
    "",
    response_model=List[enterprises_schemas.EnterpriseResponse],
    summary="Получить список предприятий"
)
async def list_enterprises(
    session: SessionDep,
):
    res = await Enterprises.get_all(session)
    return res

@router_enterprises.post(
    "",
    response_model=enterprises_schemas.EnterpriseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новое предприятие"
)
async def create_enterprise(
    enterprise: enterprises_schemas.EnterpriseCreate,
    session: SessionDep,
):    
    new_enterprise = Enterprises(
        name=enterprise.name,
    )
    session.add(new_enterprise)
    await session.commit()
    await session.refresh(new_enterprise)
    return new_enterprise


@router_enterprises.get(
    "/{enterprise_id}",
    response_model=enterprises_schemas.EnterpriseResponse,
    summary="Получить данные по конкретному предприятию"
)
async def get_enterprise(
    enterprise_id: int, 
    session: SessionDep,
):
    enterprise = await Enterprises.get_by_id(session, enterprise_id)
    if not enterprise:
        raise HTTPException(status_code=404, detail="Предприятие не найдено")
    return enterprise


@router_enterprises.patch(
    "/{enterprise_id}",
    response_model=enterprises_schemas.EnterpriseResponse,
    summary="Обновить данные предприятия"
)
async def update_enterprise(
    enterprise_id: int,
    payload: enterprises_schemas.EnterpriseUpdate,
    session: SessionDep,
):
    enterprise = await Enterprises.get_by_id(session, enterprise_id)
    if not enterprise:
        raise HTTPException(status_code=404, detail="Предприятие не найдено")

    if payload.name is not None:
        enterprise.name = payload.name
    if payload.boss_id is not None:
        enterprise.boss_id = payload.boss_id
        
    await session.commit()
    await session.refresh(enterprise)
    return enterprise

@router_enterprises.delete(
    "/{enterprise_id}",
    status_code=204,
    summary="Удалить предприятие"
)
async def remove_enterprise(
    enterprise_id: int,
    session: SessionDep,
):    
    enterprise = await Enterprises.get_by_id(session, enterprise_id)
    await session.delete(enterprise)
    await session.commit()
    return

@router_enterprises.get(
    "/{enterprise_id}/employees",
    response_model=List[employees_schemas.EmployeeResponse],
    summary="Получить сотрудников предприятия по ID"
)
async def get_employees_by_enterprise(
    enterprise_id: int, 
    session: SessionDep,
):
    result = await EnterprisesEmployees.get_all_by_enterprise_id(session, enterprise_id)
    return [ee.employee for ee in result]

@router_enterprises.post(
    "/{enterprise_id}/employees/{employee_id}",
    response_model=enterprises_schemas.EnterprisesEmployees,
    summary="Добавить сотрудника в предприятие"
)
async def add_employees_to_enterprise(
    enterprise_id: int, 
    employee_id: int, 
    session: SessionDep,
):
    res = await EnterprisesEmployees.get_all_by_employee_id(session, employee_id)
    if res:
        raise HTTPException(
            409, 
            "Сотрудник уже есть в предпиятии"
        )
    new_ee = EnterprisesEmployees(
        employee_id=employee_id,
        enterprise_id=enterprise_id,
    )
    session.add(new_ee)
    await session.commit()
    await session.refresh(new_ee)
    return new_ee


@router_enterprises.delete(
    "/{enterprise_id}/employees/{employee_id}",
    status_code=204,
    summary="Удалить сотрудника из предприятия"
)
async def add_employees_to_enterprise(
    enterprise_id: int, 
    employee_id: int, 
    session: SessionDep,
):
    res = await EnterprisesEmployees.get_by_employee_id_by_enterprise_id(session, employee_id=employee_id, enterprise_id=enterprise_id)
    if not res:
        raise HTTPException(
            404, 
            "Сотрудник не найден в предприятии"
        )
    await session.delete(res)
    await session.commit()

