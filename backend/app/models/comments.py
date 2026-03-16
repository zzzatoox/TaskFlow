from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, Text, DateTime, func, ForeignKey
from backend.app.database import Base
from datetime import datetime

import textwrap


class Comment(Base):
    __table_name__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Не буду делать ограничение на длину текста в бд, сделаю на уровне бэка
    comment: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    task: Mapped["Task"] = relationship(
        "Task", back_populates="comments", foreign_keys=[task_id]
    )
    author: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        text = (self.comment or "").replace("\n", " ")
        short = textwrap.shorten(text, width=60, placeholder="...")
        return f"Comment(id={self.id!r}, comment={short!r})"
