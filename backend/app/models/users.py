from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320))
    login: Mapped[str] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(64))
    first_name: Mapped[str] = mapped_column(String(64))
    patronymic: Mapped[Optional[str]] = mapped_column(String(64))

    owned_tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="owner", foreign_keys="[Task.owner_id]"
    )
    assigned_tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="executor", foreign_keys="[Task.executor_id]"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, login={self.login!r})"
