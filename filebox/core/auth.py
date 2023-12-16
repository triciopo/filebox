import datetime
from typing import Annotated, Union, Optional, Dict

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from jose import JWTError, jwt
from passlib.context import CryptContext

from filebox.core.config import settings
from filebox.core.database import DBSession
from filebox.models.user import User
from filebox.schemas.token import TokenData
from filebox.services import users as service

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("access_token")

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl=f"{settings.API_PREFIX}/token")


def create_access_token(
    data: dict,
    expires_delta: Union[datetime.timedelta, None] = None,
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.API_SECRET_KEY, algorithm=settings.API_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DBSession,
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.API_SECRET_KEY, algorithms=[settings.API_ALGORITHM]
        )
        username: str = str(payload.get("sub"))
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await service.get_user_by_name(db, username=str(token_data.username))
    if user is None:
        raise credentials_exception
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def authenticate_user(
    username: str,
    password: str,
    db: DBSession,
):
    user = await service.get_user_by_name(db, username)
    if not user:
        return False
    if not verify_password(password, str(user.hashed_password)):
        return False
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)
