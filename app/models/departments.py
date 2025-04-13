from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session, selectinload
from app.base import Base
from sqlalchemy.ext.asyncio import AsyncSession


if TYPE_CHECKING:
    from app.models import Enterprises, Employees
    
class Departaments(Base):
    __tablename__ = "departaments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    enterprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("enterprises.id"))

    boss_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("employees.id"), nullable=True)

    boss: Mapped[Optional["Employees"]] = relationship("Employees", back_populates="departaments_boss")
    enterprise: Mapped["Enterprises"] = relationship("Enterprises", back_populates="departments")
    employees: Mapped[List["DepartamentsEmployees"]] = relationship("DepartamentsEmployees", back_populates="department")


    @staticmethod
    async def get_all(session: AsyncSession) -> List['Departaments']:
        stmt = (
            select(Departaments)
        )
        res = await session.execute(stmt)
        return res.scalars().all()
    
    @staticmethod
    async def get_by_id(session: AsyncSession, departament_id: int) -> "Departaments":
        stmt = (
            select(Departaments)
            .where(Departaments.id == departament_id)
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

class DepartamentsEmployees(Base):
    __tablename__ = "departaments_employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    employee_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("employees.id"))
    departament_id: Mapped[int] = mapped_column(Integer, ForeignKey("departaments.id"))
    role: Mapped[str] = mapped_column(String, nullable=True)

    department: Mapped["Departaments"] = relationship("Departaments", back_populates="employees")
    employee: Mapped["Employees"] = relationship("Employees", back_populates="departments_assoc")

    @staticmethod
    async def get_all_by_departament_id(session: AsyncSession, departament_id: int) -> List['DepartamentsEmployees']:
        stmt = (
            select(DepartamentsEmployees)
            .where(DepartamentsEmployees.departament_id == departament_id)
            .options(
                selectinload(DepartamentsEmployees.department),
                selectinload(DepartamentsEmployees.employee)
            )
        )
        res = await session.execute(stmt)
        return res.scalars().all()

    @staticmethod
    async def get_by_employee_id_by_departament_id(session: AsyncSession, employee_id: int, departament_id: int) -> Optional['DepartamentsEmployees']:
        stmt = (
            select(DepartamentsEmployees)
            .where(
                DepartamentsEmployees.departament_id == departament_id, 
                DepartamentsEmployees.employee_id == employee_id, 
            )
            .options(
                selectinload(DepartamentsEmployees.department),
                selectinload(DepartamentsEmployees.employee)
            )
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()
    
    @staticmethod
    async def get_by_id(session: AsyncSession, de_id: int) -> Optional['DepartamentsEmployees']:
        stmt = (
            select(DepartamentsEmployees)
            .where(
                DepartamentsEmployees.id == de_id, 
            )
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()
    
    @staticmethod
    async def get_all_by_employee_id(session: AsyncSession, employee_id: int) -> List['DepartamentsEmployees']:
        stmt = (
            select(DepartamentsEmployees)
            .where(
                DepartamentsEmployees.employee_id == employee_id, 
            )
            .options(
                selectinload(DepartamentsEmployees.department),
                selectinload(DepartamentsEmployees.employee)
            )
        )
        res = await session.execute(stmt)
        return res.scalars().all()