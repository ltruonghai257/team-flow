# Phase 1: Production Hardening - Research

## Context
Fix all critical issues that block production deployment.

## Technical Approaches

### 1. Alembic Migrations
- **Init:** `alembic init -t async migrations` (use async template since we use asyncpg).
- **Env.py:** Configure `target_metadata = Base.metadata` and `sqlalchemy.url = settings.DATABASE_URL` in `alembic/env.py`.
- **Lifespan runner:** In `main.py`, run `alembic upgrade head` programmatically.
  ```python
  from alembic.config import Config
  from alembic import command
  import asyncio
  
  def run_migrations():
      alembic_cfg = Config("alembic.ini")
      command.upgrade(alembic_cfg, "head")
      
  @asynccontextmanager
  async def lifespan(app: FastAPI):
      try:
          await asyncio.to_thread(run_migrations)
      except Exception as e:
          import sys
          print(f"Migration failed: {e}")
          sys.exit(1)
      # ...
  ```

### 2. SECRET_KEY Validation
Use Pydantic V2 `@field_validator` in `backend/app/config.py`:
```python
from pydantic import field_validator
from pydantic_core.core_schema import ValidationInfo

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change-me-in-production"

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info: ValidationInfo):
        env = info.data.get("ENVIRONMENT", "development")
        if env == "production" and v == "change-me-in-production":
            raise ValueError("SECRET_KEY must be changed in production")
        return v
```

### 3. CORS ALLOWED_ORIGINS
Parse from env string:
```python
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:4173,http://localhost:3000"
    
    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]
```

### 4. Rate Limiting (slowapi)
Need `slowapi` in `requirements.txt`.
Setup in `main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```
Add to `auth.py` and `ai.py` (ensure `request: Request` is added to signature):
```python
from fastapi import Request
from app.main import limiter

@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, ...):
```

### 5. `datetime.utcnow()`
Replace `datetime.utcnow()` with `datetime.now(timezone.utc).replace(tzinfo=None)`.
Need `from datetime import datetime, timezone`.
Files: `auth.py`, `routers/tasks.py`, `routers/ai.py`, `routers/dashboard.py`, `routers/notifications.py`, `routers/websocket.py`, `models.py`.

## RESEARCH COMPLETE
