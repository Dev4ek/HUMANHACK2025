from sqlalchemy import Integer, String, DateTime, ForeignKey, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from app.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Employees, Departaments, Documents

class Enterprises(Base):
    __tablename__ = "enterprises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    
    departments: Mapped[List["Departaments"]] = relationship("Departaments", back_populates="enterprise")
    employees: Mapped[List["EnterprisesEmployees"]] = relationship("EnterprisesEmployees", back_populates="enterprise")

    @staticmethod
    async def get_all(session: AsyncSession) -> List['Enterprises']:
        stmt = (
            select(Enterprises)
        )
        res = await session.execute(stmt)
        return res.scalars().all()
    
    @staticmethod
    async def get_by_id(session: AsyncSession, enterprise_id: int) -> "Enterprises":
        stmt = (
            select(Enterprises)
            .where(Enterprises.id == enterprise_id)
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()
    
    
class EnterprisesEmployees(Base):
    __tablename__ = "enterprises_employees"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    employee_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("employees.id"), nullable=True)
    enterprise_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("enterprises.id"), nullable=True)
    
    employee: Mapped["Employees"] = relationship("Employees", back_populates="enterprises")
    enterprise: Mapped["Enterprises"] = relationship("Enterprises", back_populates="employees")
    
    @staticmethod
    async def get_all_by_enterprise_id(session: AsyncSession, enterprise_id: int) -> List['EnterprisesEmployees']:
        stmt = (
            select(EnterprisesEmployees)
            .where(EnterprisesEmployees.enterprise_id == enterprise_id)
            .options(
                selectinload(EnterprisesEmployees.employee),
                selectinload(EnterprisesEmployees.enterprise)
            )
        )
        res = await session.execute(stmt)
        return res.scalars().all()
    
    @staticmethod
    async def get_all_by_employee_id(session: AsyncSession, employee_id: int) -> List['EnterprisesEmployees']:
        stmt = (
            select(EnterprisesEmployees)
            .where(EnterprisesEmployees.employee_id == employee_id)
            .options(
                selectinload(EnterprisesEmployees.employee),
                selectinload(EnterprisesEmployees.enterprise)
            )
        )
        res = await session.execute(stmt)
        return res.scalars().all()
    
    @staticmethod
    async def get_by_employee_id_by_enterprise_id(session: AsyncSession, employee_id: int, enterprise_id: int) -> Optional['EnterprisesEmployees']:
        stmt = (
            select(EnterprisesEmployees)
            .where(
                EnterprisesEmployees.employee_id == employee_id,
                EnterprisesEmployees.enterprise_id == enterprise_id
            )
        )
        res = await session.execute(stmt)  
        return res.scalar_one_or_none()