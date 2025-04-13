import enum
from sqlalchemy import Integer, String, Text, ForeignKey, Enum as SAEnum, DateTime, select
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
    status: Mapped[DocumentStatus] = mapped_column(SAEnum(DocumentStatus), default=DocumentStatus.pending)

    sender: Mapped["Employees"] = relationship("Employees", foreign_keys=[sender_id], back_populates="documents_sent")
    recipient: Mapped["Employees"] = relationship("Employees", foreign_keys=[recipient_id], back_populates="documents_received")
