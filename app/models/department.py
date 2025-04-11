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
    from app.models import Enterprise, EmployeeDepartment
    
class Department(Base):
    __tablename__ = "department"

    department_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    enterprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("enterprise.enterprise_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    enterprise: Mapped["Enterprise"] = relationship("Enterprise", back_populates="departments")
    employee_associations: Mapped[List["EmployeeDepartment"]] = relationship("EmployeeDepartment", back_populates="department", cascade="all, delete-orphan")
