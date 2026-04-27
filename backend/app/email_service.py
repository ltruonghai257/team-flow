# Phase 20 compatibility delegate — canonical path: app.utils.email_service
# Review for removal in Phase 22 after runtime/Docker/Azure verification.
from app.utils.email_service import send_invite_email, send_kpi_warning_email  # noqa: F401
