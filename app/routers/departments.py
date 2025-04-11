from typing import List, Optional
from app.dependencies import SessionDep
from app.models import Department
from app.schemas import auth as auth_schemas
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from app.schemas import departments as departments_schemas

router_departments = APIRouter(prefix="/departments", tags=["Departments"])

@router_departments.get(
    "",
    response_model=List[departments_schemas.DepartmentResponse]
)
async def list_departments(
    session: SessionDep
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
    session: SessionDep
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

