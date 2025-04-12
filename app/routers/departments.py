from typing import List
from fastapi import APIRouter, HTTPException, status
from app.dependencies import SessionDep, UserTokenDep
from app.models import Department, Employee, Enterprise
from app.schemas import departments as departments_schemas

router_departments = APIRouter(prefix="/departments", tags=["Отделы"])


@router_departments.get(
    "",
    response_model=List[departments_schemas.DepartmentResponse],
    summary="Получить список всех отделов",
    description="Возвращает список всех отделов."
)
async def list_departments(
    session: SessionDep,
    current_user: UserTokenDep
):
    return await Department.get_all(session)


@router_departments.get(
    "/{department_id}",
    response_model=departments_schemas.DepartmentResponse,
    summary="Получить отдел по ID",
    description="Возвращает данные отдела по его ID."
)
async def get_department(
    department_id: int,
    session: SessionDep,
    current_user: UserTokenDep
):
    department = await Department.get_by_id(session, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Отдел не найден")
    return department


@router_departments.post(
    "",
    response_model=departments_schemas.DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать отдел",
    description="Создать новый отдел может только начальник компании."
)
async def create_department(
    data: departments_schemas.DepartmentCreate,
    session: SessionDep,
    current_user: UserTokenDep
):
    employee = await Employee.get_by_id(session, current_user.employee_id)
    if not employee:
        raise HTTPException(status_code=403, detail="Нет доступа")

    if not employee.department_id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    enterprise = await Enterprise.get_by_id(session, employee.department.enterprise_id)
    if not enterprise or enterprise.boss_id != employee.employee_id:
        raise HTTPException(status_code=403, detail="Создавать отделы может только начальник компании")

    department = await Department.create(session, name=data.name, enterprise_id=enterprise.enterprise_id)
    return department


@router_departments.patch(
    "/{department_id}",
    response_model=departments_schemas.DepartmentResponse,
    summary="Редактировать отдел",
    description="Редактировать отдел может только начальник компании или начальник этого отдела."
)
async def update_department(
    department_id: int,
    data: departments_schemas.DepartmentUpdate,
    session: SessionDep,
    current_user: UserTokenDep
):
    department = await Department.get_by_id(session, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Отдел не найден")

    employee = await Employee.get_by_id(session, current_user.employee_id)
    if not employee:
        raise HTTPException(status_code=403, detail="Нет доступа")

    enterprise = await Enterprise.get_by_id(session, department.enterprise_id)

    if enterprise.boss_id != employee.employee_id and department.department_id != employee.department_id:
        raise HTTPException(status_code=403, detail="Редактировать может только начальник компании или отдела")

    await department.update(session, **data.dict(exclude_unset=True))
    return department


@router_departments.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить отдел",
    description="Удалить отдел может только начальник компании или начальник этого отдела."
)
async def delete_department(
    department_id: int,
    session: SessionDep,
    current_user: UserTokenDep
):
    department = await Department.get_by_id(session, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Отдел не найден")

    employee = await Employee.get_by_id(session, current_user.employee_id)
    if not employee:
        raise HTTPException(status_code=403, detail="Нет доступа")

    enterprise = await Enterprise.get_by_id(session, department.enterprise_id)

    if enterprise.boss_id != employee.employee_id and department.department_id != employee.department_id:
        raise HTTPException(status_code=403, detail="Удалять может только начальник компании или отдела")

    await department.delete(session)
