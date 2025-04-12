from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from app.base import Base

if TYPE_CHECKING:
    from app.models import Enterprise, Employee
    
class Department(Base):
    __tablename__ = "department"

    department_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    enterprise_id: Mapped[int] = mapped_column(Integer, ForeignKey("enterprise.enterprise_id"), nullable=False)

    enterprise: Mapped["Enterprise"] = relationship("Enterprise", back_populates="departments")
    employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="department")

    @classmethod
    def create(cls, session: Session, **kwargs) -> "Department":
        department = cls(**kwargs)
        session.add(department)
        session.commit()
        return department

    def add_employee(self, session: Session, employee: "Employee"):
        employee.department_id = self.department_id
        session.commit()

    def update(self, session: Session, **kwargs) -> "Department":
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        session.commit()
        return self

    def delete(self, session: Session):
        session.delete(self)
        session.commit()

    @classmethod
    def get_by_id(cls, session: Session, department_id: int) -> Optional["Department"]:
        return session.query(cls).filter_by(department_id=department_id).first()

    @classmethod
    def get_all(cls, session: Session) -> List["Department"]:
        return session.query(cls).all()
