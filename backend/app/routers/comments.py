from fastapi import APIRouter

from backend.app.dependencies import SessionDep, UserDep

from backend.app.schemas.comments import CommentCreate
from backend.app.services.comments import get_comments_by_task, add_comment_to_task

router = APIRouter(tags=["comments"])


@router.get("tasks/{task_id}/comments")
async def get_comments(task_id: int, user: UserDep, session: SessionDep):
    comments = await get_comments_by_task(task_id, user.id, session)
    return comments


@router.post("tasks/{task_id}/comments")
async def add_comment(
    task_id: int, content: CommentCreate, user: UserDep, session: SessionDep
):
    comment = await add_comment_to_task(task_id, user.id, content, session)
    return comment
