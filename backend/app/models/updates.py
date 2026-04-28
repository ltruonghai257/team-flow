from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.database import Base


class StandupPost(Base):
    __tablename__ = "standup_posts"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sub_team_id = Column(Integer, ForeignKey("sub_teams.id"), nullable=False, index=True)
    field_values = Column(JSONB, nullable=False)
    task_snapshot = Column(JSONB, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        index=True,
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    author = relationship("User", foreign_keys=[author_id])


class StandupTemplate(Base):
    __tablename__ = "standup_templates"

    id = Column(Integer, primary_key=True, index=True)
    sub_team_id = Column(Integer, ForeignKey("sub_teams.id"), nullable=False, unique=True, index=True)
    fields = Column(JSONB, nullable=False)  # ordered list of field-name strings
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )


class StandupSettings(Base):
    """Single-row global default template settings. Seeded in migration."""
    __tablename__ = "standup_settings"

    id = Column(Integer, primary_key=True, index=True)
    default_fields = Column(JSONB, nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
