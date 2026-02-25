from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(30), nullable=False)
    login: Mapped[str] = mapped_column(String(20), nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    patronymic: Mapped[Optional[str]] = mapped_column(String)

    owned_tasks: Mapped[List["Task"]] = relationship("Task", back_populates="owner")
    assigned_tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="executor"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, login={self.login!r})"
