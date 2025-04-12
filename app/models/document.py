import enum
from sqlalchemy import Integer, String, Text, ForeignKey, Enum as SAEnum, DateTime, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional, List
from app.base import Base


class DocumentStatus(enum.Enum):
    pending = "Ожидает подписание"
    signed = "Подписан"


class Document(Base):
    __tablename__ = "document"

    document_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee.employee_id"), nullable=False)
    enterprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("enterprise.enterprise_id"), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[DocumentStatus] = mapped_column(SAEnum(DocumentStatus), nullable=False, default=DocumentStatus.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    enterprise: Mapped["Enterprise"] = relationship("Enterprise", back_populates="documents")
    sender: Mapped["Employee"] = relationship("Employee")

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> "Document":
        document = cls(**kwargs)
        session.add(document)
        await session.commit()
        await session.refresh(document)
        return document

    async def update(self, session: AsyncSession, **kwargs) -> "Document":
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
    async def get_by_id(cls, session: AsyncSession, document_id: int) -> Optional["Document"]:
        result = await session.get(cls, document_id)
        return result

    @classmethod
    async def get_all(cls, session: AsyncSession) -> List["Document"]:
        result = await session.execute(select(cls))
        return result.scalars().all()
