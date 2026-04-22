from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import ai, auth, chat, dashboard, milestones, notifications, projects, schedules, tasks, users, websocket as ws_router
from app.scheduler_jobs import shutdown_scheduler, start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(milestones.router)
app.include_router(tasks.router)
app.include_router(schedules.router)
app.include_router(notifications.router)
app.include_router(ai.router)
app.include_router(dashboard.router)
app.include_router(chat.router)
app.include_router(ws_router.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
