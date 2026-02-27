from fastapi import APIRouter
from backend.app.dependencies import SessionDep

from backend.app.schemas.priorities import PriorityCreate
from backend.app.services.priorities import (
    add_priority,
    get_all_priorities,
    get_priority_by_id,
)


router = APIRouter(
    tags=["priorities"],
)


@router.get("/priorities")
async def get_priorities(session: SessionDep):
    priorities = await get_all_priorities(session)
    return priorities


@router.get("/priorities/{priority_id}")
async def get_priority(priority_id: int, session: SessionDep):
    priority = await get_priority_by_id(priority_id, session)
    return priority


@router.post("/priorities")
async def create_priority(priority_obj: PriorityCreate, session: SessionDep):
    priority = await add_priority(priority_obj, session)
    return priority
