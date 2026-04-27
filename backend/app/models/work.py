from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.enums import (
    MilestoneStatus,
    SprintStatus,
    StatusSetScope,
    TaskPriority,
    TaskStatus,
    TaskType,
)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String, default="#6366f1")
    sub_team_id = Column(Integer, ForeignKey("sub_teams.id"), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    milestones = relationship("Milestone", back_populates="project")
    tasks = relationship("Task", back_populates="project")
    sub_team = relationship("SubTeam", foreign_keys="Project.sub_team_id")


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(MilestoneStatus), default=MilestoneStatus.planned)
    start_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    project = relationship("Project", back_populates="milestones")
    tasks = relationship("Task", back_populates="milestone")
    sprints = relationship("Sprint", back_populates="milestone")


class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(Enum(SprintStatus), default=SprintStatus.planned)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    milestone = relationship("Milestone", back_populates="sprints")
    tasks = relationship("Task", back_populates="sprint")


class StatusSet(Base):
    __tablename__ = "status_sets"

    id = Column(Integer, primary_key=True, index=True)
    scope = Column(Enum(StatusSetScope), nullable=False, index=True)
    sub_team_id = Column(Integer, ForeignKey("sub_teams.id"), nullable=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    statuses = relationship(
        "CustomStatus",
        back_populates="status_set",
        order_by="CustomStatus.position",
        cascade="all, delete-orphan",
    )
    transitions = relationship(
        "StatusTransition",
        back_populates="status_set",
        cascade="all, delete-orphan",
    )
    sub_team = relationship("SubTeam")
    project = relationship("Project")


class CustomStatus(Base):
    __tablename__ = "custom_statuses"

    id = Column(Integer, primary_key=True, index=True)
    status_set_id = Column(
        Integer, ForeignKey("status_sets.id"), nullable=False, index=True
    )
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, index=True)
    color = Column(String, nullable=False, default="#64748b")
    position = Column(Integer, nullable=False, default=0)
    is_done = Column(Boolean, nullable=False, default=False, index=True)
    is_archived = Column(Boolean, nullable=False, default=False, index=True)
    legacy_status = Column(Enum(TaskStatus), nullable=True, index=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    status_set = relationship("StatusSet", back_populates="statuses")
    tasks = relationship("Task", back_populates="custom_status")
    outgoing_transitions = relationship(
        "StatusTransition",
        back_populates="from_status",
        foreign_keys="StatusTransition.from_status_id",
        cascade="all, delete-orphan",
    )
    incoming_transitions = relationship(
        "StatusTransition",
        back_populates="to_status",
        foreign_keys="StatusTransition.to_status_id",
        cascade="all, delete-orphan",
    )


class StatusTransition(Base):
    __tablename__ = "status_transitions"
    __table_args__ = (
        UniqueConstraint(
            "status_set_id",
            "from_status_id",
            "to_status_id",
            name="uq_status_transitions_status_set_from_to",
        ),
        CheckConstraint(
            "from_status_id != to_status_id",
            name="ck_status_transitions_no_self_transition",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    status_set_id = Column(
        Integer,
        ForeignKey("status_sets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_status_id = Column(
        Integer,
        ForeignKey("custom_statuses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    to_status_id = Column(
        Integer,
        ForeignKey("custom_statuses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    status_set = relationship("StatusSet", back_populates="transitions")
    from_status = relationship(
        "CustomStatus",
        back_populates="outgoing_transitions",
        foreign_keys=[from_status_id],
    )
    to_status = relationship(
        "CustomStatus",
        back_populates="incoming_transitions",
        foreign_keys=[to_status_id],
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.todo)
    priority = Column(Enum(TaskPriority), default=TaskPriority.medium)
    type = Column(Enum(TaskType), default=TaskType.task, nullable=False)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_hours = Column(Integer, nullable=True)
    tags = Column(String, nullable=True)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    custom_status_id = Column(
        Integer, ForeignKey("custom_statuses.id"), nullable=True, index=True
    )
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    project = relationship("Project", back_populates="tasks")
    milestone = relationship("Milestone", back_populates="tasks")
    sprint = relationship("Sprint", back_populates="tasks")
    custom_status = relationship("CustomStatus", back_populates="tasks")
    assignee = relationship(
        "User", back_populates="assigned_tasks", foreign_keys=[assignee_id]
    )
    creator = relationship(
        "User", back_populates="created_tasks", foreign_keys=[creator_id]
    )


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    all_day = Column(Boolean, default=False)
    color = Column(String, default="#6366f1")
    location = Column(String, nullable=True)
    recurrence = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    user = relationship("User", back_populates="schedules")
