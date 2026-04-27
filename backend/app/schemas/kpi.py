from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, field_validator

from app.models.enums import TaskType


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


class KPIWarningEmailRequest(BaseModel):
    user_id: int
    kpi_score: int
    level: str
    message: Optional[str] = None


class KPIWarningEmailResponse(BaseModel):
    sent: bool
    level: str
    recipient_email: str


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
