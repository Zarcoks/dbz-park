"""Who is calling: `CurrentUser` (logged in) and `StaffUser` (console).

Both refuse with the same message, so a logged-in visitor hitting a staff route is
treated exactly like someone with no token at all.
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db import SessionDep
from app.errors import NOT_AUTHENTICATED, NOT_STAFF, ApiError
from app.models import User
from app.security import read_token

# auto_error=False: otherwise FastAPI answers 403 itself, outside the contract.
bearer_scheme = HTTPBearer(auto_error=False)
BearerDep = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]


async def get_current_user(session: SessionDep, credentials: BearerDep) -> User:
    if credentials is None:
        raise ApiError(NOT_AUTHENTICATED)

    user_id = read_token(credentials.credentials)
    if user_id is None:
        raise ApiError(NOT_AUTHENTICATED)

    user = await session.get(User, user_id)
    if user is None:
        # Valid token, account deleted since.
        raise ApiError(NOT_AUTHENTICATED)
    return user


async def get_staff_user(user: Annotated[User, Depends(get_current_user)]) -> User:
    if not user.is_staff:
        raise ApiError(NOT_STAFF)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
StaffUser = Annotated[User, Depends(get_staff_user)]
