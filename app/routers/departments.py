from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import SessionDep, UserTokenDep
from app.models import Departaments, DepartamentsEmployees, Enterprises, Employees, EnterprisesEmployees
from app.schemas import departaments as departaments_schemas

router_departments = APIRouter(prefix="/departments", tags=["Отделы"])


@router_departments.get(
    "/me",
    response_model=List[departaments_schemas.DepartmentEmployeeResponse],
    summary="Получить мои отделы"
)
async def list_departments_me(
    session: SessionDep,
    current_user: UserTokenDep
):
    res = await DepartamentsEmployees.get_all_by_employee_id(session, current_user.id)
    return res


@router_departments.get(
    "",
    response_model=List[departaments_schemas.DepartmentResponse],
    summary="Получить список всех отделов"
)
async def list_departments(
    session: SessionDep,
):
    res = await Departaments.get_all(session)
    return res

@router_departments.post(
    "",
    response_model=departaments_schemas.DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый отдел в предприятии"
)
async def create_department(
    payload: departaments_schemas.DepartmentCreate,
    session: SessionDep,
):
    enterprice_exists = await Enterprises.get_by_id(session, payload.enterprise_id)
    if not enterprice_exists:
        raise HTTPException(
            404, "Предприятие не найдено"
        )
        
    new_department = Departaments(
        name=payload.name,
        enterprise_id=payload.enterprise_id
    )
    session.add(new_department)
    await session.commit()
    await session.refresh(new_department)
    return new_department


@router_departments.get(
    "/{departament_id}",
    response_model=departaments_schemas.DepartmentResponse,
    summary="Получить данные отдела предприятия"
)
async def get_department(
    departament_id: int,
    session: SessionDep,
):
    department = await Departaments.get_by_id(session, departament_id=departament_id)
    if not department:
        raise HTTPException(status_code=404, detail="Отдел не найден")

    return department


@router_departments.patch(
    "/{departament_id}",
    response_model=departaments_schemas.DepartmentResponse,
    summary="Обновить данные отдела предприятия"
)
async def update_department(
    departament_id: int,
    payload: departaments_schemas.DepartmentUpdate,
    session: SessionDep,
):
    department = await Departaments.get_by_id(session, departament_id)
    if not department:
        raise HTTPException(status_code=404, detail="Отдел не найден")
    
    department.name = payload.name or department.name
    
    await session.commit()
    await session.refresh(department)
    return department


@router_departments.delete(
    "/{departament_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить отдел предприятия"
)
async def delete_department(
    departament_id: int,
    session: SessionDep,
):
    department = await Departaments.get_by_id(session, departament_id)
    if not department:
        raise HTTPException(status_code=404, detail="Отдел не найден")
    await session.delete(department)
    await session.commit()
    return

@router_departments.get(
    "/{departament_id}/employees",
    response_model=List[departaments_schemas.DepartmentEmployeeResponse],
    summary="Получить список сотрудников отдела"
)
async def list_department_employees(
    departament_id: int,
    session: SessionDep,
):
    de = await DepartamentsEmployees.get_all_by_departament_id(session, departament_id)
    return de


@router_departments.post(
    "/{departament_id}/employees",
    response_model=departaments_schemas.DepartmentEmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить сотрудника в отдел с указанием роли"
)
async def add_employee_to_department(
    departament_id: int,
    payload: departaments_schemas.DepartmentEmployeeCreate,
    session: SessionDep,
):
    department = await Departaments.get_by_id(session, departament_id) 
    if not department:
        raise HTTPException(status_code=404, detail="Отдел не найден")
    
    de = await DepartamentsEmployees.get_by_employee_id_by_departament_id(session, payload.employee_id, departament_id)
    if de:
        raise HTTPException(
            409,
            "Сотрудник уже добавлен в этот отдел"
        )
    new_association = DepartamentsEmployees(
        employee_id=payload.employee_id,
        departament_id=departament_id,
    )
    session.add(new_association)
    await session.commit()
    await session.refresh(new_association)
    
    association = await DepartamentsEmployees.get_by_id(session, association.id)
    return association


@router_departments.patch(
    "/{departament_id}/employees/{employee_id}",
    response_model=departaments_schemas.DepartmentEmployeeResponse,
    summary="Обновить роль сотрудника в отделе"
)
async def update_employee_role_in_department(
    departament_id: int,
    employee_id: int,
    payload: departaments_schemas.DepartmentEmployeeUpdate,
    session: SessionDep,
):
    association = await DepartamentsEmployees.get_by_employee_id_by_departament_id(session, employee_id=employee_id, departament_id=departament_id)
    if not association:
        raise HTTPException(404, "Отдел не найден")
        
    association.role = payload.role or association.role
    await session.commit()
    await session.refresh(association)
    return association


@router_departments.delete(
    "/{department_id}/employees/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить сотрудника из отдела"
)
async def remove_employee_from_department(
    enterprise_id: int,
    department_id: int,
    employee_id: int,
    session: SessionDep,
):
    association = await DepartamentsEmployees.get_by_employee_id_by_departament_id(session, employee_id=employee_id, department_id=department_id)
    if not association:
        raise HTTPException(status_code=404, detail="Связь сотрудника с отделом не найдена")
    
    await session.delete(association)
    await session.commit()
    return

