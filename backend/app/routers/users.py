from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from schemas.users import UserIn, UserOutput


users = [
    {
        "id": 1,
        "email": "zzzatoox@mail.ru",
        "login": "zzzatoox",
        "password": "guzeevaTop123",
        "last_name": "Лазарев",
        "first_name": "Никита",
        "patronymic": None,
    }
]


USER_INT = 2

router = APIRouter()


@router.post("/users/", response_model=UserOutput)
async def register(user_obj: UserIn) -> Response:
    global USER_INT
    user = user_obj.model_dump()
    user["id"] = USER_INT
    USER_INT += 1
    users.append(user)

    return JSONResponse(content={"message": "Success registration"})


@router.get("/users/me")
async def get_user_me():
    pass


@router.get("/users/{user_id}", response_model=UserOutput)
async def get_user_by_id(user_id: int) -> UserOutput | Response:
    for user in users:
        if user.get("id") == user_id:
            return user
    return JSONResponse(status_code=404, content={"message": "User not found"})


@router.get("/users")
async def get_users() -> list[UserOutput]:
    return users
