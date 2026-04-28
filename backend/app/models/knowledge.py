from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.enums import KnowledgeSessionType


class KnowledgeSession(Base):
    __tablename__ = "knowledge_sessions"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    references = Column(Text, nullable=True)
    session_type = Column(
        Enum(KnowledgeSessionType),
        nullable=False,
        default=KnowledgeSessionType.presentation,
    )
    start_time = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False)
    tags = Column(String, nullable=True)
    presenter_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sub_team_id = Column(Integer, ForeignKey("sub_teams.id"), nullable=True, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
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

    presenter = relationship("User", foreign_keys=[presenter_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    sub_team = relationship("SubTeam", foreign_keys=[sub_team_id])
