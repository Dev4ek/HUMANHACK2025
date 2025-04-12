import datetime
from typing import List, Optional
from app.dependencies import SessionDep, UserTokenDep

from app.models import Employee, Enterprise, EmployeeEnterprise, Department, EmployeeDepartment
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
    response_model=List[employees_schemas.EmployeeResponse],
    summary="Получить список сотрудников"
)
async def list_employees(session: SessionDep,Bearer: UserTokenDep):
    stmt = select(Employee)
    result = await session.execute(stmt)
    employees = result.scalars().all()
    return employees

@router_employees.post(
    "",
    response_model=employees_schemas.EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать нового сотрудника"
)
async def create_employee(
    employee: employees_schemas.EmployeeCreate,
    session: SessionDep,
    current_user: UserTokenDep
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

@router_employees.post(
    "/invite-enterprise",
    status_code=status.HTTP_201_CREATED,
    summary="Пригласить сотрудника в предприятие"
)
async def invite_employee_to_enterprise(
    payload: employees_schemas.EmployeeEnterpriseInvite,
    session: SessionDep,
    current_user: UserTokenDep
):
    stmt = select(Employee).where(Employee.employee_id == payload.employee_id)
    result = await session.execute(stmt)
    employee = result.scalars().first()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    stmt = select(Enterprise).where(Enterprise.enterprise_id == payload.enterprise_id)
    result = await session.execute(stmt)
    enterprise = result.scalars().first()
    if not enterprise:
        raise HTTPException(status_code=404, detail="Предприятие не найдено")

    stmt = select(EmployeeEnterprise).where(
        EmployeeEnterprise.employee_id == payload.employee_id,
        EmployeeEnterprise.enterprise_id == payload.enterprise_id
    )
    result = await session.execute(stmt)
    association = result.scalars().first()
    if association:
        raise HTTPException(status_code=400, detail="Сотрудник уже прикреплён к данному предприятию")

    new_association = EmployeeEnterprise(
        employee_id=payload.employee_id,
        enterprise_id=payload.enterprise_id,
        role=payload.role
    )
    session.add(new_association)
    await session.commit()
    return {"message": "Сотрудник успешно приглашён в предприятие"}

@router_employees.post(
    "/assign-department",
    status_code=status.HTTP_201_CREATED,
    summary="Назначить сотрудника в отдел"
)
async def assign_employee_to_department(
    payload: employees_schemas.EmployeeDepartmentAssign,
    session: SessionDep,
    current_user: UserTokenDep
):
    stmt = select(Employee).where(Employee.employee_id == payload.employee_id)
    result = await session.execute(stmt)
    employee = result.scalars().first()
    if not employee:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    from app.models import Department  
    stmt = select(Department).where(Department.department_id == payload.department_id)
    result = await session.execute(stmt)
    department = result.scalars().first()
    if not department:
        raise HTTPException(status_code=404, detail="Отдел не найден")

    stmt = select(EmployeeDepartment).where(
        EmployeeDepartment.employee_id == payload.employee_id,
        EmployeeDepartment.department_id == payload.department_id
    )
    result = await session.execute(stmt)
    association = result.scalars().first()
    if association:
        raise HTTPException(status_code=400, detail="Сотрудник уже назначен в данный отдел")

    new_association = EmployeeDepartment(
        employee_id=payload.employee_id,
        department_id=payload.department_id,
        role=payload.role
    )
    session.add(new_association)
    await session.commit()
    return {"message": "Сотрудник успешно назначен в отдел"}

@router_employees.patch(
    "/{employee_id}/enterprise/{enterprise_id}",
    summary="Обновить роль сотрудника в предприятии"
)
async def update_employee_enterprise_role(
    employee_id: int,
    enterprise_id: int,
    payload: employees_schemas.EmployeeEnterpriseUpdate,
    session: SessionDep,
    current_user: UserTokenDep
):
    stmt = select(EmployeeEnterprise).where(
        EmployeeEnterprise.employee_id == employee_id,
        EmployeeEnterprise.enterprise_id == enterprise_id
    )
    result = await session.execute(stmt)
    association = result.scalars().first()
    if not association:
        raise HTTPException(status_code=404, detail="Ассоциация не найдена")
    association.role = payload.role
    await session.commit()
    return {"message": "Роль успешно обновлена"}

@router_employees.patch(
    "/{employee_id}/department/{department_id}",
    summary="Обновить роль сотрудника в отделе"
)
async def update_employee_department_role(
    employee_id: int,
    department_id: int,
    payload: employees_schemas.EmployeeDepartmentUpdate,
    session: SessionDep,
    current_user: UserTokenDep
):
    stmt = select(EmployeeDepartment).where(
        EmployeeDepartment.employee_id == employee_id,
        EmployeeDepartment.department_id == department_id
    )
    result = await session.execute(stmt)
    association = result.scalars().first()
    if not association:
        raise HTTPException(status_code=404, detail="Ассоциация не найдена")
    association.role = payload.role
    await session.commit()
    return {"message": "Роль успешно обновлена"}