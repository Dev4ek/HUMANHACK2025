from sqlalchemy import Integer, String, DateTime, ForeignKey, func, select, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from app.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Employees

class Messages(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"))
    message: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, server_default='now()')
    
    sender: Mapped["Employees"] = relationship("Employees",foreign_keys=[sender_id], back_populates="messages_sent")
    recipient: Mapped["Employees"] = relationship("Employees",foreign_keys=[recipient_id], back_populates="messages_received")


    