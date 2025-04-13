from sqlalchemy import ARRAY, Boolean, Integer, String, DateTime, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional, List
from app.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Documents, DepartamentsEmployees, EnterprisesEmployees, Messages

class Employees(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    phone: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(50))
    last_name: Mapped[Optional[str]] = mapped_column(String(50))
    
    big_boss: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false')
    
    enterprises: Mapped[List["EnterprisesEmployees"]] = relationship("EnterprisesEmployees", back_populates="employee")
    departments_assoc: Mapped[List["DepartamentsEmployees"]] = relationship("DepartamentsEmployees", back_populates="employee")
    documents_sent: Mapped[List["Documents"]] = relationship("Documents", foreign_keys="[Documents.sender_id]", back_populates="sender")
    documents_received: Mapped[List["Documents"]] = relationship("Documents", foreign_keys="[Documents.recipient_id]", back_populates="recipient")

    messages_sent: Mapped[List["Messages"]] = relationship("Messages", foreign_keys="[Messages.sender_id]", back_populates="sender")
    messages_received: Mapped[List["Messages"]] = relationship("Messages", foreign_keys="[Messages.recipient_id]", back_populates="recipient")

    @staticmethod
    async def get_all(session: AsyncSession) -> List['Employees']:
        stmt = select(Employees)
        res = await session.execute(stmt)
        return res.scalars().all()
    

    @staticmethod
    async def get_by_phone(session: AsyncSession, phone: str) -> Optional['Employees']:
        stmt = (
            select(Employees)
            .where(Employees.phone == phone)
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none() 
    
    @staticmethod
    async def get_by_id(session: AsyncSession, employee_id: int) -> "Employees":
        stmt = (
            select(Employees)
            .where(Employees.id == employee_id)
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()