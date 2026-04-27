from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.enums import InviteStatus, UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.member)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    sub_team_id = Column(Integer, ForeignKey("sub_teams.id"), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    assigned_tasks = relationship(
        "Task", back_populates="assignee", foreign_keys="Task.assignee_id"
    )
    created_tasks = relationship(
        "Task", back_populates="creator", foreign_keys="Task.creator_id"
    )
    schedules = relationship("Schedule", back_populates="user")
    ai_conversations = relationship("AIConversation", back_populates="user")
    sub_team = relationship(
        "SubTeam", back_populates="members", foreign_keys=[sub_team_id]
    )


class SubTeam(Base):
    __tablename__ = "sub_teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    supervisor = relationship("User", foreign_keys=[supervisor_id])
    members = relationship(
        "User", back_populates="sub_team", foreign_keys="User.sub_team_id"
    )


class TeamInvite(Base):
    __tablename__ = "team_invites"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    role = Column(Enum(UserRole), default=UserRole.member)
    token = Column(String, unique=True, nullable=False, index=True)
    validation_code = Column(String, nullable=False)
    status = Column(Enum(InviteStatus), default=InviteStatus.pending, index=True)
    invited_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sub_team_id = Column(Integer, ForeignKey("sub_teams.id"), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    invited_by = relationship("User", foreign_keys=[invited_by_id])
    sub_team = relationship("SubTeam", foreign_keys="TeamInvite.sub_team_id")


class KPIWeightSettings(Base):
    __tablename__ = "kpi_weight_settings"

    id = Column(Integer, primary_key=True, index=True)
    sub_team_id = Column(Integer, ForeignKey("sub_teams.id"), nullable=True, unique=True, index=True)
    workload_weight = Column(Integer, nullable=False, default=20)
    velocity_weight = Column(Integer, nullable=False, default=25)
    cycle_time_weight = Column(Integer, nullable=False, default=20)
    on_time_weight = Column(Integer, nullable=False, default=20)
    defect_weight = Column(Integer, nullable=False, default=15)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    sub_team = relationship("SubTeam", foreign_keys=[sub_team_id])
