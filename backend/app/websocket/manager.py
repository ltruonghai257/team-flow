# Phase 20 compatibility delegate — canonical path: app.socket.manager
# Review for removal in Phase 22 after runtime/Docker/Azure verification.
from app.socket.manager import ConnectionManager, manager  # noqa: F401
