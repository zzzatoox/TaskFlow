from fastapi import APIRouter

from backend.app.dependencies import SessionDep, UserDep

from backend.app.schemas.comments import CommentCreate, CommentUpdate
from backend.app.services.comments import (
    get_comments_by_task,
    add_comment_to_task,
    update_comment as update_comment_service,
    delete_comment as delete_comment_service,
)

router = APIRouter(tags=["comments"])


@router.get("/tasks/{task_id}/comments")
async def get_comments(task_id: int, user: UserDep, session: SessionDep):
    comments = await get_comments_by_task(task_id, user.id, session)
    return comments


@router.post("/tasks/{task_id}/comments")
async def add_comment(
    task_id: int, content: CommentCreate, user: UserDep, session: SessionDep
):
    comment = await add_comment_to_task(task_id, user.id, content, session)
    return comment


@router.put("/tasks/{task_id}/comments/{comment_id}")
async def update_comment(
    task_id: int,
    comment_id: int,
    comment_obj: CommentUpdate,
    user: UserDep,
    session: SessionDep,
):
    comment = await update_comment_service(
        task_id, comment_id, comment_obj, user.id, session
    )
    return comment


@router.delete("/tasks/{task_id}/comments/{comment_id}")
async def delete_comment(
    task_id: int, comment_id: int, user: UserDep, session: SessionDep
):
    await delete_comment_service(task_id, comment_id, user.id, session)
    return {"detail": "Comment deleted successfully"}
