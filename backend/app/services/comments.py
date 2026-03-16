from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine

from typing import Annotated
from backend.app.database import get_async_session

from backend.app.schemas.comments import CommentCreate
from backend.app.services.tasks import get_task_by_id

from backend.app.models.comments import Comment as CommentModel


async def get_comments_by_task(
    task_id: int,
    user_id: int,
    session: Annotated[AsyncEngine, Depends(get_async_session)],
):
    task = await get_task_by_id(task_id, user_id, session)
    return task.comments


async def add_comment_to_task(
    task_id: int,
    user_id: int,
    content: CommentCreate,
    session: Annotated[AsyncEngine, Depends(get_async_session)],
):
    task = await get_task_by_id(task_id, user_id, session)
    comment = CommentModel(comment=content.content, task_id=task_id, author_id=user_id)
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return comment
