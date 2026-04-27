# Phase 20 compatibility delegate — canonical path: app.schemas package
# HIGH-RISK: keep through Phase 22. Routers and tests use this path.
# The schemas/ package now contains all domain modules; this file re-exports for compatibility.
from app.schemas import *  # noqa: F401, F403
