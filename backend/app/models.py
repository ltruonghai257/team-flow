import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    supervisor = "supervisor"
    member = "member"


class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    review = "review"
    done = "done"
    blocked = "blocked"


class StatusSetScope(str, enum.Enum):
    sub_team_default = "sub_team_default"
    project = "project"


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class TaskType(str, enum.Enum):
    feature = "feature"
    bug = "bug"
    task = "task"
    improvement = "improvement"


class MilestoneStatus(str, enum.Enum):
    planned = "planned"
    in_progress = "in_progress"
    completed = "completed"
    delayed = "delayed"


class SprintStatus(str, enum.Enum):
    planned = "planned"
    active = "active"
    closed = "closed"


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    dismissed = "dismissed"


class NotificationEventType(str, enum.Enum):
    schedule = "schedule"
    task = "task"


class InviteStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    expired = "expired"
    cancelled = "cancelled"


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


class ChatChannel(Base):
    __tablename__ = "chat_channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    members = relationship(
        "ChatChannelMember", back_populates="channel", cascade="all, delete-orphan"
    )
    messages = relationship(
        "ChatMessage", back_populates="channel", cascade="all, delete-orphan"
    )


class ChatChannelMember(Base):
    __tablename__ = "chat_channel_members"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(
        Integer, ForeignKey("chat_channels.id"), nullable=False, index=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    joined_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    channel = relationship("ChatChannel", back_populates="members")


class ChatConversation(Base):
    """Direct message conversation between two users."""

    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_a_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user_b_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    last_message_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        index=True,
    )

    messages = relationship(
        "ChatMessage", back_populates="conversation", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    channel_id = Column(
        Integer, ForeignKey("chat_channels.id"), nullable=True, index=True
    )
    conversation_id = Column(
        Integer, ForeignKey("chat_conversations.id"), nullable=True, index=True
    )
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        index=True,
    )

    channel = relationship("ChatChannel", back_populates="messages")
    conversation = relationship("ChatConversation", back_populates="messages")


class UserPresence(Base):
    __tablename__ = "user_presence"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    is_online = Column(Boolean, default=False, nullable=False)
    custom_status = Column(String, nullable=True)
    last_seen = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    user = relationship("User", back_populates="ai_conversations")
    messages = relationship(
        "AIMessage", back_populates="conversation", order_by="AIMessage.created_at"
    )


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    model = Column(String, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    conversation = relationship("AIConversation", back_populates="messages")


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
