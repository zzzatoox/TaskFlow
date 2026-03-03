from asyncpg import InternalServerError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import Depends

from typing import Annotated

from backend.app.dependencies import get_async_session
from backend.app.models.tasks import Task as TaskModel

from backend.app.schemas.tasks import TaskCreate, TaskUpdate
from backend.app.services.statuses import get_status_by_id
from backend.app.utils.custom_exceptions import TaskNotFoundException

# TODO: посмотреть, можно ли объявить свой тип, чтобы сократить Annotated[AsyncSession, Depends(get_async_session)]


# TODO: сделать пагинацию задач
async def get_all_tasks(session: Annotated[AsyncSession, Depends(get_async_session)]):
    result = await session.scalars(select(TaskModel))
    return result.all()


async def get_task_by_id(
    task_id: int, session: Annotated[AsyncSession, Depends(get_async_session)]
):
    task = (
        await session.scalars(select(TaskModel).where(TaskModel.id == task_id))
    ).first()
    if not task:
        raise TaskNotFoundException(f"Task with id {task_id} not found")
    return task


async def create_task(
    task_data: TaskCreate, session: Annotated[AsyncSession, Depends(get_async_session)]
):
    task = TaskModel(**task_data.model_dump())
    session.add(task)
    try:
        await session.commit()
        await session.refresh(task)
    except Exception:
        await session.rollback()
        raise InternalServerError("Unexpected error while creating task")
    return task


# TODO: нужна ли, если есть функция update_task?
async def assign_executor_to_task(
    task_id: int,
    executor_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    task = await get_task_by_id(task_id, session)
    task.executor_id = executor_id
    try:
        await session.commit()
        await session.refresh(task)
    except Exception:
        await session.rollback()
        raise InternalServerError("Unexpected error while assigning executor to task")
    return task


# TODO: нужна ли, если есть функция update_task?
async def change_task_status(
    task_id: int,
    new_status_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    task = await get_task_by_id(task_id, session)
    task.status_id = new_status_id
    try:
        await session.commit()
        await session.refresh(task)
    except Exception:
        await session.rollback()
        raise InternalServerError("Unexpected error while changing task status")
    return task


async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    task = await get_task_by_id(task_id, session)
    for key, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    try:
        await session.commit()
        await session.refresh(task)
    except Exception:
        await session.rollback()
        raise InternalServerError("Unexpected error while updating task")
    return task


async def delete_task(
    task_id: int, session: Annotated[AsyncSession, Depends(get_async_session)]
):
    task = await get_task_by_id(task_id, session)
    if not task:
        raise TaskNotFoundException(f"Task with id {task_id} not found")
    await session.delete(task)
    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise InternalServerError("Unexpected error while deleting task")
    return {"detail": f"Task with id {task_id} deleted successfully"}


# TODO: добавить функции с фильтрацией.
