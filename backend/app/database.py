# Phase 20 compatibility delegate — canonical path: app.db.database
# Review for removal in Phase 22 after runtime/Docker/Azure verification.
from app.db.database import engine, AsyncSessionLocal, Base, get_db  # noqa: F401
