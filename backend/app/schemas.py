from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.models import (
    InviteStatus,
    MilestoneStatus,
    NotificationEventType,
    NotificationStatus,
    SprintStatus,
    StatusSetScope,
    TaskPriority,
    TaskStatus,
    TaskType,
    UserRole,
)


def _to_naive_utc(v):
    """Convert tz-aware datetime to naive UTC; pass through naive datetimes and None."""
    if isinstance(v, datetime) and v.tzinfo is not None:
        return v.astimezone(timezone.utc).replace(tzinfo=None)
    return v


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


# ── Notifications ─────────────────────────────────────────────────────────────


class NotificationCreate(BaseModel):
    event_type: NotificationEventType
    event_ref_id: int
    offset_minutes: int  # how many minutes before event to fire


class NotificationBulkCreate(BaseModel):
    event_type: NotificationEventType
    event_ref_id: int
    offset_minutes_list: List[int]  # replace any existing reminders with this set


class NotificationOut(BaseModel):
    id: int
    user_id: int
    event_type: NotificationEventType
    event_ref_id: int
    title_cache: str
    start_at_cache: datetime
    remind_at: datetime
    offset_minutes: int
    status: NotificationStatus
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Chat ──────────────────────────────────────────────────────────────────────


class ChatChannelOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageOut(BaseModel):
    id: int
    sender_id: int
    sender_name: Optional[str] = None
    channel_id: Optional[int]
    conversation_id: Optional[int]
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatConversationOut(BaseModel):
    id: int
    other_user_id: int
    other_user_name: Optional[str] = None
    last_message: Optional[str] = None
    last_message_at: datetime

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


# ── Performance ───────────────────────────────────────────────────────────────


class TrendDataPoint(BaseModel):
    date: str  # YYYY-MM-DD
    completed_count: int


class TeamMemberPerformance(BaseModel):
    user_id: int
    full_name: str
    avatar_url: Optional[str] = None
    active_tasks: int
    completed_30d: int
    avg_cycle_time: Optional[float] = None  # Hours
    on_time_rate: Optional[float] = None  # Percentage
    collaboration_score: int  # Message count
    status: str  # "green", "yellow", "red"

    model_config = {"from_attributes": True}


class PerformanceDashboard(BaseModel):
    team_metrics: List[TeamMemberPerformance]
    overall_on_time_rate: float
    total_active_tasks: int


class UserPerformanceDetail(BaseModel):
    user_id: int
    full_name: str
    metrics: TeamMemberPerformance
    trend_data: List[TrendDataPoint]
    recent_completed_tasks: List[TaskOut]


# ── AI Breakdown ──────────────────────────────────────────────────────────────


class AiBreakdownRequest(BaseModel):
    description: str
    project_id: int


class AiBreakdownSubtask(BaseModel):
    title: str
    priority: str
    type: TaskType = TaskType.task
    estimated_hours: int
    description: str


class AiBreakdownResponse(BaseModel):
    subtasks: List[AiBreakdownSubtask]


# ── Project Summary ───────────────────────────────────────────────────────────


class ProjectSummaryRequest(BaseModel):
    project_id: int


class ProjectSummarySections(BaseModel):
    milestone_progress: str
    recent_completions: str
    overdue: str
    at_risk: str


class ProjectSummaryResponse(BaseModel):
    summary: str
    sections: ProjectSummarySections


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


# ── SubTeam ────────────────────────────────────────────────────────────────────


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


# ── Invites ───────────────────────────────────────────────────────────────────


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


# ── KPI Dashboard ──────────────────────────────────────────────────────────────


class KPIWeightSettingsOut(BaseModel):
    id: int
    sub_team_id: Optional[int]
    workload_weight: int
    velocity_weight: int
    cycle_time_weight: int
    on_time_weight: int
    defect_weight: int
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class KPIWeightSettingsUpdate(BaseModel):
    workload_weight: Optional[int] = None
    velocity_weight: Optional[int] = None
    cycle_time_weight: Optional[int] = None
    on_time_weight: Optional[int] = None
    defect_weight: Optional[int] = None

    @field_validator("defect_weight", mode="before")
    @classmethod
    def validate_total(cls, v, info):
        return v

    def validate_sum(self) -> None:
        fields = [
            self.workload_weight,
            self.velocity_weight,
            self.cycle_time_weight,
            self.on_time_weight,
            self.defect_weight,
        ]
        if all(f is not None for f in fields):
            total = sum(fields)
            if total != 100:
                raise ValueError("Total weight must equal 100")


class KPIFilterOptions(BaseModel):
    sprints: List[Dict] = []
    projects: List[Dict] = []
    members: List[Dict] = []
    task_types: List[str] = []


class KPIReason(BaseModel):
    label: str
    severity: str


class KPIScoreBreakdown(BaseModel):
    workload: int
    velocity: int
    cycle_time: int
    on_time: int
    defects: int


class KPIMemberScorecard(BaseModel):
    user_id: int
    full_name: str
    avatar_url: Optional[str]
    kpi_score: int
    trend: str
    reasons: List[KPIReason]
    breakdown: KPIScoreBreakdown


class KPIChartPoint(BaseModel):
    label: str
    value: float
    meta: Optional[Dict] = None


class KPIChartSeries(BaseModel):
    name: str
    points: List[KPIChartPoint]


class KPIOverviewSummary(BaseModel):
    average_score: int
    active_tasks: int
    completed_tasks: int
    average_cycle_time_hours: Optional[float]
    defect_count: int


class KPIOverviewResponse(BaseModel):
    scorecards: List[KPIMemberScorecard]
    needs_attention: List[KPIMemberScorecard]
    summary: KPIOverviewSummary
    weights: KPIWeightSettingsOut


class KPISprintResponse(BaseModel):
    velocity_series: List[KPIChartSeries]
    burndown_series: List[KPIChartSeries]
    filter_options: KPIFilterOptions


class KPIQualityResponse(BaseModel):
    bugs_series: List[KPIChartSeries]
    mttr_series: List[KPIChartSeries]
    filter_options: KPIFilterOptions


class KPIMembersResponse(BaseModel):
    throughput_series: List[KPIChartSeries]
    cycle_time_series: List[KPIChartSeries]
    filter_options: KPIFilterOptions


class KPIDrilldownTask(BaseModel):
    id: int
    title: str
    task_type: Optional[str]
    assignee: Optional[str]
    project: Optional[str]
    sprint: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime]
    completed_at: Optional[datetime]


class KPIDrilldownResponse(BaseModel):
    tasks: List[KPIDrilldownTask]
    total: int
