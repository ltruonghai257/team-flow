from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.enums import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str
    role: str = "member"
    sub_team_id: Optional[int] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[str] = None
    sub_team_id: Optional[int] = None


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: str
    avatar_url: Optional[str]
    is_active: bool
    sub_team_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}
