"""Package structure import compatibility tests — Phase 20.

Verifies that canonical and compatibility import paths for high-risk
runtime surfaces resolve to the same objects.
"""
import os
from pathlib import Path

os.environ.setdefault(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{Path(__file__).resolve().parent / 'test.db'}",
)
os.environ.setdefault("RUN_MIGRATIONS", "false")
os.environ.setdefault("COOKIE_SECURE", "false")


def test_canonical_app_import():
    from app.api.main import app, create_app
    assert app is not None
    assert callable(create_app)


def test_compat_app_import_same_object():
    from app.api.main import app as canonical_app
    from app.main import app as compat_app
    assert canonical_app is compat_app


def test_app_routes_include_health():
    from app.api.main import app
    paths = {getattr(r, "path", "") for r in app.routes}
    assert "/health" in paths


def test_app_routes_include_ws_chat():
    from app.api.main import app
    paths = {getattr(r, "path", "") for r in app.routes}
    assert "/ws/chat" in paths


def test_app_routes_include_api_tasks():
    from app.api.main import app
    paths = {getattr(r, "path", "") for r in app.routes}
    assert any(p.startswith("/api/tasks") for p in paths)


def test_canonical_config_import():
    from app.core.config import settings
    assert settings is not None
    assert hasattr(settings, "DATABASE_URL")


def test_compat_config_same_object():
    from app.core.config import settings as canonical_settings
    from app.config import settings as compat_settings
    assert canonical_settings is compat_settings


def test_canonical_database_import():
    from app.db.database import Base, AsyncSessionLocal, get_db
    assert Base is not None
    assert AsyncSessionLocal is not None
    assert callable(get_db)


def test_compat_database_same_object():
    from app.db.database import Base as canonical_base
    from app.database import Base as compat_base
    assert canonical_base is compat_base


def test_canonical_scheduler_import():
    from app.internal.scheduler_jobs import start_scheduler, shutdown_scheduler
    assert callable(start_scheduler)
    assert callable(shutdown_scheduler)


def test_compat_scheduler_same_object():
    from app.internal.scheduler_jobs import start_scheduler as canonical_start
    from app.scheduler_jobs import start_scheduler as compat_start
    assert canonical_start is compat_start


def test_canonical_socket_manager_import():
    from app.socket.manager import manager
    assert manager is not None


def test_compat_websocket_manager_same_object():
    from app.socket.manager import manager as canonical_manager
    from app.websocket.manager import manager as compat_manager
    assert canonical_manager is compat_manager


# ── Plan 20-02: Model Package ─────────────────────────────────────────────────

def test_aggregate_models_import():
    from app.models import User, Task, EventNotification
    assert User is not None
    assert Task is not None
    assert EventNotification is not None


def test_aggregate_models_full_required_set():
    import app.models as m
    required = [
        "User", "SubTeam", "Project", "Milestone", "Sprint", "Task",
        "StatusSet", "CustomStatus", "StatusTransition",
        "EventNotification", "Schedule", "AIConversation",
    ]
    missing = [name for name in required if not hasattr(m, name)]
    assert not missing, f"Missing from app.models: {missing}"


def test_canonical_model_domain_imports():
    from app.models.users import User, SubTeam, TeamInvite, KPIWeightSettings
    from app.models.work import Task, Project, Milestone, Sprint, StatusSet, CustomStatus, StatusTransition, Schedule
    from app.models.notifications import EventNotification, SubTeamReminderSettings, ReminderSettingsProposal
    from app.models.communication import ChatChannel, ChatConversation, ChatMessage, UserPresence
    from app.models.ai import AIConversation, AIMessage
    assert Task is not None
    assert User is not None
    assert AIConversation is not None


def test_models_metadata_tables():
    from app.db.database import Base
    import app.models  # noqa: F401 — ensure registration
    tables = set(Base.metadata.tables.keys())
    for expected in ("users", "tasks", "event_notifications"):
        assert expected in tables, f"Table '{expected}' not in metadata"
