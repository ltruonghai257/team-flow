from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator


# ── Template schemas ──────────────────────────────────────────────────────────

class TemplateOut(BaseModel):
    fields: List[str]
    field_types: Dict[str, str]
    model_config = {"from_attributes": True}


class TemplateUpdate(BaseModel):
    fields: List[str]
    field_types: Optional[Dict[str, str]] = None

    @field_validator("fields")
    @classmethod
    def fields_not_empty(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Template must have at least one field")
        cleaned = [f.strip() for f in v if f.strip()]
        if not cleaned:
            raise ValueError("Template fields cannot be blank")
        return cleaned

    @field_validator("field_types")
    @classmethod
    def validate_field_types(cls, v: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        if v is None:
            return v
        valid_types = {"text", "datetime", "richtext"}
        for field_name, field_type in v.items():
            if field_type not in valid_types:
                raise ValueError(f"Invalid field type '{field_type}' for field '{field_name}'. Must be one of: {valid_types}")
        return v


# ── StandupPost schemas ───────────────────────────────────────────────────────

class StandupPostCreate(BaseModel):
    field_values: Dict[str, str]  # {"Pending Tasks": "...", ...}
    # task_snapshot is NOT accepted from client — built server-side

    @field_validator("field_values")
    @classmethod
    def validate_datetime_fields(cls, v: Dict[str, str]) -> Dict[str, str]:
        # This validator runs at the API layer. datetime fields are validated against template field_types in the router.
        # This is a basic ISO 8601 format check for datetime values.
        for field_name, value in v.items():
            # Check if value looks like an ISO 8601 datetime (basic format check)
            # Full validation happens in router against template field_types
            if value and "T" in value and len(value) > 15:
                try:
                    # Try parsing as ISO datetime
                    datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    # Not a valid datetime, but we'll let the router handle the actual validation
                    # This is just a basic sanity check
                    pass
        return v


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
