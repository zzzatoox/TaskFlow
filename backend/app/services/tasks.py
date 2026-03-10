from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import Depends

from typing import Annotated

from backend.app.dependencies import get_async_session
from backend.app.models.tasks import Task as TaskModel

from backend.app.schemas.tasks import TaskCreate, TaskUpdate
from backend.app.services.users import get_user_by_id
from backend.app.utils.custom_exceptions import (
    TaskNotFoundException,
    TaskAccessDeniedException,
    IntegrityErrorException,
    InternalServerException,
)

# TODO: посмотреть, можно ли объявить свой тип, чтобы сократить Annotated[AsyncSession, Depends(get_async_session)]


# TODO: сделать пагинацию задач
async def get_all_tasks(
    user_id: int, session: Annotated[AsyncSession, Depends(get_async_session)]
):
    result = await session.scalars(
        select(TaskModel).where(TaskModel.owner_id == user_id)
    )
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
