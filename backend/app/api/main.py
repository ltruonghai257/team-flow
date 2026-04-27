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

from app.core.config import settings
from app.core.limiter import limiter
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
    sprints,
    statuses,
    sub_teams,
    tasks,
    timeline,
    users,
    websocket as ws_router,
)
from app.internal.scheduler_jobs import shutdown_scheduler, start_scheduler

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    command.upgrade(alembic_cfg, "head")


def create_app() -> FastAPI:
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

    application = FastAPI(
        title="TeamFlow API",
        description="Private team & personal task management with AI",
        version="1.0.0",
        lifespan=lifespan,
    )

    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(auth.router)
    application.include_router(users.router)
    application.include_router(invites.router)
    application.include_router(sub_teams.router)
    application.include_router(projects.router)
    application.include_router(statuses.router)
    application.include_router(milestones.router)
    application.include_router(sprints.router)
    application.include_router(tasks.router)
    application.include_router(schedules.router)
    application.include_router(notifications.router)
    application.include_router(ai.router)
    application.include_router(dashboard.router)
    application.include_router(performance.router)
    application.include_router(timeline.router)
    application.include_router(chat.router)
    application.include_router(ws_router.router)

    @application.get("/health")
    async def health():
        return {"status": "ok"}

    return application


app = create_app()
