# Phase 20 compatibility delegate — canonical path: app.utils.auth
# Review for removal in Phase 22 after runtime/Docker/Azure verification.
from app.utils.auth import (  # noqa: F401
    oauth2_scheme,
    verify_password,
    hash_password,
    create_access_token,
    get_current_user,
    require_supervisor,
    require_admin,
    require_supervisor_or_admin,
    get_sub_team,
    get_user_from_cookie,
)
