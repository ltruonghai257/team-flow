import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.limiter import limiter
from app.routers import (
    ai,
    auth,
    chat,
    dashboard,
    invites,
    milestones,
    notifications,
    performance,
    projects,
    schedules,
    sub_teams,
    tasks,
    timeline,
    users,
    websocket as ws_router,
)
from app.scheduler_jobs import shutdown_scheduler, start_scheduler

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.RUN_MIGRATIONS:
        try:
            await asyncio.to_thread(run_migrations)
        except Exception as exc:
            logger.error("Alembic migration failed: %s", exc)
            sys.exit(1)
    start_scheduler()
    try:
        yield
    finally:
        shutdown_scheduler()


app = FastAPI(
    title="TeamFlow API",
    description="Private team & personal task management with AI",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(invites.router)
app.include_router(sub_teams.router)
app.include_router(projects.router)
app.include_router(milestones.router)
app.include_router(tasks.router)
app.include_router(schedules.router)
app.include_router(notifications.router)
app.include_router(ai.router)
app.include_router(dashboard.router)
app.include_router(performance.router)
app.include_router(timeline.router)
app.include_router(chat.router)
app.include_router(ws_router.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
