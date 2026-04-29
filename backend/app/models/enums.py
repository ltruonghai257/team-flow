import enum


class UserRole(str, enum.Enum):
    manager = "manager"
    supervisor = "supervisor"
    assistant_manager = "assistant_manager"
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
    knowledge_session = "knowledge_session"
    sprint_end = "sprint_end"
    milestone_due = "milestone_due"
    reminder_settings_proposal = "reminder_settings_proposal"


class KnowledgeSessionType(str, enum.Enum):
    presentation = "presentation"
    demo = "demo"
    workshop = "workshop"
    qa = "qa"


class ReminderProposalStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class InviteStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    expired = "expired"
    cancelled = "cancelled"


class MilestoneDecisionStatus(str, enum.Enum):
    proposed = "proposed"
    approved = "approved"
    rejected = "rejected"
    superseded = "superseded"
