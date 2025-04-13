import datetime
from typing import List, Optional
from app.dependencies import SessionDep, UserTokenDep

from app.models import Employees, Enterprises, Departaments, DepartamentsEmployees, EnterprisesEmployees
from app.schemas import auth as auth_schemas
from app.schemas import users as users_schemas
import bcrypt
import jwt
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session     
from app.dependencies import SessionDep  
from app.utils import auth as auth_utils
from app.schemas import employees as employees_schemas

router_employees = APIRouter(prefix="/employees", tags=["Работники"])

@router_employees.get(
    "",
    response_model=List[employees_schemas.EmployeeResponse],
    summary="Получить список сотрудников"
)
async def list_employees(session: SessionDep):
    res = await Employees.get_all(session)
    return res


@router_employees.get(
    "/me",
    response_model=employees_schemas.EmployeeFullInfoResponse,
    summary="Получить инфу обо мне"
)
async def me_info(
    session: SessionDep,
    current_user: UserTokenDep  
):
    enterprise_assocs = await EnterprisesEmployees.get_all_by_employee_id(session, current_user.id)
    dept_assocs = await DepartamentsEmployees.get_all_by_employee_id(session, current_user.id)
    
    enterprises_dict = {}
    for assoc in enterprise_assocs:
        enterprise = assoc.enterprise
        enterprises_dict[enterprise.id] = {
            "id": enterprise.id,
            "name": enterprise.name,
            "boss_id": enterprise.boss_id,
            "departments": []  
        }
    
    for assoc in dept_assocs:
        department = assoc.department
        if department.enterprise_id in enterprises_dict:
            enterprises_dict[department.enterprise_id]["departments"].append({
                "id": department.id,
                "name": department.name,
                "role": assoc.role,
            })
    
    result = {
        "employee": {
            "id": current_user.id,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "phone": current_user.phone,
            "big_boss": current_user.big_boss,
        },
        "enterprises": list(enterprises_dict.values())
    }
    return result


@router_employees.get(
    "/{employee_id}",
    response_model=employees_schemas.EmployeeResponse,
    summary="Получить инфу о пользователе"
)
async def me_info(
    employee_id: int,
    session: SessionDep,
):
    res = await Employees.get_by_id(session, employee_id)
    return res

@router_employees.post(
    "/boss",
    # response_model=employees_schemas.EmployeeFullInfoResponse,
    summary="Сделать себя биг босом всего"
)
async def big_boss(
    session: SessionDep,
    current_user: UserTokenDep  
):
    current_user.big_boss = True
    await session.commit()
    return {
        "message": "успешно"
    }  