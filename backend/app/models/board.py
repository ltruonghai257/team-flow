from datetime import datetime, timezone

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.database import Base


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class WeeklyPost(Base):
    __tablename__ = "weekly_posts"
    __table_args__ = (
        UniqueConstraint("author_id", "iso_year", "iso_week", name="uq_weekly_posts_author_week"),
    )

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sub_team_id = Column(Integer, ForeignKey("sub_teams.id"), nullable=False, index=True)
    iso_year = Column(Integer, nullable=False, index=True)
    iso_week = Column(Integer, nullable=False, index=True)
    week_start_date = Column(Date, nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    author = relationship("User", foreign_keys=[author_id])
    sub_team = relationship("SubTeam", foreign_keys=[sub_team_id])
    appends = relationship(
        "WeeklyPostAppend",
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="WeeklyPostAppend.created_at",
    )


class WeeklyPostAppend(Base):
    __tablename__ = "weekly_post_appends"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("weekly_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_now, index=True)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    post = relationship("WeeklyPost", back_populates="appends")
    author = relationship("User", foreign_keys=[author_id])


class WeeklyBoardSummary(Base):
    __tablename__ = "weekly_board_summaries"
    __table_args__ = (
        UniqueConstraint("sub_team_id", "iso_year", "iso_week", name="uq_weekly_board_summary_week"),
    )

    id = Column(Integer, primary_key=True, index=True)
    sub_team_id = Column(Integer, ForeignKey("sub_teams.id"), nullable=False, index=True)
    iso_year = Column(Integer, nullable=False, index=True)
    iso_week = Column(Integer, nullable=False, index=True)
    week_start_date = Column(Date, nullable=False, index=True)
    summary_text = Column(Text, nullable=False)
    source_post_count = Column(Integer, nullable=False, default=0)
    generated_by_mode = Column(String, nullable=False, default="manual")
    generated_at = Column(DateTime, default=_now, index=True)

    sub_team = relationship("SubTeam", foreign_keys=[sub_team_id])
