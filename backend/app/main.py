# Phase 20 compatibility delegate — canonical path: app.api.main
# HIGH-RISK: keep through Phase 22. uvicorn, Dockerfile, and supervisord reference app.main:app.
from app.api.main import app, create_app, run_migrations  # noqa: F401
