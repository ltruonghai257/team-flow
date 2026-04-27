from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.enums import (
    NotificationEventType,
    NotificationStatus,
    ReminderProposalStatus,
)


class EventNotification(Base):
    __tablename__ = "event_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(Enum(NotificationEventType), nullable=False)
    event_ref_id = Column(Integer, nullable=False)
    title_cache = Column(String, nullable=False)
    start_at_cache = Column(DateTime, nullable=False)
    remind_at = Column(DateTime, nullable=False, index=True)
    offset_minutes = Column(Integer, nullable=False, default=15)
    status = Column(
        Enum(NotificationStatus), default=NotificationStatus.pending, index=True
    )
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )


class SubTeamReminderSettings(Base):
    __tablename__ = "sub_team_reminder_settings"

    id = Column(Integer, primary_key=True, index=True)
    sub_team_id = Column(
        Integer, ForeignKey("sub_teams.id"), nullable=False, unique=True, index=True
    )
    lead_time_days = Column(Integer, nullable=False, default=2)
    sprint_reminders_enabled = Column(Boolean, nullable=False, default=True)
    milestone_reminders_enabled = Column(Boolean, nullable=False, default=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    sub_team = relationship("SubTeam", foreign_keys=[sub_team_id])


class ReminderSettingsProposal(Base):
    __tablename__ = "reminder_settings_proposals"

    id = Column(Integer, primary_key=True, index=True)
    sub_team_id = Column(Integer, ForeignKey("sub_teams.id"), nullable=False, index=True)
    proposed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    lead_time_days = Column(Integer, nullable=True)
    sprint_reminders_enabled = Column(Boolean, nullable=True)
    milestone_reminders_enabled = Column(Boolean, nullable=True)
    status = Column(
        Enum(ReminderProposalStatus),
        nullable=False,
        default=ReminderProposalStatus.pending,
        index=True,
    )
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    reviewed_at = Column(DateTime, nullable=True)

    sub_team = relationship("SubTeam", foreign_keys=[sub_team_id])
    proposed_by = relationship("User", foreign_keys=[proposed_by_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
