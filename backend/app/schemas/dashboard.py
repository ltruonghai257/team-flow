from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import TaskPriority, TaskStatus


class DashboardTaskItem(BaseModel):
    """Slim task card for my_tasks (D-02)."""
    id: int
    title: str
    project_name: Optional[str] = None
    status: TaskStatus
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    is_overdue: bool
    is_due_soon: bool


class DashboardTeamHealthMember(BaseModel):
    """Per-member team health entry (D-06, D-07)."""
    user_id: int
    full_name: str
    avatar_url: Optional[str] = None
    status: str  # values: "green", "yellow", "red"
    active_tasks: int
    completed_30d: int
    overdue_tasks: int


class DashboardKpiSummary(BaseModel):
    """KPI strip (D-11)."""
    avg_score: int
    completion_rate: float  # 0.0–1.0
    needs_attention_count: int


class DashboardActivityItem(BaseModel):
    """Recent standup post entry (D-14, D-15)."""
    post_id: int
    author_id: int
    author_name: str
    created_at: datetime
    field_values: Dict  # full JSONB — Phase 32 decides what to render


class DashboardPayload(BaseModel):
    """Top-level response schema (D-01, D-09, D-12)."""
    model_config = ConfigDict(exclude_none=True)  # makes team_health and kpi_summary absent (not null) for member role

    my_tasks: List[DashboardTaskItem]
    team_health: Optional[List[DashboardTeamHealthMember]] = None
    kpi_summary: Optional[DashboardKpiSummary] = None
    recent_activity: List[DashboardActivityItem]
