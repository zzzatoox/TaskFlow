from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.users import get_current_user
from .database import get_async_session
from backend.app.schemas.users import UserResponse

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
UserDep = Annotated[UserResponse, Depends(get_current_user)]
