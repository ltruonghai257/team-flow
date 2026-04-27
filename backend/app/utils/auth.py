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


async def require_supervisor(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in (UserRole.admin, UserRole.supervisor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supervisor or admin access required",
        )
    return current_user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


async def require_supervisor_or_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role not in (UserRole.admin, UserRole.supervisor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supervisor or admin access required",
        )
    return current_user


async def get_sub_team(
    current_user: User = Depends(get_current_user),
    x_sub_team_id: Optional[int] = Header(None, alias="X-SubTeam-ID"),
    db: AsyncSession = Depends(get_db),
) -> Optional[SubTeam]:
    """Inject sub-team context: implicit for member/supervisor, explicit for admin."""
    if current_user.role == UserRole.member:
        # Members have exactly one sub-team
        result = await db.execute(
            select(SubTeam).where(SubTeam.id == current_user.sub_team_id)
        )
        return result.scalar_one_or_none()
    elif current_user.role == UserRole.supervisor:
        # Supervisors see their assigned sub-team
        result = await db.execute(
            select(SubTeam).where(SubTeam.supervisor_id == current_user.id)
        )
        return result.scalars().first()
    elif current_user.role == UserRole.admin:
        # Admins use X-SubTeam-ID header (from global switcher)
        if x_sub_team_id is None:
            return None  # Admin sees all data when no filter
        result = await db.execute(select(SubTeam).where(SubTeam.id == x_sub_team_id))
        sub_team = result.scalar_one_or_none()
        if not sub_team:
            raise HTTPException(status_code=403, detail="Invalid sub-team")
        return sub_team
    return None


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
