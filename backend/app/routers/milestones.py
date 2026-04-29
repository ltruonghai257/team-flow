from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.utils.auth import get_current_user, get_sub_team
from app.db.database import get_db
from app.models import (
    Milestone,
    MilestoneDecision,
    MilestoneDecisionStatus,
    MilestoneStatus,
    Project,
    SubTeam,
    Task,
    TaskStatus,
    User,
)
from app.schemas import (
    MilestoneCommandViewMetrics,
    MilestoneCommandViewMilestone,
    MilestoneCommandViewResponse,
    MilestoneCreate,
    MilestoneDecisionCreate,
    MilestoneDecisionOut,
    MilestoneDecisionSummary,
    MilestoneDecisionUpdate,
    MilestoneOut,
    MilestoneTaskRollup,
    MilestoneUpdate,
)
from app.services.reminder_notifications import rebuild_milestone_reminders
from app.services.visibility import scoped_sub_team_filter, visible_sub_team_ids

router = APIRouter(prefix="/api/milestones", tags=["milestones"])


async def _visible_project_ids(
    db: AsyncSession,
    current_user: User,
    sub_team: Optional[SubTeam] = None,
):
    return await visible_sub_team_ids(
        db, current_user, requested_sub_team_id=sub_team.id if sub_team else None
    )


def _milestone_scope_filter(current_user: User, allowed_ids):
    return scoped_sub_team_filter(Project.sub_team_id, current_user, allowed_ids)


async def _get_visible_project(
    db: AsyncSession,
    current_user: User,
    project_id: int,
) -> Project:
    allowed_ids = await _visible_project_ids(db, current_user)
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            scoped_sub_team_filter(Project.sub_team_id, current_user, allowed_ids),
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def _get_visible_milestone(
    db: AsyncSession,
    current_user: User,
    milestone_id: int,
) -> Milestone:
    allowed_ids = await _visible_project_ids(db, current_user)
    result = await db.execute(
        select(Milestone)
        .join(Project)
        .where(
            Milestone.id == milestone_id,
            _milestone_scope_filter(current_user, allowed_ids),
        )
    )
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return milestone


async def _get_visible_decision(
    db: AsyncSession,
    current_user: User,
    decision_id: int,
) -> MilestoneDecision:
    allowed_ids = await _visible_project_ids(db, current_user)
    result = await db.execute(
        select(MilestoneDecision)
        .join(Milestone)
        .join(Project)
        .where(
            MilestoneDecision.id == decision_id,
            _milestone_scope_filter(current_user, allowed_ids),
        )
    )
    decision = result.scalar_one_or_none()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision


@router.get("/", response_model=List[MilestoneOut])
async def list_milestones(
    project_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    allowed_ids = await _visible_project_ids(db, current_user, sub_team)
    query = select(Milestone).join(Project).where(
        _milestone_scope_filter(current_user, allowed_ids)
    )
    if project_id:
        query = query.where(Milestone.project_id == project_id)
    query = query.order_by(Milestone.due_date)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/command-view/", response_model=MilestoneCommandViewResponse)
async def command_view(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    # Fetch milestones with eager-loaded relationships
    stmt = (
        select(Milestone)
        .options(
            selectinload(Milestone.project),
            selectinload(Milestone.decisions),
            selectinload(Milestone.tasks).selectinload(Task.assignee),
            selectinload(Milestone.tasks).selectinload(Task.custom_status),
        )
        .join(Project)
    )

    allowed_ids = await _visible_project_ids(db, current_user, sub_team)
    stmt = stmt.where(_milestone_scope_filter(current_user, allowed_ids))

    result = await db.execute(stmt)
    milestones = result.scalars().unique().all()

    def derive_planning_state(m: Milestone) -> str:
        if m.status == MilestoneStatus.completed:
            return "completed"
        if m.status == MilestoneStatus.in_progress:
            return "active"
        if m.start_date and m.due_date and len(m.tasks) > 0:
            return "committed"
        return "planned"

    def derive_risk(m: Milestone) -> Optional[str]:
        if m.status == MilestoneStatus.completed:
            return None

        # Blocked: any linked task is blocked
        if any(
            t.status == TaskStatus.blocked
            or (t.custom_status and t.custom_status.name.lower() == "blocked")
            for t in m.tasks
        ):
            return "blocked"

        # Delayed: status is delayed or due date passed
        if m.status == MilestoneStatus.delayed or (m.due_date and m.due_date < now):
            return "delayed"

        # At Risk: any overdue task
        if any(
            t.due_date
            and t.due_date < now
            and t.status != TaskStatus.done
            and (not t.custom_status or not t.custom_status.is_done)
            for t in m.tasks
        ):
            return "at_risk"

        # Watch: any proposed decisions
        if any(d.status == MilestoneDecisionStatus.proposed for d in m.decisions):
            return "watch"

        return None

    def compute_rollup(tasks: List[Task]) -> MilestoneTaskRollup:
        total = len(tasks)
        if total == 0:
            return MilestoneTaskRollup()

        done = sum(
            1
            for t in tasks
            if t.status == TaskStatus.done
            or (t.custom_status and t.custom_status.is_done)
        )
        blocked = sum(1 for t in tasks if t.status == TaskStatus.blocked)

        return MilestoneTaskRollup(
            total=total,
            done=done,
            blocked=blocked,
            completion_percent=round((done / total) * 100, 1) if total > 0 else 0.0,
        )

    def compute_decision_summary(
        decisions: List[MilestoneDecision],
    ) -> MilestoneDecisionSummary:
        return MilestoneDecisionSummary(
            proposed=sum(
                1 for d in decisions if d.status == MilestoneDecisionStatus.proposed
            ),
            approved=sum(
                1 for d in decisions if d.status == MilestoneDecisionStatus.approved
            ),
            rejected=sum(
                1 for d in decisions if d.status == MilestoneDecisionStatus.rejected
            ),
            superseded=sum(
                1 for d in decisions if d.status == MilestoneDecisionStatus.superseded
            ),
        )

    lanes = {"planned": [], "committed": [], "active": [], "completed": []}
    metrics = MilestoneCommandViewMetrics()

    for m in milestones:
        planning_state = derive_planning_state(m)
        risk = derive_risk(m)
        progress = compute_rollup(m.tasks)
        decision_summary = compute_decision_summary(m.decisions)

        # Update metrics
        if planning_state == "active":
            metrics.active_milestones += 1
        if risk:
            metrics.risky_milestones += 1
        metrics.proposed_decisions += decision_summary.proposed
        metrics.blocked_tasks += progress.blocked

        # Sort tasks: status first (done last), then due date
        def task_sort_key(t: Task):
            is_done = t.status == TaskStatus.done or (
                t.custom_status and t.custom_status.is_done
            )
            status_rank = 1 if is_done else 0
            due = t.due_date or datetime.max
            return (status_rank, due)

        sorted_tasks = sorted(m.tasks, key=task_sort_key)

        view_milestone = MilestoneCommandViewMilestone(
            id=m.id,
            title=m.title,
            description=m.description,
            status=m.status,
            planning_state=planning_state,
            risk=risk,
            start_date=m.start_date,
            due_date=m.due_date,
            completed_at=m.completed_at,
            project_id=m.project_id,
            project_name=m.project.name,
            project_color=m.project.color,
            progress=progress,
            decision_summary=decision_summary,
            tasks=sorted_tasks,
            decisions=m.decisions,
        )
        lanes[planning_state].append(view_milestone)

    # Sort milestones within lanes: risk first, then due date
    risk_rank = {"blocked": 0, "delayed": 1, "at_risk": 2, "watch": 3, None: 4}
    for lane_name in lanes:
        lanes[lane_name].sort(key=lambda x: (risk_rank.get(x.risk, 4), x.due_date))

    return MilestoneCommandViewResponse(metrics=metrics, lanes=lanes)


@router.post("/", response_model=MilestoneOut, status_code=201)
async def create_milestone(
    payload: MilestoneCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_visible_project(db, current_user, payload.project_id)
    milestone = Milestone(**payload.model_dump())
    db.add(milestone)
    await db.flush()
    await db.refresh(milestone)
    
    # Rebuild reminders for milestone
    await rebuild_milestone_reminders(db, milestone.id)
    
    return milestone


@router.get("/{milestone_id}", response_model=MilestoneOut)
async def get_milestone(
    milestone_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await _get_visible_milestone(db, current_user, milestone_id)


@router.patch("/{milestone_id}", response_model=MilestoneOut)
async def update_milestone(
    milestone_id: int,
    payload: MilestoneUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    milestone = await _get_visible_milestone(db, current_user, milestone_id)
    
    # Track if due_date changed
    old_due_date = milestone.due_date
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(milestone, field, value)
    await db.flush()
    await db.refresh(milestone)
    
    # Rebuild reminders if due_date changed
    if old_due_date != milestone.due_date:
        await rebuild_milestone_reminders(db, milestone.id)
    
    return milestone


@router.delete("/{milestone_id}", status_code=204)
async def delete_milestone(
    milestone_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    milestone = await _get_visible_milestone(db, current_user, milestone_id)
    await db.delete(milestone)
    await db.flush()


# ── Milestone Decisions ───────────────────────────────────────────────────────


@router.get("/{milestone_id}/decisions", response_model=List[MilestoneDecisionOut])
async def list_milestone_decisions(
    milestone_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_visible_milestone(db, current_user, milestone_id)

    result = await db.execute(
        select(MilestoneDecision)
        .where(MilestoneDecision.milestone_id == milestone_id)
        .order_by(MilestoneDecision.created_at.desc())
    )
    return result.scalars().all()


@router.post(
    "/{milestone_id}/decisions", response_model=MilestoneDecisionOut, status_code=201
)
async def create_milestone_decision(
    milestone_id: int,
    payload: MilestoneDecisionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _get_visible_milestone(db, current_user, milestone_id)

    # If task_id is provided, verify it exists and belongs to the same milestone
    if payload.task_id:
        task_result = await db.execute(
            select(Task).where(
                Task.id == payload.task_id, Task.milestone_id == milestone_id
            )
        )
        if not task_result.scalar_one_or_none():
            raise HTTPException(
                status_code=400, detail="Task not found or not linked to this milestone"
            )

    decision = MilestoneDecision(**payload.model_dump())
    decision.milestone_id = milestone_id  # Ensure it matches the URL
    db.add(decision)
    await db.flush()
    await db.refresh(decision)
    return decision


@router.patch("/decisions/{decision_id}", response_model=MilestoneDecisionOut)
async def update_milestone_decision(
    decision_id: int,
    payload: MilestoneDecisionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = await _get_visible_decision(db, current_user, decision_id)

    # If task_id is being updated, verify it exists and belongs to the same milestone
    if payload.task_id is not None:
        task_result = await db.execute(
            select(Task).where(
                Task.id == payload.task_id, Task.milestone_id == decision.milestone_id
            )
        )
        if not task_result.scalar_one_or_none():
            raise HTTPException(
                status_code=400, detail="Task not found or not linked to this milestone"
            )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(decision, field, value)
    await db.flush()
    await db.refresh(decision)
    return decision


@router.delete("/decisions/{decision_id}", status_code=204)
async def delete_milestone_decision(
    decision_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = await _get_visible_decision(db, current_user, decision_id)
    await db.delete(decision)
    await db.flush()
