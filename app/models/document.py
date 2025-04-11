import random
from typing import List, Optional
from sqlalchemy import (
    ForeignKey,
    String,
    Integer,
    Boolean,
    Numeric,
    BigInteger,
    Sequence,
    Text,
    and_,
    func,
    or_,
    select,
    text,
    update,
    DateTime,
    UUID as PostgresUUID,
    or_,
    JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from app.base import Base
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TYPE_CHECKING
from datetime import datetime, timedelta
from app.utils.main import get_moscow_time

if TYPE_CHECKING:
    from app.models import Employee

class Document(Base):
    __tablename__ = "document"

    document_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee.employee_id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    sender: Mapped["Employee"] = relationship("Employee", back_populates="documents_created")
    recipients: Mapped[List["DocumentRecipient"]] = relationship("DocumentRecipient", back_populates="document", cascade="all, delete-orphan")
    signatures: Mapped[List["DocumentSignature"]] = relationship("DocumentSignature", back_populates="document", cascade="all, delete-orphan")

class DocumentRecipient(Base):
    __tablename__ = "document_recipient"

    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("document.document_id"), primary_key=True)
    recipient_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee.employee_id"), primary_key=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    # Связи: связь с документом и получателем (сотрудником)
    document: Mapped["Document"] = relationship("Document", back_populates="recipients")
    recipient: Mapped["Employee"] = relationship("Employee", back_populates="document_recipients")

class DocumentSignature(Base):
    __tablename__ = "document_signature"

    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("document.document_id"), primary_key=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee.employee_id"), primary_key=True)
    signature: Mapped[str] = mapped_column(String(255), nullable=False)
    signed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    confirmation_method: Mapped[str] = mapped_column(String(50), nullable=False)

    # Связи: связь с документом и сотрудником, подписывающим его
    document: Mapped["Document"] = relationship("Document", back_populates="signatures")
    employee: Mapped["Employee"] = relationship("Employee", back_populates="signatures")