from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.enums import KnowledgeSessionType


def _to_naive_utc(v):
    """Convert tz-aware datetime to naive UTC; pass through naive datetimes and None."""
    if isinstance(v, datetime) and v.tzinfo is not None:
        return v.astimezone(timezone.utc).replace(tzinfo=None)
    return v


def _normalize_tag_list(value):
    if value is None:
        return None
    if isinstance(value, str):
        items = value.split(",")
    else:
        items = list(value)
    normalized = []
    seen = set()
    for item in items:
        if item is None:
            continue
        tag = str(item).strip()
        if not tag:
            continue
        key = tag.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(tag)
    return normalized


class KnowledgeSessionPresenterOut(BaseModel):
    id: int
    full_name: str
    username: str
    avatar_url: Optional[str] = None
    sub_team_id: Optional[int] = None

    model_config = {"from_attributes": True}


class KnowledgeSessionCreate(BaseModel):
    topic: str
    description: Optional[str] = None
    references: Optional[str] = None
    presenter_id: Optional[int] = None
    session_type: KnowledgeSessionType = KnowledgeSessionType.presentation
    duration_minutes: int = Field(ge=15)
    start_time: datetime
    tags: list[str] = []
    offset_minutes_list: list[int] = []

    _normalize_start = field_validator("start_time", mode="after")(_to_naive_utc)
    _normalize_tags = field_validator("tags", mode="before")(
        lambda v: _normalize_tag_list(v) or []
    )


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

    _normalize_start = field_validator("start_time", mode="after")(_to_naive_utc)
    _normalize_tags = field_validator("tags", mode="before")(_normalize_tag_list)


class KnowledgeSessionOut(BaseModel):
    id: int
    topic: str
    description: Optional[str]
    references: Optional[str]
    presenter_id: int
    session_type: KnowledgeSessionType
    start_time: datetime
    duration_minutes: int
    tags: list[str]
    sub_team_id: Optional[int]
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    presenter: Optional[KnowledgeSessionPresenterOut] = None

    model_config = {"from_attributes": True}

    _normalize_tags = field_validator("tags", mode="before")(
        lambda v: _normalize_tag_list(v) or []
    )
