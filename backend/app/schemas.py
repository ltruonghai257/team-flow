from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from app.models import MilestoneStatus, TaskPriority, TaskStatus


# ── Auth ──────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ── User ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str
    role: str = "member"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: str
    avatar_url: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Project ───────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#6366f1"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    color: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Milestone ─────────────────────────────────────────────────────────────────

class MilestoneCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: MilestoneStatus = MilestoneStatus.planned
    start_date: Optional[datetime] = None
    due_date: datetime
    project_id: int


class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[MilestoneStatus] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class MilestoneOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: MilestoneStatus
    start_date: Optional[datetime]
    due_date: datetime
    completed_at: Optional[datetime]
    project_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Task ──────────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    tags: Optional[str] = None
    project_id: Optional[int] = None
    milestone_id: Optional[int] = None
    assignee_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    tags: Optional[str] = None
    project_id: Optional[int] = None
    milestone_id: Optional[int] = None
    assignee_id: Optional[int] = None
    completed_at: Optional[datetime] = None


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_hours: Optional[int]
    tags: Optional[str]
    project_id: Optional[int]
    milestone_id: Optional[int]
    assignee_id: Optional[int]
    creator_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    assignee: Optional[UserOut] = None

    model_config = {"from_attributes": True}


# ── Schedule ──────────────────────────────────────────────────────────────────

class ScheduleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    all_day: bool = False
    color: str = "#6366f1"
    location: Optional[str] = None
    recurrence: Optional[str] = None
    task_id: Optional[int] = None


class ScheduleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    all_day: Optional[bool] = None
    color: Optional[str] = None
    location: Optional[str] = None
    recurrence: Optional[str] = None
    task_id: Optional[int] = None


class ScheduleOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    all_day: bool
    color: str
    location: Optional[str]
    recurrence: Optional[str]
    user_id: int
    task_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── AI ────────────────────────────────────────────────────────────────────────

class AIMessageCreate(BaseModel):
    content: str
    conversation_id: Optional[int] = None


class AIMessageOut(BaseModel):
    id: int
    role: str
    content: str
    model: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AIConversationOut(BaseModel):
    id: int
    title: Optional[str]
    user_id: int
    created_at: datetime
    updated_at: datetime
    messages: List[AIMessageOut] = []

    model_config = {"from_attributes": True}


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_tasks: int
    todo_tasks: int
    in_progress_tasks: int
    done_tasks: int
    overdue_tasks: int
    total_team_members: int
    upcoming_milestones: List[MilestoneOut]
    recent_tasks: List[TaskOut]
