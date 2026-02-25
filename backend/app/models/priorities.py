from ..database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from typing import List


class Priority(Base):
    __tablename__ = "priorities"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), unique=True)

    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="priority")

    def __repr__(self):
        return f"Priority(id={self.id!r}, title={self.title!r})"
