from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from typing import Annotated
from backend.app.database import get_async_session

from backend.app.schemas.comments import CommentCreate, CommentUpdate
from backend.app.services.tasks import get_task_by_id

from backend.app.models.comments import Comment as CommentModel
from backend.app.utils.custom_exceptions import (
    CommentNotFoundException,
    IntegrityErrorException,
    InternalServerException,
    CommentAccessDeniedException,
)


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


async def get_comment_by_id(
    comment_id: int, session: Annotated[AsyncEngine, Depends(get_async_session)]
):
    comment = (
        await session.scalars(select(CommentModel).where(CommentModel.id == comment_id))
    ).first()
    if not comment:
        raise CommentNotFoundException(f"Comment with id {comment_id} not found")

    # TODO: нужно ли здесь делать проверку на владельца комментария?

    return comment


async def update_comment(
    task_id: int,
    comment_id: int,
    comment_data: CommentUpdate,
    user_id: int,
    session: Annotated[AsyncEngine, Depends(get_async_session)],
):
    task = await get_task_by_id(task_id, session)
    comment = await get_comment_by_id(comment_id, session)

    for key, value in comment_data.model_dump(exclude_unset=True).items():
        setattr(comment, key, value)

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
    task = await get_task_by_id(task_id, session)
    comment = await get_comment_by_id(comment_id, session)

    if comment.author.id != user_id and task.owner.id != user_id:
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
