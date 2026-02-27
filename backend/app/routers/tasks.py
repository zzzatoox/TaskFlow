from fastapi import APIRouter

from backend.app.dependencies import SessionDep
from backend.app.services.tasks import get_all_tasks, create_task as create_task_service

router = APIRouter(
    tags=["tasks"],
)


@router.get("/tasks")
async def get_tasks(session: SessionDep):
    tasks = await get_all_tasks(session)
    return tasks


@router.post("/tasks")
async def create_task(task_data: dict, session: SessionDep):
    result = await create_task_service(task_data, session)
    return result
