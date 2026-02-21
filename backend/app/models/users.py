from sqlalchemy import create_engine, ForeignKey, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional

from ..database import Base


# users = [
#     {
#         "id": 1,
#         "email": "zzzatoox@mail.ru",
#         "login": "zzzatoox",
#         "password": "guzeevaTop123",
#         "last_name": "Лазарев",
#         "first_name": "Никита",
#         "patronymic": None,
#     }
# ]


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(30), nullable=False)
    login: Mapped[str] = mapped_column(String(20), nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    patronymic: Mapped[Optional[str]] = mapped_column(String)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, login={self.login!r})"
