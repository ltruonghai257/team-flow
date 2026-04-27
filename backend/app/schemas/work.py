from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, field_validator

from app.models.enums import (
    MilestoneStatus,
    SprintStatus,
    StatusSetScope,
    TaskPriority,
    TaskStatus,
    TaskType,
)
from app.schemas.users import UserOut


def _to_naive_utc(v):
    """Convert tz-aware datetime to naive UTC; pass through naive datetimes and None."""
    if isinstance(v, datetime) and v.tzinfo is not None:
        return v.astimezone(timezone.utc).replace(tzinfo=None)
    return v


# ── Project ───────────────────────────────────────────────────────────────────


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#6366f1"
    sub_team_id: Optional[int] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    sub_team_id: Optional[int] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    color: str
    sub_team_id: Optional[int]
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

    _normalize_dates = field_validator("start_date", "due_date", mode="after")(
        _to_naive_utc
    )


class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[MilestoneStatus] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    _normalize_dates = field_validator(
        "start_date", "due_date", "completed_at", mode="after"
    )(_to_naive_utc)


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


# ── Sprint ────────────────────────────────────────────────────────────────────


class SprintBase(BaseModel):
    name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: SprintStatus
    milestone_id: int


class SprintCreate(SprintBase):
    _normalize_dates = field_validator("start_date", "end_date", mode="after")(_to_naive_utc)


class SprintUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[SprintStatus] = None
    milestone_id: Optional[int] = None

    _normalize_dates = field_validator("start_date", "end_date", mode="after")(_to_naive_utc)


class SprintOut(SprintBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SprintClosePayload(BaseModel):
    task_mapping: Dict[int, Optional[int]]


# ── Status Sets ───────────────────────────────────────────────────────────────


class CustomStatusOut(BaseModel):
    id: int
    status_set_id: int
    name: str
    slug: str
    color: str
    position: int
    is_done: bool
    is_archived: bool
    legacy_status: Optional[TaskStatus]
    task_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StatusSetOut(BaseModel):
    id: int
    scope: StatusSetScope
    sub_team_id: Optional[int]
    project_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    statuses: List[CustomStatusOut] = []

    model_config = {"from_attributes": True}


class StatusTransitionOut(BaseModel):
    id: int
    status_set_id: int
    from_status_id: int
    to_status_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class StatusTransitionPair(BaseModel):
    from_status_id: int
    to_status_id: int


class StatusTransitionsReplace(BaseModel):
    transitions: List[StatusTransitionPair]


class BlockedStatusTransitionDetail(BaseModel):
    code: str
    message: str
    status_set_id: int
    current_status_id: int
    current_status_name: str
    target_status_id: int
    target_status_name: str
    allowed_status_ids: List[int]


class CustomStatusCreate(BaseModel):
    name: str
    color: str = "#64748b"
    is_done: bool = False
    position: Optional[int] = None


class CustomStatusUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    is_done: Optional[bool] = None
    is_archived: Optional[bool] = None


class StatusReorderPayload(BaseModel):
    status_ids: List[int]


class StatusDeletePayload(BaseModel):
    mode: str
    replacement_status_id: Optional[int] = None


class ProjectStatusRevertPayload(BaseModel):
    fallback_mappings: Dict[int, int] = {}


# ── Task ──────────────────────────────────────────────────────────────────────


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    priority: TaskPriority = TaskPriority.medium
    type: TaskType = TaskType.task
    due_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    tags: Optional[str] = None
    project_id: Optional[int] = None
    milestone_id: Optional[int] = None
    sprint_id: Optional[int] = None
    assignee_id: Optional[int] = None
    custom_status_id: Optional[int] = None

    _normalize_due = field_validator("due_date", mode="after")(_to_naive_utc)


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    type: Optional[TaskType] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    tags: Optional[str] = None
    project_id: Optional[int] = None
    milestone_id: Optional[int] = None
    sprint_id: Optional[int] = None
    assignee_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    custom_status_id: Optional[int] = None

    _normalize_due = field_validator("due_date", "completed_at", mode="after")(
        _to_naive_utc
    )


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    type: TaskType
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_hours: Optional[int]
    tags: Optional[str]
    project_id: Optional[int]
    milestone_id: Optional[int]
    sprint_id: Optional[int]
    assignee_id: Optional[int]
    creator_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    assignee: Optional[UserOut] = None
    custom_status_id: Optional[int] = None
    custom_status: Optional[CustomStatusOut] = None

    model_config = {"from_attributes": True}


class AiParseRequest(BaseModel):
    input: str
    mode: str  # "nlp" | "json"
    model: Optional[str] = None


class AiParseResponse(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    type: Optional[TaskType] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[int] = None
    tags: Optional[str] = None
    assignee_name: Optional[str] = None

    _normalize_due = field_validator("due_date", mode="after")(_to_naive_utc)


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

    _normalize_times = field_validator("start_time", "end_time", mode="after")(
        _to_naive_utc
    )


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

    _normalize_times = field_validator("start_time", "end_time", mode="after")(
        _to_naive_utc
    )


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


# ── Timeline ──────────────────────────────────────────────────────────────────


class TimelineTaskOut(BaseModel):
    id: int
    title: str
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime]
    created_at: datetime
    milestone_id: Optional[int]
    project_id: Optional[int]
    assignee_id: Optional[int]
    assignee: Optional[UserOut] = None

    model_config = {"from_attributes": True}


class TimelineMilestoneOut(BaseModel):
    id: int
    title: str
    status: MilestoneStatus
    start_date: Optional[datetime]
    due_date: datetime
    tasks: List[TimelineTaskOut] = []

    model_config = {"from_attributes": True}


class TimelineProjectOut(BaseModel):
    id: int
    name: str
    color: str
    milestones: List[TimelineMilestoneOut] = []
    unassigned_tasks: List[TimelineTaskOut] = []

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
