from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import SubTeam, User
from app.models.updates import StandupPost, StandupSettings, StandupTemplate
from app.models.work import Task
from app.schemas.updates import (
    StandupPostCreate,
    StandupPostOut,
    StandupPostUpdate,
    TemplateOut,
    TemplateUpdate,
)
from app.utils.auth import get_current_user, get_sub_team, require_supervisor

router = APIRouter(prefix="/api/updates", tags=["updates"])

PAGE_SIZE = 20


# ─── helpers ──────────────────────────────────────────────────────────────────


async def _get_template_fields(db: AsyncSession, sub_team_id: Optional[int]) -> List[str]:
    """Return the effective template field list: sub-team override or global default."""
    if sub_team_id is not None:
        result = await db.execute(
            select(StandupTemplate).where(StandupTemplate.sub_team_id == sub_team_id)
        )
        template = result.scalar_one_or_none()
        if template:
            return template.fields

    # Fall back to global default (seeded in migration)
    result = await db.execute(select(StandupSettings).limit(1))
    settings_row = result.scalar_one_or_none()
    if settings_row:
        return settings_row.default_fields
    # Hard fallback if seed was skipped
    return ["Pending Tasks", "Future Tasks", "Blockers", "Need Help From", "Critical Timeline", "Release Date"]


async def _build_task_snapshot(db: AsyncSession, user_id: int) -> List[Dict[str, Any]]:
    """Capture all tasks assigned to user_id as a frozen JSON list (D-08, D-09)."""
    result = await db.execute(select(Task).where(Task.assignee_id == user_id))
    tasks = result.scalars().all()
    return [
        {
            "id": t.id,
            "title": t.title,
            "status": t.status.value if t.status else None,
            "priority": t.priority.value if t.priority else None,
            "due_date": t.due_date.isoformat() if t.due_date else None,
        }
        for t in tasks
    ]


# ─── template endpoints ────────────────────────────────────────────────────────


@router.get("/template", response_model=TemplateOut)
async def get_template(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    """Return the effective standup template for the caller's sub-team (UPD-01, UPD-02, per D-01/D-02)."""
    sub_team_id = sub_team.id if sub_team else None
    fields = await _get_template_fields(db, sub_team_id)
    return {"fields": fields}


@router.put("/template", response_model=TemplateOut)
async def update_template(
    payload: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    """Supervisor/admin upserts the sub-team template (UPD-03). Returns 403 for members."""
    if sub_team is None:
        raise HTTPException(status_code=400, detail="Sub-team context required to update template")

    result = await db.execute(
        select(StandupTemplate).where(StandupTemplate.sub_team_id == sub_team.id)
    )
    template = result.scalar_one_or_none()
    if template:
        template.fields = payload.fields
        template.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    else:
        template = StandupTemplate(
            sub_team_id=sub_team.id,
            fields=payload.fields,
        )
        db.add(template)

    await db.flush()
    await db.refresh(template)
    return {"fields": template.fields}


# ─── post endpoints ────────────────────────────────────────────────────────────


@router.get("/", response_model=Dict[str, Any])
async def list_posts(
    cursor: Optional[int] = None,
    author_id: Optional[int] = None,
    date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    """
    Return paginated standup posts newest-first (UPD-05, UPD-06, per D-04/D-06).
    Sub-team scoped: member/supervisor sees their sub-team; admin with no header sees all.
    Query params: cursor (last-seen post id), author_id, date (YYYY-MM-DD).
    Response: {"posts": [...], "next_cursor": int|null}
    """
    query = select(StandupPost)

    # Sub-team scoping (Pitfall 5: sub_team=None for admin → no filter, sees all)
    if sub_team is not None:
        query = query.where(StandupPost.sub_team_id == sub_team.id)

    if author_id is not None:
        query = query.where(StandupPost.author_id == author_id)

    if date is not None:
        try:
            day = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=422, detail="date must be YYYY-MM-DD")
        day_start = datetime(day.year, day.month, day.day, 0, 0, 0)
        day_end = datetime(day.year, day.month, day.day, 23, 59, 59)
        query = query.where(
            StandupPost.created_at >= day_start,
            StandupPost.created_at <= day_end,
        )

    if cursor is not None:
        query = query.where(StandupPost.id < cursor)

    query = query.order_by(StandupPost.id.desc()).limit(PAGE_SIZE + 1)
    result = await db.execute(query)
    rows = result.scalars().all()

    has_more = len(rows) > PAGE_SIZE
    posts = rows[:PAGE_SIZE]
    next_cursor = posts[-1].id if has_more and posts else None

    return {
        "posts": posts,
        "next_cursor": next_cursor,
    }


@router.post("/", status_code=201)
async def create_post(
    payload: StandupPostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    """
    Create a standup post (UPD-01, UPD-04).
    task_snapshot is built server-side from current tasks at POST time (D-08, D-09).
    Client never supplies task_snapshot.
    Returns 201 with the created post.
    """
    if sub_team is None:
        raise HTTPException(status_code=400, detail="Sub-team context required to post a standup")

    snapshot = await _build_task_snapshot(db, current_user.id)

    post = StandupPost(
        author_id=current_user.id,
        sub_team_id=sub_team.id,
        field_values=payload.field_values,
        task_snapshot=snapshot,
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)
    # Load author relationship for response
    await db.refresh(post, attribute_names=["author"])
    return post


@router.patch("/{post_id}")
async def update_post(
    post_id: int,
    payload: StandupPostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Edit own standup post (UPD-07, per D-10/D-11).
    Updates field_values ONLY. task_snapshot is never re-frozen on edit.
    Returns 404 if post not found, 403 if caller is not the author.
    """
    result = await db.execute(select(StandupPost).where(StandupPost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot modify another member's post")

    # Only field_values is patchable (StandupPostUpdate schema enforces this)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(post, field, value)

    await db.flush()
    await db.refresh(post)
    await db.refresh(post, attribute_names=["author"])
    return post


@router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete own standup post (UPD-08, per D-12).
    Returns 404 if post not found, 403 if caller is not the author.
    """
    result = await db.execute(select(StandupPost).where(StandupPost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot modify another member's post")

    await db.delete(post)
    await db.flush()
