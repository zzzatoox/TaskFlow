from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import Depends

from typing import Annotated

from datetime import datetime

from backend.app.dependencies import get_async_session
from backend.app.models.tasks import Task as TaskModel

from backend.app.schemas.tasks import TaskCreate, TaskUpdate
from backend.app.services.users import get_user_by_id
from backend.app.utils.custom_exceptions import (
    TaskNotFoundException,
    TaskAccessDeniedException,
    IntegrityErrorException,
    InternalServerException,
    ValidationException,
)


# TODO: посмотреть, можно ли объявить свой тип, чтобы сократить Annotated[AsyncSession, Depends(get_async_session)]
def ensure_timezone_aware(value: datetime | None, field_name: str) -> None:
    if value is None:
        return

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValidationException(
            f"{field_name} must include timezone, for example 2026-03-13T12:00:00Z"
        )


def validate_task_date_range(
    start_date: datetime | None,
    end_date: datetime | None,
) -> None:
    if start_date and end_date and start_date > end_date:
        raise ValidationException(
            "start_date must be earlier than or equal to end_date"
        )


async def get_all_tasks(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    skip: int = 0,
    limit: int = 10,
    status: str | None = None,
    priority: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
):
    ensure_timezone_aware(start_date, "start_date")
    ensure_timezone_aware(end_date, "end_date")
    validate_task_date_range(start_date, end_date)

    query = select(TaskModel).where(TaskModel.owner_id == user_id)

    if start_date and end_date:
        query = query.where(TaskModel.created_at.between(start_date, end_date))
    elif start_date:
        query = query.where(TaskModel.created_at >= start_date)
    elif end_date:
        query = query.where(TaskModel.created_at <= end_date)

    if status:
        query = query.where(TaskModel.status.has(title=status))
    if priority:
        query = query.where(TaskModel.priority.has(title=priority))

    query = query.order_by(TaskModel.id).offset(skip).limit(limit)
    result = await session.scalars(query)
    return result.all()


async def get_task_by_id(
    task_id: int,
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    task = (
        await session.scalars(select(TaskModel).where(TaskModel.id == task_id))
    ).first()
    if not task:
        raise TaskNotFoundException(f"Task with id {task_id} not found")
    if task.owner_id != user_id:
        raise TaskAccessDeniedException(
            f"User with id {user_id} does not have permission to access task with id {task_id}"
        )
    return task


async def create_task(
    task_data: TaskCreate,
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    task_data = task_data.model_dump()
    task_data["owner_id"] = user_id

    executor_id = task_data.get("executor_id")
    if executor_id is not None:
        await get_user_by_id(executor_id, session)

    task = TaskModel(**task_data)
    session.add(task)
    try:
        await session.commit()
        await session.refresh(task)
    except IntegrityError:
        await session.rollback()
        raise IntegrityErrorException("Database integrity error")
    except Exception:
        await session.rollback()
        raise InternalServerException("Unexpected error while creating task")
    return task


async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    task = await get_task_by_id(task_id, user_id, session)
    for key, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    try:
        await session.commit()
        await session.refresh(task)
    except IntegrityError:
        await session.rollback()
        raise IntegrityErrorException("Database integrity error")
    except Exception:
        await session.rollback()
        raise InternalServerException("Unexpected error while updating task")
    return task


async def delete_task(
    task_id: int,
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    task = await get_task_by_id(task_id, user_id, session)
    if not task:
        raise TaskNotFoundException(f"Task with id {task_id} not found")

    owner_id = task.owner_id
    if owner_id != user_id:
        raise TaskAccessDeniedException(
            f"User with id {user_id} does not have permission to delete task with id {task_id}"
        )
    await session.delete(task)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise IntegrityErrorException("Database integrity error")
    except Exception:
        await session.rollback()
        raise InternalServerException("Unexpected error while deleting task")
    return {"detail": f"Task with id {task_id} deleted successfully"}


# TODO: добавить функции с фильтрацией.
