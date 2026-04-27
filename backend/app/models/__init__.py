# app.models aggregate compatibility surface — Phase 20
# Imports all domain modules so Base.metadata is fully populated,
# and re-exports every symbol that was previously importable from app.models.
# HIGH-RISK: keep through Phase 22 (Alembic env.py, tests, and routers use this path).
#
# Domain cluster deviations from Phase 19 map default:
#   - SubTeam kept in users.py (not separate teams.py) to avoid FK cycle complexity
#   - Schedule kept in work.py (FK to tasks)

from app.models.enums import (  # noqa: F401
    InviteStatus,
    MilestoneStatus,
    NotificationEventType,
    NotificationStatus,
    ReminderProposalStatus,
    SprintStatus,
    StatusSetScope,
    TaskPriority,
    TaskStatus,
    TaskType,
    UserRole,
)
from app.models.users import KPIWeightSettings, SubTeam, TeamInvite, User  # noqa: F401
from app.models.work import (  # noqa: F401
    CustomStatus,
    Milestone,
    Project,
    Schedule,
    Sprint,
    StatusSet,
    StatusTransition,
    Task,
)
from app.models.notifications import (  # noqa: F401
    EventNotification,
    ReminderSettingsProposal,
    SubTeamReminderSettings,
)
from app.models.communication import (  # noqa: F401
    ChatChannel,
    ChatChannelMember,
    ChatConversation,
    ChatMessage,
    UserPresence,
)
from app.models.ai import AIConversation, AIMessage  # noqa: F401
