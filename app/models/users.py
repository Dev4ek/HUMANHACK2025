from datetime import datetime
from typing import List, Optional
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from app.base import Base

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Связь "один к одному" с Employee
    employee: Mapped[Optional["Employee"]] = relationship("Employee", back_populates="user", uselist=False)

    # CRUD методы:
    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> "Users":
        user = cls(**kwargs)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def update(self, session: AsyncSession, **kwargs) -> "Users":
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
    async def get_by_id(cls, session: AsyncSession, user_id: int) -> Optional["Users"]:
        return await session.get(cls, user_id)

    @classmethod
    async def get_by_phone(cls, session: AsyncSession, phone: str) -> Optional["Users"]:
        result = await session.execute(
            select(cls).filter_by(phone=phone)
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, session: AsyncSession) -> List["Users"]:
        result = await session.execute(select(cls))
        return result.scalars().all()
