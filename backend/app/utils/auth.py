from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import get_db
from app.models import SubTeam, User, UserRole
from app.schemas import TokenData
from app.services.visibility import (
    is_leader,
    is_manager,
    resolve_visible_sub_team,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc).replace(tzinfo=None) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
    request: Request,
    bearer_token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = request.cookies.get("access_token") or bearer_token
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == token_data.user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


async def require_manager(current_user: User = Depends(get_current_user)) -> User:
    if not is_manager(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required",
        )
    return current_user


async def require_leader_or_manager(
    current_user: User = Depends(get_current_user),
) -> User:
    if not (is_manager(current_user) or is_leader(current_user)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Leader or manager access required",
        )
    return current_user


async def require_leader(
    current_user: User = Depends(get_current_user),
) -> User:
    if not is_leader(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Leader access required",
        )
    return current_user


require_supervisor = require_leader_or_manager
require_admin = require_manager
require_supervisor_or_admin = require_leader_or_manager


async def get_sub_team(
    current_user: User = Depends(get_current_user),
    x_sub_team_id: Optional[int] = Header(None, alias="X-SubTeam-ID"),
    db: AsyncSession = Depends(get_db),
) -> Optional[SubTeam]:
    """Inject Phase 29 sub-team context for scoped route dependencies."""
    return await resolve_visible_sub_team(
        db, current_user, requested_sub_team_id=x_sub_team_id
    )


async def get_user_from_cookie(
    token: Optional[str], db: AsyncSession
) -> Optional[User]:
    """Validate the access_token cookie and return the User, or None if invalid.

    Used by the WebSocket endpoint where the standard FastAPI Depends-based flow
    doesn't apply during the handshake.
    """
    if not token:
        return None
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        return None
    return user
