from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from typing import Annotated
from backend.app.database import get_async_session

from backend.app.schemas.comments import CommentCreate, CommentUpdate
from backend.app.services.tasks import get_task_by_id
from backend.app.models.tasks import Task as TaskModel

from backend.app.models.comments import Comment as CommentModel
from backend.app.utils.custom_exceptions import (
    CommentNotFoundException,
    TaskNotFoundException,
    IntegrityErrorException,
    InternalServerException,
    CommentAccessDeniedException,
)


def _can_access_comment(task: TaskModel, comment: CommentModel, user_id: int) -> bool:
    # TODO: добавить наблюдателей здесь, когда появятся
    return (
        comment.user_id == user_id
        or task.owner_id == user_id
        or task.executor_id == user_id
    )


async def _get_task_or_404(
    task_id: int,
    session: Annotated[AsyncEngine, Depends(get_async_session)],
) -> TaskModel:
    task = (
        await session.scalars(select(TaskModel).where(TaskModel.id == task_id))
    ).first()
    if not task:
        raise TaskNotFoundException(f"Task with id {task_id} not found")
    return task


async def _get_task_comment_or_404(
    task_id: int,
    comment_id: int,
    session: Annotated[AsyncEngine, Depends(get_async_session)],
) -> CommentModel:
    comment = (
        await session.scalars(
            select(CommentModel).where(
                CommentModel.id == comment_id,
                CommentModel.task_id == task_id,
            )
        )
    ).first()
    if not comment:
        raise CommentNotFoundException(
            f"Comment with id {comment_id} for task with id {task_id} not found"
        )
    return comment


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
    await get_task_by_id(task_id, user_id, session)
    comment = CommentModel(content=content.content, task_id=task_id, user_id=user_id)
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return comment


async def get_comment_by_id(
    task_id: int,
    comment_id: int,
    user_id: int,
    session: Annotated[AsyncEngine, Depends(get_async_session)],
):
    task = await _get_task_or_404(task_id, session)
    comment = await _get_task_comment_or_404(task_id, comment_id, session)

    if not _can_access_comment(task, comment, user_id):
        raise CommentAccessDeniedException(
            f"User with id {user_id} does not have permission to access comment with id {comment_id}"
        )

    return comment


async def update_comment(
    task_id: int,
    comment_id: int,
    comment_data: CommentUpdate,
    user_id: int,
    session: Annotated[AsyncEngine, Depends(get_async_session)],
):
    task = await _get_task_or_404(task_id, session)
    comment = await _get_task_comment_or_404(task_id, comment_id, session)

    if not _can_access_comment(task, comment, user_id):
        raise CommentAccessDeniedException(
            f"User with id {user_id} does not have permission to update comment with id {comment_id}"
        )

    payload = comment_data.model_dump(exclude_unset=True)
    if "content" in payload:
        comment.content = payload["content"]

    try:
        await session.commit()
        await session.refresh(comment)
    except IntegrityError:
        await session.rollback()
        raise IntegrityErrorException("Database integrity error")
    except Exception:
        await session.rollback()
        raise InternalServerException("Unexpected error while updating comment")
    return comment


async def delete_comment(
    task_id: int,
    comment_id: int,
    user_id: int,
    session: Annotated[AsyncEngine, Depends(get_async_session)],
):
    task = await _get_task_or_404(task_id, session)
    comment = await _get_task_comment_or_404(task_id, comment_id, session)

    if not _can_access_comment(task, comment, user_id):
        raise CommentAccessDeniedException(
            f"User with id {user_id} does not have permission to delete comment with id {comment_id}"
        )

    await session.delete(comment)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise IntegrityErrorException("Database integrity error")
    except Exception:
        await session.rollback()
        raise InternalServerException("Unexpected error while deleting comment")
    return {"detail": f"Comment with id {comment_id} deleted successfully"}
