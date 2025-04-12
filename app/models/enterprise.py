from sqlalchemy import Integer, String, DateTime, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from app.base import Base


class Enterprise(Base):
    __tablename__ = "enterprise"

    enterprise_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    boss_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("employee.employee_id"), nullable=True)

    boss: Mapped[Optional["Employee"]] = relationship("Employee", foreign_keys=[boss_id])
    departments: Mapped[List["Department"]] = relationship("Department", back_populates="enterprise", cascade="all, delete-orphan")
    employee_associations: Mapped[List["EmployeeEnterprise"]] = relationship("EmployeeEnterprise", back_populates="enterprise", cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="enterprise", cascade="all, delete-orphan")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> "Enterprise":
        enterprise = cls(**kwargs)
        session.add(enterprise)
        await session.commit()
        await session.refresh(enterprise)
        return enterprise

    async def update(self, session: AsyncSession, **kwargs) -> "Enterprise":
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
    async def get_by_id(cls, session: AsyncSession, enterprise_id: int) -> Optional["Enterprise"]:
        result = await session.get(cls, enterprise_id)
        return result

    @classmethod
    async def get_all(cls, session: AsyncSession) -> List["Enterprise"]:
        result = await session.execute(select(cls))
        return result.scalars().all()
