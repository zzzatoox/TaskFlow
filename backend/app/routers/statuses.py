from fastapi import APIRouter
from backend.app.dependencies import SessionDep
from backend.app.schemas.statuses import StatusUpdate, StatusCreate
from backend.app.services.statuses import (
    add_status,
    get_all_statuses,
    get_status_by_id,
    update_status as update_status_service,
    delete_status as delete_status_service,
)


router = APIRouter(
    tags=["statuses"],
)


@router.get("/statuses")
async def get_statuses(session: SessionDep):
    statuses = await get_all_statuses(session)
    return statuses


@router.get("/statuses/{status_id}")
async def get_status(status_id: int, session: SessionDep):
    status = await get_status_by_id(status_id, session)
    return status


@router.post("/statuses")
async def create_status(status_obj: StatusCreate, session: SessionDep):
    status = await add_status(status_obj, session)
    return status


@router.put("/statuses/{status_id}")
async def update_status(status_id: int, status_obj: StatusUpdate, session: SessionDep):
    status = await update_status_service(status_id, status_obj, session)
    return status


@router.delete("/statuses/{status_id}")
async def delete_status(status_id: int, session: SessionDep):
    await delete_status_service(status_id, session)
    return {"detail": "Status deleted successfully"}
