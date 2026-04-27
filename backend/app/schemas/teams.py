from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.enums import InviteStatus, UserRole


class SubTeamBase(BaseModel):
    name: str


class SubTeamCreate(SubTeamBase):
    supervisor_id: Optional[int] = None


class SubTeamUpdate(BaseModel):
    name: Optional[str] = None
    supervisor_id: Optional[int] = None


class SubTeamOut(BaseModel):
    id: int
    name: str
    supervisor_id: Optional[int]
    created_at: datetime
    members_count: Optional[int] = None

    model_config = {"from_attributes": True}


class InviteCreate(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.member
    sub_team_id: Optional[int] = None


class InviteOut(BaseModel):
    id: int
    email: str
    role: str
    status: InviteStatus
    invited_by_id: int
    sub_team_id: Optional[int]
    expires_at: datetime
    accepted_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class InviteValidateOut(BaseModel):
    id: int
    email: str
    role: str
    invited_by_name: str
    expires_at: datetime
    valid: bool


class InviteAcceptRequest(BaseModel):
    token: str
    validation_code: str
    username: str
    full_name: str
    password: str


class DirectAddRequest(BaseModel):
    user_id: int
    role: Optional[UserRole] = None
