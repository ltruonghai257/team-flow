from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.enums import TaskType


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
