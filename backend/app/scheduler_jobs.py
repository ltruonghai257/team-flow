# Phase 20 compatibility delegate — canonical path: app.internal.scheduler_jobs
# Review for removal in Phase 22 after runtime/Docker/Azure verification.
from app.internal.scheduler_jobs import (  # noqa: F401
    process_due_notifications,
    reconcile_generated_reminders_job,
    start_scheduler,
    shutdown_scheduler,
)
