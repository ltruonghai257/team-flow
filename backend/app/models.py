# Phase 20 compatibility delegate — canonical path: app.models package
# HIGH-RISK: keep through Phase 22. Alembic env.py, tests, and routers use this path.
# The models/ package now contains all domain modules; this file re-exports for compatibility.
from app.models import *  # noqa: F401, F403
