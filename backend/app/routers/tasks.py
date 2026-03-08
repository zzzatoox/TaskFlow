from fastapi import APIRouter, HTTPException

from backend.app.dependencies import SessionDep, UserDep
from backend.app.schemas.tasks import TaskCreate, TaskUpdate
from backend.app.services.tasks import (
    get_all_tasks,
    create_task as create_task_service,
    get_task_by_id,
    update_task as update_task_service,
    delete_task as delete_task_service,
)

router = APIRouter(
    tags=["tasks"],
)

# TODO: сделать ручки доступные только после авторизации


@router.get("/tasks")
async def get_tasks(user: UserDep, session: SessionDep):
    tasks = await get_all_tasks(user.id, session)
    return tasks


@router.post("/tasks")
async def create_task(task_data: TaskCreate, user: UserDep, session: SessionDep):
    result = await create_task_service(task_data, user.id, session)
    return result


@router.get("/tasks/{task_id}")
async def get_task(task_id: int, user: UserDep, session: SessionDep):
    task = await get_task_by_id(task_id, user.id, session)
    return task


@router.put("/tasks/{task_id}")
async def update_task(
    task_id: int, task_data: TaskUpdate, user: UserDep, session: SessionDep
):
    task = await update_task_service(task_id, task_data, user.id, session)
    return task


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, user: UserDep, session: SessionDep):
    result = await delete_task_service(task_id, user.id, session)
    return result
