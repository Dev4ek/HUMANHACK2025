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
    from app.models import Document, DocumentSignature, DocumentRecipient, Enterprise, Department
    
class Employee(Base):
    __tablename__ = "employee"

    employee_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)

    enterprise_associations: Mapped[List["EmployeeEnterprise"]] = relationship("EmployeeEnterprise", back_populates="employee", cascade="all, delete-orphan")
    department_associations: Mapped[List["EmployeeDepartment"]] = relationship("EmployeeDepartment", back_populates="employee", cascade="all, delete-orphan")
    documents_created: Mapped[List["Document"]] = relationship("Document", back_populates="sender", cascade="all, delete-orphan")
    signatures: Mapped[List["DocumentSignature"]] = relationship("DocumentSignature", back_populates="employee", cascade="all, delete-orphan")
    document_recipients: Mapped[List["DocumentRecipient"]] = relationship("DocumentRecipient", back_populates="recipient", cascade="all, delete-orphan")

class EmployeeEnterprise(Base):
    __tablename__ = "employee_enterprise"

    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee.employee_id"), primary_key=True)
    enterprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("enterprise.enterprise_id"), primary_key=True)
    role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    employee: Mapped["Employee"] = relationship("Employee", back_populates="enterprise_associations")
    enterprise: Mapped["Enterprise"] = relationship("Enterprise", back_populates="employee_associations")

class EmployeeDepartment(Base):
    __tablename__ = "employee_department"

    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee.employee_id"), primary_key=True)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("department.department_id"), primary_key=True)
    role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    employee: Mapped["Employee"] = relationship("Employee", back_populates="department_associations")
    department: Mapped["Department"] = relationship("Department", back_populates="employee_associations")

