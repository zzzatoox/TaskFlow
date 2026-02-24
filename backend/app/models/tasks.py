from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base

from datetime import datetime


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50))

    # TODO: прочитать как устанавливать связи таблиц
    description: Mapped[str]
    owner_id: Mapped[int]
    executor_id: Mapped[int]

    # TODO: создать таблицу priorities
    priority_id: Mapped[int]

    # TODO: проверить как устанавливаются значения для datetime в sqlalchemy
    # прочитать как указывать дефолтное значение now()
    # первое предположение - написать функцию, где буду делать datetime now
    deadline: Mapped[datetime]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]

    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, title={self.title!r})"
