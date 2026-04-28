from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.updates import AuthorOut


class WeeklyPostAppendCreate(BaseModel):
    content: str


class WeeklyPostAppendUpdate(BaseModel):
    content: str


class WeeklyPostAppendOut(BaseModel):
    id: int
    author_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    author: Optional[AuthorOut] = None

    model_config = {"from_attributes": True}


class WeeklyPostCreate(BaseModel):
    content: str


class WeeklyPostUpdate(BaseModel):
    content: str


class WeeklyPostOut(BaseModel):
    id: int
    author_id: int
    sub_team_id: int
    iso_year: int
    iso_week: int
    week_start_date: date
    content: str
    created_at: datetime
    updated_at: datetime
    author: Optional[AuthorOut] = None
    appends: list[WeeklyPostAppendOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class WeeklyBoardSummaryOut(BaseModel):
    id: int
    sub_team_id: int
    iso_year: int
    iso_week: int
    week_start_date: date
    summary_text: str
    source_post_count: int
    generated_by_mode: str
    generated_at: datetime

    model_config = {"from_attributes": True}


class WeeklyBoardWeekOptionOut(BaseModel):
    iso_year: int
    iso_week: int
    week_start_date: date
    label: str
    is_current_week: bool = False


class WeeklyBoardWeekResponse(BaseModel):
    selected_iso_year: int
    selected_iso_week: int
    selected_week_start_date: date
    summary: Optional[WeeklyBoardSummaryOut] = None
    posts: list[WeeklyPostOut] = Field(default_factory=list)
    week_options: list[WeeklyBoardWeekOptionOut] = Field(default_factory=list)
    viewer_can_post: bool = False
    is_current_week: bool = False

    model_config = {"from_attributes": True}

    @field_validator("posts", "week_options", mode="before")
    @classmethod
    def default_lists(cls, value):
        return value or []
