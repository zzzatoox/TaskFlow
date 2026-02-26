from sqlalchemy import String, ForeignKey, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

from datetime import datetime


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    executor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    priority_id: Mapped[int] = mapped_column(ForeignKey("priorities.id"))
    deadline: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped["User"] = relationship(
        "User", back_populates="owned_tasks", foreign_keys=[owner_id]
    )
    executor: Mapped["User"] = relationship(
        "User", back_populates="assigned_tasks", foreign_keys=[executor_id]
    )

    priority: Mapped["Priority"] = relationship("Priority", back_populates="tasks")

    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, title={self.title!r})"
