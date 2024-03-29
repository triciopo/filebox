from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm

from filebox.core.auth import authenticate_user, create_access_token
from filebox.core.config import settings
from filebox.core.database import DBSession
from filebox.schemas.token import Token

auth_router = APIRouter()


@auth_router.post("/token", response_model=Token)
async def access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSession,
) -> dict:
    """Get access token"""
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.API_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=True if settings.ENV != "tests" else False,  # for tests
        samesite="none",
    )
    return {"access_token": access_token, "token_type": "bearer"}
