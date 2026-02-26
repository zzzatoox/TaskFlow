from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import Depends

from typing import Annotated

from backend.app.dependencies import get_async_session
from backend.app.models.priorities import Priority as PriorityModel


async def get_all_priorities(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    result = await session.scalars(select(PriorityModel))
    return result.all()


async def get_priority_by_id(
    priority_id: int, session: Annotated[AsyncSession, Depends(get_async_session)]
) -> PriorityModel | None:
    priority = session.scalars(
        select(PriorityModel).where(PriorityModel.id == priority_id)
    ).first()
    return priority


async def add_priority(
    title: str, session: Annotated[AsyncSession, Depends(get_async_session)]
) -> PriorityModel:
    priority = PriorityModel(title=title)
    session.add(priority)
    await session.commit()
    await session.refresh(priority)
    return priority


# TODO: добавить функции с фильтрацией.
