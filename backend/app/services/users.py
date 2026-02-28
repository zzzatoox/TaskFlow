import jwt
from jwt import InvalidTokenError

from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_async_session
from backend.app.models.users import User as UserModel
from backend.app.schemas.tokens import TokenData
from backend.app.schemas.users import UserCreate, UserResponse

from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from backend.app.utils.custom_exceptions import (
    IntegrityErrorException,
    UserAlreadyExistsException,
    InternalServerException,
    UserNotFoundException,
)
from backend.app.utils.password_hashing import get_password_hash_async

from sqlalchemy import select

from typing import Annotated

from fastapi import Depends
from backend.app.security import oauth2_scheme

from backend.app.config import settings


async def get_user(
    login: str, session: Annotated[AsyncSession, Depends(get_async_session)]
) -> UserModel | None:
    user = (
        await session.scalars(select(UserModel).where(UserModel.login == login))
    ).first()
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserResponse | HTTPException:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        login = payload.get("sub")
        if login is None:
            raise credentials_exception
        token_data = TokenData(username=login)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(token_data.username, session)
    if user is None:
        raise credentials_exception
    return UserResponse(**user.__dict__)


async def get_all_users(session: Annotated[AsyncSession, Depends(get_async_session)]):
    result = await session.scalars(select(UserModel))
    if not result:
        raise UserNotFoundException("No users found")
    return result.all()


async def get_user_by_id(
    user_id: int, session: Annotated[AsyncSession, Depends(get_async_session)]
):
    user = (
        await session.scalars(select(UserModel).where(UserModel.id == user_id))
    ).first()
    if not user:
        raise UserNotFoundException("User not found")
    return user


async def create_user(
    user_obj: UserCreate, session: Annotated[AsyncSession, Depends(get_async_session)]
):
    password = user_obj.password.get_secret_value()
    password_hash = await get_password_hash_async(password)
    user_data = user_obj.model_dump(exclude={"password", "password_confirm"})

    existing = await session.execute(
        select(UserModel).where(UserModel.email == user_data["email"])
    )
    if existing.scalar_one_or_none():
        raise UserAlreadyExistsException("User with this email already exists")

    existing = await session.execute(
        select(UserModel).where(UserModel.login == user_data["login"])
    )
    if existing.scalar_one_or_none():
        raise UserAlreadyExistsException("User with this login already exists")

    user = UserModel(**user_data, password_hash=password_hash)
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
    except IntegrityError:
        await session.rollback()
        raise IntegrityErrorException("Database integrity error")
    except Exception:
        await session.rollback()
        raise InternalServerException("Unexpected error while creating user")
    return user
