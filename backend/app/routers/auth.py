# from backend.app.models.users import User
# from backend.app.schemas.users import User
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from backend.app.schemas.tokens import Token
from typing import Annotated
from datetime import timedelta

from backend.app.config import settings

from backend.app.dependencies import SessionDep

from backend.app.services.auth import authenticate_user, create_access_token
from backend.app.utils.custom_exceptions import UnauthorizedException


router = APIRouter(tags=["auth"])


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise UnauthorizedException()
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Incorrect username or password",
        #     headers={"WWW-Authenticate": "Bearer"},
        # )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
