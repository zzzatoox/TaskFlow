from datetime import datetime, timedelta, timezone

import jwt

from backend.app.dependencies import SessionDep
from backend.app.schemas.users import UserInDB

from backend.app.services.users import get_user
from backend.app.utils.password_hashing import verify_password_async, DUMMY_HASH

from backend.app.config import settings


async def authenticate_user(
    login: str, password: str, session: SessionDep
) -> UserInDB | bool:
    user = await get_user(login, session)
    if not user:
        await verify_password_async(password, DUMMY_HASH)
        return False
    if not await verify_password_async(password, user.password_hash):
        return False
    return user


async def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
