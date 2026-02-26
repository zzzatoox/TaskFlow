from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import Depends

from typing import Annotated

from backend.app.dependencies import get_async_session
from backend.app.models.tasks import Task as TaskModel


# TODO: посмотреть, можно ли объявить свой тип, чтобы сократить Annotated[AsyncSession, Depends(get_async_session)]


# TODO: сделать пагинацию задач
async def get_all_tasks(session: Annotated[AsyncSession, Depends(get_async_session)]):
    result = await session.scalars(select(TaskModel))
    return result.all()


async def get_task_by_id(
    task_id: int, session: Annotated[AsyncSession, Depends(get_async_session)]
):
    task = session.scalars(select(TaskModel).where(TaskModel.id == task_id)).first()
    return task


async def create_task(
    task_data: dict, session: Annotated[AsyncSession, Depends(get_async_session)]
):
    task = TaskModel(**task_data)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


# TODO: добавить функции с фильтрацией.
