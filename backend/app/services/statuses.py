from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import Depends, HTTPException

from typing import Annotated

from backend.app.dependencies import get_async_session
from backend.app.models.statuses import Status as StatusModel
from backend.app.schemas.statuses import StatusCreate, StatusUpdate

from backend.app.utils.custom_exceptions import (
    InternalServerException,
    StatusNotFoundException,
)


async def get_all_statuses(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    result = await session.scalars(select(StatusModel))
    if not result:
        raise StatusNotFoundException("No statuses found")
    return result.all()


async def get_status_by_id(
    status_id: int, session: Annotated[AsyncSession, Depends(get_async_session)]
) -> StatusModel | None:
    status = (
        await session.scalars(select(StatusModel).where(StatusModel.id == status_id))
    ).first()
    if not status:
        raise StatusNotFoundException(f"Status with id {status_id} not found")
    return status


async def add_status(
    status_obj: StatusCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> StatusModel:
    status = StatusModel(**status_obj.model_dump())
    session.add(status)
    try:
        await session.commit()
        await session.refresh(status)
    except Exception:
        await session.rollback()
        raise InternalServerException("Unexpected error while adding status")
    return status


async def delete_status(
    status_id: int, session: Annotated[AsyncSession, Depends(get_async_session)]
):
    status = await get_status_by_id(status_id, session)
    if not status:
        raise StatusNotFoundException(f"Status with id {status_id} not found")
    await session.delete(status)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise InternalServerException("Unexpected error while deleting status")
    return HTTPException(status_code=204, detail=f"Status with id {status_id} deleted")


async def get_status_by_title(
    title: str, session: Annotated[AsyncSession, Depends(get_async_session)]
) -> StatusModel | None:
    status = (
        await session.scalars(select(StatusModel).where(StatusModel.title == title))
    ).first()
    return status


async def update_status(
    status_id: int,
    new_title: StatusUpdate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    # TODO: подумать, нужно ли делать проверку, если все поля None, то не обновлять, а возвращать ошибку.
    status = await get_status_by_id(status_id, session)
    if not status:
        raise StatusNotFoundException(f"Status with id {status_id} not found")

    # If no new title provided, nothing to update
    if new_title.title is None:
        return status

    existing = await get_status_by_title(new_title.title, session)
    if existing and existing.id != status.id:
        raise InternalServerException(
            f"Status with title {new_title.title} already exists"
        )

    status.title = new_title.title
    try:
        await session.commit()
        await session.refresh(status)
    except Exception:
        await session.rollback()
        raise InternalServerException("Unexpected error while updating status")
    return status


# TODO: добавить функции с фильтрацией.
