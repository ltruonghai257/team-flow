from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Iterable, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models import SubTeam, User, WeeklyBoardSummary, WeeklyPost, WeeklyPostAppend
from app.utils.ai_client import acompletion


SUMMARY_COOLDOWN_MINUTES = 30
EMPTY_WEEK_SUMMARY = "No updates this week"


@dataclass
class BoardWeek:
    iso_year: int
    iso_week: int
    week_start_date: date


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _week_start(iso_year: int, iso_week: int) -> date:
    return date.fromisocalendar(iso_year, iso_week, 1)


def current_board_week(now: Optional[datetime] = None) -> BoardWeek:
    current = now or _now()
    iso = current.isocalendar()
    return BoardWeek(iso.year, iso.week, _week_start(iso.year, iso.week))


def normalize_board_week(iso_year: Optional[int], iso_week: Optional[int], now: Optional[datetime] = None) -> BoardWeek:
    if iso_year is None or iso_week is None:
        return current_board_week(now)
    return BoardWeek(iso_year, iso_week, _week_start(iso_year, iso_week))


async def resolve_visible_sub_team(db: AsyncSession, current_user: User, sub_team: Optional[SubTeam]) -> Optional[SubTeam]:
    return sub_team


def _post_text(post: WeeklyPost) -> str:
    append_lines = "\n".join(f"- {append.content}" for append in post.appends)
    return f"{post.content}\n{append_lines}".strip()


def _build_summary_prompt(posts: Iterable[WeeklyPost]) -> str:
    blocks = []
    for post in posts:
        author = post.author.full_name if post.author else f"User {post.author_id}"
        blocks.append(f"{author}:\n{_post_text(post)}")
    return "\n\n".join(blocks)


async def get_weekly_board_payload(
    db: AsyncSession,
    current_user: User,
    sub_team: Optional[SubTeam],
    iso_year: Optional[int] = None,
    iso_week: Optional[int] = None,
) -> dict:
    week = normalize_board_week(iso_year, iso_week)
    current_week = current_board_week()

    post_stmt = (
        select(WeeklyPost)
        .options(selectinload(WeeklyPost.author), selectinload(WeeklyPost.appends).selectinload(WeeklyPostAppend.author))
        .where(
            WeeklyPost.iso_year == week.iso_year,
            WeeklyPost.iso_week == week.iso_week,
        )
        .order_by(WeeklyPost.created_at.asc())
    )
    if sub_team is not None:
        post_stmt = post_stmt.where(WeeklyPost.sub_team_id == sub_team.id)
    result = await db.execute(post_stmt)
    posts = result.scalars().all()

    summary_stmt = select(WeeklyBoardSummary).where(
        WeeklyBoardSummary.iso_year == week.iso_year,
        WeeklyBoardSummary.iso_week == week.iso_week,
    )
    if sub_team is not None:
        summary_stmt = summary_stmt.where(WeeklyBoardSummary.sub_team_id == sub_team.id)
    summary = (await db.execute(summary_stmt)).scalar_one_or_none()

    options_stmt = (
        select(WeeklyPost.iso_year, WeeklyPost.iso_week, func.min(WeeklyPost.week_start_date))
        .group_by(WeeklyPost.iso_year, WeeklyPost.iso_week)
        .order_by(func.min(WeeklyPost.week_start_date).desc())
    )
    if sub_team is not None:
        options_stmt = options_stmt.where(WeeklyPost.sub_team_id == sub_team.id)
    options_result = await db.execute(options_stmt)
    week_options = [
        {
            "iso_year": year,
            "iso_week": week,
            "week_start_date": start,
            "label": f"{start.isoformat()} · W{week}",
            "is_current_week": year == current_week.iso_year and week == current_week.iso_week,
        }
        for year, week, start in options_result.all()
    ]

    return {
        "selected_iso_year": week.iso_year,
        "selected_iso_week": week.iso_week,
        "selected_week_start_date": week.week_start_date,
        "summary": summary,
        "posts": posts,
        "week_options": week_options,
        "viewer_can_post": week.iso_year == current_week.iso_year and week.iso_week == current_week.iso_week,
        "is_current_week": week.iso_year == current_week.iso_year and week.iso_week == current_week.iso_week,
    }


async def get_summary_cooldown(
    db: AsyncSession,
    sub_team_id: int,
    iso_year: int,
    iso_week: int,
) -> dict:
    summary = (
        await db.execute(
            select(WeeklyBoardSummary).where(
                WeeklyBoardSummary.sub_team_id == sub_team_id,
                WeeklyBoardSummary.iso_year == iso_year,
                WeeklyBoardSummary.iso_week == iso_week,
            )
        )
    ).scalar_one_or_none()
    if not summary:
        return {"active": False, "remaining_minutes": 0}
    age = _now() - summary.generated_at
    remaining = max(0, SUMMARY_COOLDOWN_MINUTES - int(age.total_seconds() // 60))
    return {"active": remaining > 0, "remaining_minutes": remaining}


async def upsert_weekly_board_summary(
    db: AsyncSession,
    *,
    sub_team_id: int,
    iso_year: int,
    iso_week: int,
    week_start_date: date,
    summary_text: str,
    source_post_count: int,
    generated_by_mode: str,
) -> WeeklyBoardSummary:
    result = await db.execute(
        select(WeeklyBoardSummary).where(
            WeeklyBoardSummary.sub_team_id == sub_team_id,
            WeeklyBoardSummary.iso_year == iso_year,
            WeeklyBoardSummary.iso_week == iso_week,
        )
    )
    row = result.scalar_one_or_none()
    if row is None:
        row = WeeklyBoardSummary(
            sub_team_id=sub_team_id,
            iso_year=iso_year,
            iso_week=iso_week,
            week_start_date=week_start_date,
            summary_text=summary_text,
            source_post_count=source_post_count,
            generated_by_mode=generated_by_mode,
            generated_at=_now(),
        )
        db.add(row)
    else:
        row.week_start_date = week_start_date
        row.summary_text = summary_text
        row.source_post_count = source_post_count
        row.generated_by_mode = generated_by_mode
        row.generated_at = _now()
    await db.flush()
    await db.refresh(row)
    return row


async def generate_weekly_board_summary(
    db: AsyncSession,
    *,
    sub_team_id: int,
    iso_year: int,
    iso_week: int,
    generated_by_mode: str = "manual",
) -> WeeklyBoardSummary:
    posts = (
        await db.execute(
            select(WeeklyPost)
            .options(selectinload(WeeklyPost.author), selectinload(WeeklyPost.appends).selectinload(WeeklyPostAppend.author))
            .where(
                WeeklyPost.sub_team_id == sub_team_id,
                WeeklyPost.iso_year == iso_year,
                WeeklyPost.iso_week == iso_week,
            )
            .order_by(WeeklyPost.created_at.asc())
        )
    ).scalars().all()

    if not posts:
        return await upsert_weekly_board_summary(
            db,
            sub_team_id=sub_team_id,
            iso_year=iso_year,
            iso_week=iso_week,
            week_start_date=_week_start(iso_year, iso_week),
            summary_text=EMPTY_WEEK_SUMMARY,
            source_post_count=0,
            generated_by_mode=generated_by_mode,
        )

    cooldown = await get_summary_cooldown(db, sub_team_id, iso_year, iso_week)
    if generated_by_mode == "manual" and cooldown["active"]:
        existing = (
            await db.execute(
                select(WeeklyBoardSummary).where(
                    WeeklyBoardSummary.sub_team_id == sub_team_id,
                    WeeklyBoardSummary.iso_year == iso_year,
                    WeeklyBoardSummary.iso_week == iso_week,
                )
            )
        ).scalar_one()
        return existing

    prompt = _build_summary_prompt(posts)
    response = await acompletion(
        model=settings.AI_MODEL,
        messages=[
            {"role": "system", "content": "Summarize the team's weekly board in a concise digest."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    summary_text = (response.choices[0].message.content or "").strip() or EMPTY_WEEK_SUMMARY
    return await upsert_weekly_board_summary(
        db,
        sub_team_id=sub_team_id,
        iso_year=iso_year,
        iso_week=iso_week,
        week_start_date=_week_start(iso_year, iso_week),
        summary_text=summary_text,
        source_post_count=len(posts),
        generated_by_mode=generated_by_mode,
    )
