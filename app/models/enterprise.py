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
    from app.models import Department, EmployeeEnterprise
    
    
class Enterprise(Base):
    __tablename__ = "enterprise"

    enterprise_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    departments: Mapped[List["Department"]] = relationship("Department", back_populates="enterprise", cascade="all, delete-orphan")
    employee_associations: Mapped[List["EmployeeEnterprise"]] = relationship("EmployeeEnterprise", back_populates="enterprise", cascade="all, delete-orphan")
