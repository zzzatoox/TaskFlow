import jwt
from jwt import InvalidTokenError

from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_async_session
from backend.app.models.users import User
from backend.app.schemas.tokens import TokenData
from backend.app.schemas.users import UserInDB

from sqlalchemy import select

from typing import Annotated

from fastapi import Depends, HTTPException, status
from backend.app.security import oauth2_scheme

from backend.app.config import settings


async def get_user(
    login: str, session: Annotated[AsyncSession, Depends(get_async_session)]
) -> UserInDB | None:
    user = (await session.scalars(select(User).where(User.login == login))).first()
    return UserInDB(**user.__dict__) if user else None


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserInDB | HTTPException:
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
    return user
