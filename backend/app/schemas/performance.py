from typing import List, Optional

from pydantic import BaseModel

from app.schemas.work import TaskOut


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
