from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.enums import KnowledgeSessionType
from app.schemas.work import _to_naive_utc


def _normalize_tag_list(value):
    if value is None:
        return []
    if not isinstance(value, list):
        return value
    normalized = []
    seen = set()
    for tag in value:
        if tag is None:
            continue
        cleaned = str(tag).strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(cleaned)
    return normalized


class KnowledgeSessionPresenterOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    role: str
    sub_team_id: Optional[int] = None

    model_config = {"from_attributes": True}


class KnowledgeSessionCreate(BaseModel):
    topic: str
    description: Optional[str] = None
    references: Optional[str] = None
    presenter_id: Optional[int] = None
    session_type: KnowledgeSessionType = KnowledgeSessionType.presentation
    duration_minutes: int = Field(..., ge=15)
    start_time: datetime
    tags: list[str] = Field(default_factory=list)
    offset_minutes_list: list[int] = Field(default_factory=list)

    _normalize_start_time = field_validator("start_time", mode="after")(_to_naive_utc)
    _normalize_tags = field_validator("tags", mode="after")(_normalize_tag_list)


class KnowledgeSessionUpdate(BaseModel):
    topic: Optional[str] = None
    description: Optional[str] = None
    references: Optional[str] = None
    presenter_id: Optional[int] = None
    session_type: Optional[KnowledgeSessionType] = None
    duration_minutes: Optional[int] = Field(default=None, ge=15)
    start_time: Optional[datetime] = None
    tags: Optional[list[str]] = None
    offset_minutes_list: Optional[list[int]] = None

    _normalize_start_time = field_validator("start_time", mode="after")(_to_naive_utc)
    _normalize_tags = field_validator("tags", mode="after")(_normalize_tag_list)


class KnowledgeSessionOut(BaseModel):
    id: int
    topic: str
    description: Optional[str]
    references: Optional[str]
    presenter_id: int
    session_type: KnowledgeSessionType
    start_time: datetime
    duration_minutes: int
    tags: list[str] = Field(default_factory=list)
    sub_team_id: Optional[int]
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    presenter: Optional[KnowledgeSessionPresenterOut] = None

    model_config = {"from_attributes": True}
