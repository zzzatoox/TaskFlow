from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from ..schemas.users import UserIn, UserOutput
from ..models.users import User
from sqlalchemy import select
from ..dependecies import SessionDep


router = APIRouter(tags=["users"])


@router.post("/users", response_model=UserOutput)
async def register(user_obj: UserIn, session: SessionDep) -> Response:
    user = User(
        email=user_obj.email,
        login=user_obj.login,
        password=user_obj.password.get_secret_value(),
        last_name=user_obj.last_name,
        first_name=user_obj.first_name,
        patronymic=user_obj.patronymic if user_obj.patronymic else None,
    )
    session.add(user)
    await session.commit()

    return JSONResponse(content={"message": "Success registration"})


# @router.get("/users/me")
# async def get_user_me():
#     pass


@router.get("/users/{user_id}", response_model=UserOutput)
async def get_user_by_id(user_id: int, session: SessionDep) -> UserOutput | Response:
    user = (await session.scalars(select(User).where(User.id == user_id))).first()
    if not user:
        return JSONResponse(content={"message": "User not found"}, status_code=404)
    return user


@router.get("/users")
async def get_users(session: SessionDep) -> list[UserOutput]:
    result = await session.scalars(select(User))
    return result.all()
