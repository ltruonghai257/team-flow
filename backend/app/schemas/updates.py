from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator


# ── Template schemas ──────────────────────────────────────────────────────────

class TemplateOut(BaseModel):
    fields: List[str]
    model_config = {"from_attributes": True}


class TemplateUpdate(BaseModel):
    fields: List[str]

    @field_validator("fields")
    @classmethod
    def fields_not_empty(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Template must have at least one field")
        cleaned = [f.strip() for f in v if f.strip()]
        if not cleaned:
            raise ValueError("Template fields cannot be blank")
        return cleaned


# ── StandupPost schemas ───────────────────────────────────────────────────────

class StandupPostCreate(BaseModel):
    field_values: Dict[str, str]  # {"Pending Tasks": "...", ...}
    # task_snapshot is NOT accepted from client — built server-side


class StandupPostUpdate(BaseModel):
    # SECURITY: only field_values is patchable.
    # task_snapshot, author_id, sub_team_id are EXCLUDED to prevent mass-assignment.
    field_values: Dict[str, str]


class AuthorOut(BaseModel):
    id: int
    full_name: str
    model_config = {"from_attributes": True}


class StandupPostOut(BaseModel):
    id: int
    author_id: int
    sub_team_id: int
    field_values: Dict[str, Any]
    task_snapshot: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    author: Optional[AuthorOut] = None
    model_config = {"from_attributes": True}
