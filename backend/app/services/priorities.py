from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import Depends, HTTPException

from typing import Annotated

from backend.app.dependencies import get_async_session
from backend.app.models.priorities import Priority as PriorityModel

from backend.app.schemas.priorities import PriorityCreate, PriorityUpdate
from backend.app.utils.custom_exceptions import (
    InternalServerException,
    PriorityNotFoundException,
)


async def get_all_priorities(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    result = await session.scalars(select(PriorityModel))
    if not result:
        raise PriorityNotFoundException("No priorities found")
    return result.all()


async def get_priority_by_id(
    priority_id: int, session: Annotated[AsyncSession, Depends(get_async_session)]
) -> PriorityModel | None:
    priority = (
        await session.scalars(
            select(PriorityModel).where(PriorityModel.id == priority_id)
        )
    ).first()
    if not priority:
        raise PriorityNotFoundException(f"Priority with id {priority_id} not found")
    return priority


async def add_priority(
    priority_obj: PriorityCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> PriorityModel:
    priority = PriorityModel(**priority_obj.model_dump())
    session.add(priority)
    try:
        await session.commit()
        await session.refresh(priority)
    except Exception:
        await session.rollback()
        raise InternalServerException("Unexpected error while adding priority")
    return priority


async def delete_priority(
    priority_id: int, session: Annotated[AsyncSession, Depends(get_async_session)]
):
    priority = await get_priority_by_id(priority_id, session)
    if not priority:
        raise PriorityNotFoundException(f"Priority with id {priority_id} not found")
    await session.delete(priority)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise InternalServerException("Unexpected error while deleting priority")
    return HTTPException(
        status_code=204, detail=f"Priority with id {priority_id} deleted"
    )


async def get_priority_by_title(
    title: str, session: Annotated[AsyncSession, Depends(get_async_session)]
) -> PriorityModel | None:
    priority = (
        await session.scalars(select(PriorityModel).where(PriorityModel.title == title))
    ).first()
    return priority


async def update_priority(
    priority_id: int,
    new_title: PriorityUpdate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    # TODO: подумать, нужно ли делать проверку, если все поля None, то не обновлять, а возвращать ошибку.
    priority = await get_priority_by_id(priority_id, session)
    if not priority:
        raise PriorityNotFoundException(f"Priority with id {priority_id} not found")

    # If no new title provided, nothing to update
    if new_title.title is None:
        return priority

    existing = await get_priority_by_title(new_title.title, session)
    if existing and existing.id != priority.id:
        raise InternalServerException(
            f"Priority with title {new_title.title} already exists"
        )

    priority.title = new_title.title
    try:
        await session.commit()
        await session.refresh(priority)
    except Exception:
        await session.rollback()
        raise InternalServerException("Unexpected error while updating priority")
    return priority


# TODO: добавить функции с фильтрацией.
