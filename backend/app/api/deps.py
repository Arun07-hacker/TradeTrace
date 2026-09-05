import uuid
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login-form",
    auto_error=False
)


async def get_token_from_header(
    oauth_token: Optional[str] = Depends(oauth2_scheme),
    authorization: Optional[str] = Header(None)
) -> Optional[str]:
    """Extract Bearer token from either OAuth2 scheme or Authorization header."""
    if oauth_token:
        return oauth_token
    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ", 1)[1]
    return None


async def get_current_user(
    token: Optional[str] = Depends(get_token_from_header),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Retrieve and validate the currently authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str: str = payload.get("sub")
    if not user_id_str:
        raise credentials_exception

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    stmt = (
        select(User)
        .options(selectinload(User.preference), selectinload(User.portfolio))
        .where(User.id == user_uuid)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verify that current user account is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")
    return current_user
