import datetime
from typing import List, Optional
from app.dependencies import SessionDep, UserTokenDep

from app.models import Employee, Enterprise, EmployeeEnterprise
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
    response_model=List[enterprises_schemas.EnterpriseResponse],
    summary="Получить список предприятий"
)
async def list_enterprises(
    session: SessionDep,
    current_user: UserTokenDep
):
    stmt = select(Enterprise)
    result = await session.execute(stmt)
    enterprises = result.scalars().all()
    return enterprises

@router_enterprises.post(
    "",
    response_model=enterprises_schemas.EnterpriseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новое предприятие"
)
async def create_enterprise(
    enterprise: enterprises_schemas.EnterpriseCreate,
    session: SessionDep,
    current_user: UserTokenDep
):
    new_enterprise = Enterprise(
        name=enterprise.name,
        address=enterprise.address
    )
    session.add(new_enterprise)
    await session.commit()
    await session.refresh(new_enterprise)
    return new_enterprise

@router_enterprises.get(
    "/{enterprise_id}/employees",
    response_model=List[employees_schemas.EmployeeResponse],
    summary="Получить сотрудников предприятия по ID"
)
async def get_employees_by_enterprise(
    enterprise_id: int, 
    session: SessionDep,
    current_user: UserTokenDep
    ):
    stmt = select(EmployeeEnterprise).where(EmployeeEnterprise.enterprise_id == enterprise_id)
    result = await session.execute(stmt)
    associations = result.scalars().all()
    employee_ids = [assoc.employee_id for assoc in associations]
    if not employee_ids:
        return []
    stmt_emp = select(Employee).where(Employee.employee_id.in_(employee_ids))
    result_emp = await session.execute(stmt_emp)
    employees = result_emp.scalars().all()
    return employees


@router_enterprises.patch(
    "/{enterprise_id}/boss",
    summary="Назначить босса для предприятия"
)
async def assign_enterprise_boss(
    enterprise_id: int,
    payload: enterprises_schemas.BossAssign,
    session: SessionDep,
    current_user: UserTokenDep
):
    stmt = select(Enterprise).where(Enterprise.enterprise_id == enterprise_id)
    result = await session.execute(stmt)
    enterprise = result.scalars().first()
    if not enterprise:
        raise HTTPException(status_code=404, detail="Предприятие не найдено")
        
    stmt = select(Employee).where(Employee.employee_id == payload.boss_id)
    result = await session.execute(stmt)
    boss = result.scalars().first()
    if not boss:
        raise HTTPException(status_code=404, detail="Сотрудник-босс не найден")

    enterprise.boss_id = payload.boss_id
    await session.commit()
    return {"message": "Босс предприятия успешно назначен"}


@router_enterprises.get(
    "/{enterprise_id}/structure",
    summary="Получить структуру предприятия с начальниками и сотрудниками"
)
async def get_enterprise_structure(
    enterprise_id: int,
    session: SessionDep,
    current_user: UserTokenDep
):
    stmt = select(Enterprise).where(Enterprise.enterprise_id == enterprise_id)
    result = await session.execute(stmt)
    enterprise = result.scalars().first()
    if not enterprise:
        raise HTTPException(status_code=404, detail="Предприятие не найдено")

    structure = {
        "enterprise_id": enterprise.enterprise_id,
        "name": enterprise.name,
        "address": enterprise.address,
        "boss": None,
        "departments": []
    }

    if enterprise.boss:
        structure["boss"] = {
            "employee_id": enterprise.boss.employee_id,
            "first_name": enterprise.boss.first_name,
            "last_name": enterprise.boss.last_name,
            "email": enterprise.boss.email,
            "phone": enterprise.boss.phone,
        }

    for dept in enterprise.departments:
        dept_info = {
            "department_id": dept.department_id,
            "name": dept.name,
            "boss": None,
            "employees": []
        }
        if dept.boss:
            dept_info["boss"] = {
                "employee_id": dept.boss.employee_id,
                "first_name": dept.boss.first_name,
                "last_name": dept.boss.last_name,
                "email": dept.boss.email,
                "phone": dept.boss.phone,
            }
        employee_ids = [assoc.employee_id for assoc in dept.employee_associations]
        if employee_ids:
            stmt_emp = select(Employee).where(Employee.employee_id.in_(employee_ids))
            result_emp = await session.execute(stmt_emp)
            employees = result_emp.scalars().all()
            dept_info["employees"] = [
                {
                    "employee_id": emp.employee_id,
                    "first_name": emp.first_name,
                    "last_name": emp.last_name,
                    "email": emp.email,
                    "phone": emp.phone,
                }
                for emp in employees
            ]
        structure["departments"].append(dept_info)
        
    return structure