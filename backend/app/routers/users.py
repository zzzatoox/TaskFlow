from fastapi import APIRouter
from backend.app.schemas.users import UserCreate, UserResponse
from backend.app.dependencies import SessionDep, UserDep
from backend.app.services.users import get_all_users
from backend.app.services.users import get_user_by_id as get_user_by_id_service

from backend.app.services.users import create_user

router = APIRouter(tags=["users"])


@router.post("/users", response_model=UserResponse)
async def register(user_obj: UserCreate, session: SessionDep) -> UserResponse:
    user = await create_user(user_obj, session)
    return user


@router.get("/users/me")
async def get_user_me(user: UserDep):
    return user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, session: SessionDep) -> UserResponse:
    user = await get_user_by_id_service(user_id, session)
    return user


@router.get("/users")
async def get_users(
    session: SessionDep, skip: int = 0, limit: int = 10
) -> list[UserResponse]:
    result = await get_all_users(session, skip, limit)
    return result
