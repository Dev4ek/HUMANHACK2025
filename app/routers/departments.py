from typing import List, Optional
from app.dependencies import SessionDep, UserTokenDep
from app.models import Department, Employee, EmployeeDepartment
from app.schemas import auth as auth_schemas
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from app.schemas import departments as departments_schemas
from app.schemas import employees as employees_schemas
from app.dependencies import SessionDep, UserTokenDep

router_departments = APIRouter(prefix="/departments", tags=["Departments"])

@router_departments.get(
    "",
    response_model=List[departments_schemas.DepartmentResponse]
)
async def list_departments(
    session: SessionDep,
    current_user: UserTokenDep
):
    stmt = (
        select(Department)
    )
    result = await session.execute(stmt)
    departments = result.scalars().all()
    return departments


@router_departments.post(
    "",
    response_model=departments_schemas.DepartmentResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_department(
    department: departments_schemas.DepartmentCreate,
    session: SessionDep,
    current_user: UserTokenDep
):
    stmt = (
        select(departments_schemas.Enterprise)
        .where(departments_schemas.Enterprise.enterprise_id == department.enterprise_id)
    )
    result = await session.execute(stmt)
    enterprise = result.scalars().first()
    
    if not enterprise:
        raise HTTPException(status_code=404, detail="Предприятие не найдено")
    
    new_department = Department(
        enterprise_id=department.enterprise_id,
        name=department.name
    )
    session.add(new_department)
    await session.commit()
    await session.refresh(new_department)
    return new_department


@router_departments.patch(
    "/{department_id}/boss",
    summary="Назначить начальника отдела"
)
async def assign_department_boss(
    department_id: int,
    payload: departments_schemas.BossAssign,
    session: SessionDep,
    current_user: UserTokenDep
):
    stmt = select(Department).where(Department.department_id == department_id)
    result = await session.execute(stmt)
    department = result.scalars().first()
    if not department:
        raise HTTPException(status_code=404, detail="Отдел не найден")
        
    stmt = select(Employee).where(Employee.employee_id == payload.boss_id)
    result = await session.execute(stmt)
    boss = result.scalars().first()
    if not boss:
        raise HTTPException(status_code=404, detail="Сотрудник-босс не найден")

    department.boss_id = payload.boss_id
    await session.commit()
    return {"message": "Начальник отдела успешно назначен"}


@router_departments.get(
    "/{department_id}/employees",
    response_model=List[employees_schemas.EmployeeResponse],
    summary="Получить сотрудников отдела по ID"
)
async def get_department_employees(
    department_id: int,
    session: SessionDep,
    current_user: UserTokenDep
):
    stmt = (
        select(Employee)
        .join(EmployeeDepartment, Employee.employee_id == EmployeeDepartment.employee_id)
        .where(EmployeeDepartment.department_id == department_id)
    )
    result = await session.execute(stmt)
    employees = result.scalars().all()
    if not employees:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сотрудники не найдены для данного отдела"
        )
    return employees