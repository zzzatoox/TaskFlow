from fastapi import APIRouter

from backend.app.dependencies import SessionDep

from backend.app.services.

router = APIRouter(tags=["comments"])

@router.get("tasks/{}/comments")
async def get_comments(session: SessionDep):
    comments = get_comments_by_task()