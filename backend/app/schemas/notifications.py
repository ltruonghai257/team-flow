from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

from app.models.enums import NotificationEventType, NotificationStatus, ReminderProposalStatus


class NotificationCreate(BaseModel):
    event_type: NotificationEventType
    event_ref_id: int
    offset_minutes: int  # how many minutes before event to fire


class NotificationBulkCreate(BaseModel):
    event_type: NotificationEventType
    event_ref_id: int
    offset_minutes_list: list[int]  # replace any existing reminders with this set


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


class ReminderSettingsOut(BaseModel):
    id: int
    sub_team_id: int
    lead_time_days: int
    sprint_reminders_enabled: bool
    milestone_reminders_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReminderSettingsUpdate(BaseModel):
    lead_time_days: Optional[int] = Field(default=None, ge=0, le=30)
    sprint_reminders_enabled: Optional[bool] = None
    milestone_reminders_enabled: Optional[bool] = None


class ReminderSettingsProposalCreate(BaseModel):
    lead_time_days: Optional[int] = Field(default=None, ge=0, le=30)
    sprint_reminders_enabled: Optional[bool] = None
    milestone_reminders_enabled: Optional[bool] = None

    @model_validator(mode="after")
    def _require_change(self):
        if (
            self.lead_time_days is None
            and self.sprint_reminders_enabled is None
            and self.milestone_reminders_enabled is None
        ):
            raise ValueError("At least one proposed setting must be provided")
        return self


class ReminderSettingsProposalReview(BaseModel):
    decision: Literal["approve", "reject"]


class ReminderSettingsProposalOut(BaseModel):
    id: int
    sub_team_id: int
    proposed_by_id: int
    reviewed_by_id: Optional[int]
    lead_time_days: Optional[int]
    sprint_reminders_enabled: Optional[bool]
    milestone_reminders_enabled: Optional[bool]
    status: ReminderProposalStatus
    created_at: datetime
    reviewed_at: Optional[datetime]

    model_config = {"from_attributes": True}
