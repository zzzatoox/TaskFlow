from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from ..schemas.users import User as UserSchema, UserOutput
from ..models.users import User as UserModel
from sqlalchemy import select
from ..dependencies import SessionDep, UserDep
from backend.app.utils.password_hashing import (
    get_password_hash_async,
    verify_password_async,
)
from backend.app.services.users import get_all_users
from backend.app.services.users import get_user_by_id as get_user_by_id_service

router = APIRouter(tags=["users"])


@router.post("/users", response_model=None)
async def register(user_obj: UserSchema, session: SessionDep) -> Response:
    password = user_obj.password.get_secret_value()
    password_hash = await get_password_hash_async(password)

    # TODO: проверить , можно ли будет сделать просто UserModal(**user_obj)
    # запишется ли patronymic как None, если его нет в user_obj
    user = UserModel(
        email=user_obj.email,
        login=user_obj.login,
        password_hash=password_hash,
        last_name=user_obj.last_name,
        first_name=user_obj.first_name,
        patronymic=user_obj.patronymic if user_obj.patronymic else None,
    )
    session.add(user)
    await session.commit()

    return JSONResponse(content={"message": "Success registration"})


@router.get("/users/me")
async def get_user_me(user: UserDep):
    return user


@router.get("/users/{user_id}", response_model=UserOutput)
async def get_user_by_id(user_id: int, session: SessionDep) -> UserOutput | Response:
    user = await get_user_by_id_service(user_id, session)
    if not user:
        return JSONResponse(content={"message": "User not found"}, status_code=404)
    return user


@router.get("/users")
async def get_users(session: SessionDep) -> list[UserOutput]:
    result = await get_all_users(session)
    return result
