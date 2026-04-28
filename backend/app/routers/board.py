from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import SubTeam, User, WeeklyPost, WeeklyPostAppend
from app.schemas.board import (
    WeeklyBoardSummaryOut,
    WeeklyBoardWeekResponse,
    WeeklyPostAppendCreate,
    WeeklyPostAppendOut,
    WeeklyPostAppendUpdate,
    WeeklyPostCreate,
    WeeklyPostOut,
    WeeklyPostUpdate,
)
from app.services.weekly_board import (
    current_board_week,
    generate_weekly_board_summary,
    get_weekly_board_payload,
    normalize_board_week,
)
from app.utils.auth import get_current_user, get_sub_team

router = APIRouter(prefix="/api/board", tags=["board"])


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def _load_post(db: AsyncSession, post_id: int) -> WeeklyPost | None:
    result = await db.execute(select(WeeklyPost).where(WeeklyPost.id == post_id))
    return result.scalar_one_or_none()


async def _load_append(db: AsyncSession, append_id: int) -> WeeklyPostAppend | None:
    result = await db.execute(select(WeeklyPostAppend).where(WeeklyPostAppend.id == append_id))
    return result.scalar_one_or_none()


@router.get("/week", response_model=WeeklyBoardWeekResponse)
async def get_week(
    year: Optional[int] = None,
    week: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    payload = await get_weekly_board_payload(db, current_user, sub_team, year, week)
    return payload


@router.post("/posts", response_model=WeeklyPostOut, status_code=201)
async def create_post(
    payload: WeeklyPostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    if sub_team is None:
        raise HTTPException(status_code=400, detail="Sub-team context required")
    week = current_board_week()
    existing = await db.execute(
        select(WeeklyPost).where(
            WeeklyPost.author_id == current_user.id,
            WeeklyPost.iso_year == week.iso_year,
            WeeklyPost.iso_week == week.iso_week,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Primary post already exists for this week")
    post = WeeklyPost(
        author_id=current_user.id,
        sub_team_id=sub_team.id,
        iso_year=week.iso_year,
        iso_week=week.iso_week,
        week_start_date=week.week_start_date,
        content=payload.content,
    )
    db.add(post)
    await db.flush()
    await db.refresh(post, attribute_names=["author", "appends"])
    return post


@router.patch("/posts/{post_id}", response_model=WeeklyPostOut)
async def update_post(
    post_id: int,
    payload: WeeklyPostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await _load_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot modify another member's post")
    if post.iso_year != current_board_week().iso_year or post.iso_week != current_board_week().iso_week:
        raise HTTPException(status_code=403, detail="Past weeks are read-only")
    post.content = payload.content
    post.updated_at = _now()
    await db.flush()
    await db.refresh(post, attribute_names=["author", "appends"])
    return post


@router.delete("/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await _load_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot modify another member's post")
    if post.iso_year != current_board_week().iso_year or post.iso_week != current_board_week().iso_week:
        raise HTTPException(status_code=403, detail="Past weeks are read-only")
    await db.delete(post)
    await db.flush()


@router.post("/posts/{post_id}/appends", response_model=WeeklyPostAppendOut, status_code=201)
async def create_append(
    post_id: int,
    payload: WeeklyPostAppendCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await _load_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot append to another member's post")
    if post.iso_year != current_board_week().iso_year or post.iso_week != current_board_week().iso_week:
        raise HTTPException(status_code=403, detail="Past weeks are read-only")
    append = WeeklyPostAppend(post_id=post.id, author_id=current_user.id, content=payload.content)
    db.add(append)
    await db.flush()
    await db.refresh(append, attribute_names=["author"])
    return append


@router.patch("/appends/{append_id}", response_model=WeeklyPostAppendOut)
async def update_append(
    append_id: int,
    payload: WeeklyPostAppendUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    append = await _load_append(db, append_id)
    if not append:
        raise HTTPException(status_code=404, detail="Append not found")
    if append.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot modify another member's append")
    if append.post.iso_year != current_board_week().iso_year or append.post.iso_week != current_board_week().iso_week:
        raise HTTPException(status_code=403, detail="Past weeks are read-only")
    append.content = payload.content
    append.updated_at = _now()
    await db.flush()
    await db.refresh(append, attribute_names=["author"])
    return append


@router.delete("/appends/{append_id}", status_code=204)
async def delete_append(
    append_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    append = await _load_append(db, append_id)
    if not append:
        raise HTTPException(status_code=404, detail="Append not found")
    if append.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot modify another member's append")
    if append.post.iso_year != current_board_week().iso_year or append.post.iso_week != current_board_week().iso_week:
        raise HTTPException(status_code=403, detail="Past weeks are read-only")
    await db.delete(append)
    await db.flush()


@router.post("/week/summary", response_model=WeeklyBoardSummaryOut)
async def summarize_week(
    year: Optional[int] = None,
    week: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    if sub_team is None:
        raise HTTPException(status_code=400, detail="Sub-team context required")
    target = normalize_board_week(year, week)
    summary = await generate_weekly_board_summary(
        db,
        sub_team_id=sub_team.id,
        iso_year=target.iso_year,
        iso_week=target.iso_week,
        generated_by_mode="manual",
    )
    return summary
