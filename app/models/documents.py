import enum
from sqlalchemy import Integer, String, Text, ForeignKey, Enum as SAEnum, DateTime, select, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional, List
from app.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Employees, Enterprises

class DocumentStatus(enum.Enum):
    pending = "Ожидает подписания"
    signed = "Подписан"
    cancelled = "Отклонён"

class Documents(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    file_path: Mapped[str] = mapped_column(String)
    signature: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[DocumentStatus] = mapped_column(SAEnum(DocumentStatus), default=DocumentStatus.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, server_default=text("now()"))
    signed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    sender: Mapped["Employees"] = relationship("Employees", foreign_keys=[sender_id], back_populates="documents_sent")
    recipient: Mapped["Employees"] = relationship("Employees", foreign_keys=[recipient_id], back_populates="documents_received")

    @staticmethod
    async def get_by_sender_id(session: AsyncSession, sender_id: int) -> List["Documents"]:
        stmt = (
            select(Documents)
            .where(Documents.sender_id == sender_id)
        )
        res = await session.execute(stmt)
        return res.scalars().all()
    
    @staticmethod
    async def get_by_recipient_id(session: AsyncSession, recipient_id: int) -> List['Documents']:
        stmt = (
            select(Documents)
            .where(Documents.recipient == recipient_id)
        )
        res = await session.execute(stmt)
        return res.scalars().all()
    
    @staticmethod
    async def get_by_id(session: AsyncSession, document_id: int) -> 'Documents':
        stmt = (
            select(Documents)
            .where(Documents.id == document_id)
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()
    