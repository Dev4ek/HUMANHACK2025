from sqlalchemy import Integer, String, DateTime, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional, List
from app.base import Base



# Модель таблицы employee
class Employee(Base):
    __tablename__ = "employee"

    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    position: Mapped[str] = mapped_column(String(255), nullable=False)
    department_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("department.department_id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    user: Mapped["Users"] = relationship("Users", back_populates="employee")
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="employees")
    enterprises_boss: Mapped[List["Enterprise"]] = relationship("Enterprise", back_populates="boss", foreign_keys="Enterprise.boss_id")
    documents_sent: Mapped[List["Document"]] = relationship("Document", back_populates="sender")
    
    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> "Employee":
        employee = cls(**kwargs)
        session.add(employee)
        await session.commit()
        await session.refresh(employee)
        return employee

    async def update(self, session: AsyncSession, **kwargs) -> "Employee":
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        await session.commit()
        await session.refresh(self)
        return self

    async def delete(self, session: AsyncSession):
        await session.delete(self)
        await session.commit()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, employee_id: int) -> Optional["Employee"]:
        result = await session.get(cls, employee_id)
        return result

    @classmethod
    async def get_all(cls, session: AsyncSession) -> List["Employee"]:
        result = await session.execute(select(cls))
        return result.scalars().all()
