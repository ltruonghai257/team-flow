from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, extract, case, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.utils.auth import require_supervisor, get_sub_team
from app.db.database import get_db
from app.utils.email_service import send_kpi_warning_email
from app.models import Project, SubTeam, User, Task, TaskStatus, TaskType, ChatMessage, KPIWeightSettings, CustomStatus, Sprint, SprintStatus
from app.schemas import (
    PerformanceDashboard,
    TeamMemberPerformance,
    UserPerformanceDetail,
    TrendDataPoint,
    TaskOut,
    KPIWeightSettingsOut,
    KPIWeightSettingsUpdate,
    KPIOverviewResponse,
    KPIOverviewSummary,
    KPIMemberScorecard,
    KPIScoreBreakdown,
    KPIReason,
    KPISprintResponse,
    KPIQualityResponse,
    KPIMembersResponse,
    KPIDrilldownResponse,
    KPIDrilldownTask,
    KPIChartSeries,
    KPIChartPoint,
    KPIFilterOptions,
    KPIWarningEmailRequest,
    KPIWarningEmailResponse,
)

router = APIRouter(prefix="/api/performance", tags=["performance"])


async def _get_or_create_kpi_weights(
    db: AsyncSession, sub_team: Optional[SubTeam]
) -> KPIWeightSettings:
    target_sub_team_id = sub_team.id if sub_team else None
    result = await db.execute(
        select(KPIWeightSettings).where(
            KPIWeightSettings.sub_team_id == target_sub_team_id
        )
    )
    weights = result.scalar_one_or_none()
    if weights is None:
        weights = KPIWeightSettings(sub_team_id=target_sub_team_id)
        db.add(weights)
        await db.flush()
    return weights


@router.get("/kpi/weights", response_model=KPIWeightSettingsOut)
async def get_kpi_weights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    weights = await _get_or_create_kpi_weights(db, sub_team)
    await db.commit()
    await db.refresh(weights)
    return weights


@router.patch("/kpi/weights", response_model=KPIWeightSettingsOut)
async def update_kpi_weights(
    payload: KPIWeightSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    payload.validate_sum()
    weights = await _get_or_create_kpi_weights(db, sub_team)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(weights, field, value)
    await db.commit()
    await db.refresh(weights)
    return weights


@router.post("/kpi/warning-email", response_model=KPIWarningEmailResponse)
async def send_kpi_warning(
    payload: KPIWarningEmailRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    if payload.level not in ("fair", "at_risk"):
        raise HTTPException(status_code=400, detail="level must be 'fair' or 'at_risk'")
    if payload.level == "fair" and not (60 <= payload.kpi_score < 80):
        raise HTTPException(status_code=400, detail="Fair warning requires score 60–79")
    if payload.level == "at_risk" and payload.kpi_score >= 60:
        raise HTTPException(status_code=400, detail="Serious warning requires score below 60")

    result = await db.execute(select(User).where(User.id == payload.user_id))
    recipient = result.scalar_one_or_none()
    if not recipient:
        raise HTTPException(status_code=404, detail="User not found")
    if sub_team and recipient.sub_team_id != sub_team.id:
        raise HTTPException(status_code=403, detail="You can only warn users in your sub-team")

    default_message = (
        "This is a friendly reminder that your KPI score is currently in the Fair range. "
        "Please review your workload, delivery timing, and open tasks so we can improve together."
        if payload.level == "fair"
        else "This is a serious warning that your KPI score is currently At Risk. "
        "Please review your performance dashboard and align with your supervisor on immediate next steps."
    )
    await send_kpi_warning_email(
        to_email=recipient.email,
        recipient_name=recipient.full_name,
        supervisor_name=current_user.full_name,
        level=payload.level,
        kpi_score=payload.kpi_score,
        message=payload.message or default_message,
    )
    return KPIWarningEmailResponse(
        sent=True,
        level=payload.level,
        recipient_email=recipient.email,
    )


@router.get("/team", response_model=PerformanceDashboard)
async def get_team_performance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    thirty_days_ago = now - timedelta(days=30)
    forty_eight_hours_ahead = now + timedelta(hours=48)

    # 1. Main Metrics Query (Aggregate Filter Pattern)
    metrics_stmt = select(
        User.id,
        User.full_name,
        User.avatar_url,
        # Active Tasks: all except 'done'
        func.count(Task.id)
        .filter(Task.status != TaskStatus.done)
        .label("active_tasks"),
        # Completed (30d)
        func.count(Task.id)
        .filter(Task.status == TaskStatus.done, Task.completed_at >= thirty_days_ago)
        .label("completed_30d"),
        # Cycle Time (Hours)
        func.avg(extract("epoch", Task.completed_at - Task.created_at) / 3600)
        .filter(Task.status == TaskStatus.done)
        .label("avg_cycle_time"),
        # On-Time Count
        func.count(Task.id)
        .filter(Task.status == TaskStatus.done, Task.completed_at <= Task.due_date)
        .label("on_time_count"),
        # Total with Due Date (Completed)
        func.count(Task.id)
        .filter(Task.status == TaskStatus.done, Task.due_date.is_not(None))
        .label("total_completed_with_due_date"),
        # Overdue Count (Active tasks past due date)
        func.count(Task.id)
        .filter(Task.status != TaskStatus.done, Task.due_date < now)
        .label("overdue_count"),
        # Due Soon (Active tasks due within 48h)
        func.count(Task.id)
        .filter(
            Task.status != TaskStatus.done,
            Task.due_date >= now,
            Task.due_date <= forty_eight_hours_ahead,
        )
        .label("due_soon_count"),
    ).join(Task, User.id == Task.assignee_id, isouter=True)

    # Apply sub-team filter
    if sub_team:
        metrics_stmt = metrics_stmt.join(Project, Task.project_id == Project.id).where(
            Project.sub_team_id == sub_team.id
        )

    metrics_stmt = metrics_stmt.group_by(User.id)

    metrics_result = await db.execute(metrics_stmt)
    metrics_rows = metrics_result.all()

    # 2. Collaboration Score (Message count 30d)
    collab_stmt = (
        select(User.id, func.count(ChatMessage.id))
        .join(ChatMessage, User.id == ChatMessage.sender_id)
        .where(ChatMessage.created_at >= thirty_days_ago)
        .group_by(User.id)
    )
    collab_result = await db.execute(collab_stmt)
    collab_map = {row[0]: row[1] for row in collab_result.all()}

    team_metrics = []
    total_active = 0
    total_on_time = 0
    total_with_due = 0

    for row in metrics_rows:
        user_id = row.id
        active_tasks = row.active_tasks
        overdue_count = row.overdue_count
        due_soon_count = row.due_soon_count

        # Calculate On-Time Rate
        on_time_count = row.on_time_count
        with_due = row.total_completed_with_due_date
        on_time_rate = (on_time_count / with_due * 100) if with_due > 0 else 100.0

        # Collaboration Score
        collab_score = collab_map.get(user_id, 0)

        # Status Logic
        if overdue_count > 0 or active_tasks > 10:
            status = "red"
        elif due_soon_count > 0 or active_tasks > 7:
            status = "yellow"
        else:
            status = "green"

        team_metrics.append(
            TeamMemberPerformance(
                user_id=user_id,
                full_name=row.full_name,
                avatar_url=row.avatar_url,
                active_tasks=active_tasks,
                completed_30d=row.completed_30d,
                avg_cycle_time=(
                    round(row.avg_cycle_time, 1) if row.avg_cycle_time else None
                ),
                on_time_rate=round(on_time_rate, 1),
                collaboration_score=collab_score,
                status=status,
            )
        )

        total_active += active_tasks
        total_on_time += on_time_count
        total_with_due += with_due

    overall_on_time = (
        (total_on_time / total_with_due * 100) if total_with_due > 0 else 100.0
    )

    return PerformanceDashboard(
        team_metrics=team_metrics,
        overall_on_time_rate=round(overall_on_time, 1),
        total_active_tasks=total_active,
    )


@router.get("/user/{user_id}", response_model=UserPerformanceDetail)
async def get_user_performance_detail(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_supervisor),
):
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    thirty_days_ago = now - timedelta(days=30)
    eight_weeks_ago = (now - timedelta(weeks=8)).date()

    # 1. Fetch Metrics (Similar to team query but for single user)
    # We can reuse the logic or run a simpler version
    metrics_stmt = select(
        func.count(Task.id)
        .filter(Task.status != TaskStatus.done)
        .label("active_tasks"),
        func.count(Task.id)
        .filter(Task.status == TaskStatus.done, Task.completed_at >= thirty_days_ago)
        .label("completed_30d"),
        func.avg(extract("epoch", Task.completed_at - Task.created_at) / 3600)
        .filter(Task.status == TaskStatus.done)
        .label("avg_cycle_time"),
        func.count(Task.id)
        .filter(Task.status == TaskStatus.done, Task.completed_at <= Task.due_date)
        .label("on_time_count"),
        func.count(Task.id)
        .filter(Task.status == TaskStatus.done, Task.due_date.is_not(None))
        .label("total_completed_with_due_date"),
        func.count(Task.id)
        .filter(Task.status != TaskStatus.done, Task.due_date < now)
        .label("overdue_count"),
        func.count(Task.id)
        .filter(
            Task.status != TaskStatus.done,
            Task.due_date >= now,
            Task.due_date <= now + timedelta(hours=48),
        )
        .label("due_soon_count"),
    ).where(Task.assignee_id == user_id)
    metrics_result = await db.execute(metrics_stmt)
    m = metrics_result.one()

    # 2. Collaboration Score
    collab_stmt = select(func.count(ChatMessage.id)).where(
        ChatMessage.sender_id == user_id, ChatMessage.created_at >= thirty_days_ago
    )
    collab_score = (await db.execute(collab_stmt)).scalar() or 0

    # 3. Trend Data (8 weeks)
    # Group by date of completed_at
    trend_stmt = (
        select(
            func.date(Task.completed_at).label("date"),
            func.count(Task.id).label("count"),
        )
        .where(
            Task.assignee_id == user_id,
            Task.status == TaskStatus.done,
            Task.completed_at >= eight_weeks_ago,
        )
        .group_by(func.date(Task.completed_at))
        .order_by(func.date(Task.completed_at))
    )
    trend_result = await db.execute(trend_stmt)
    trend_data = [
        TrendDataPoint(date=str(row[0]), completed_count=row[1])
        for row in trend_result.all()
    ]

    # 4. Recent Completed Tasks
    recent_tasks_stmt = (
        select(Task)
        .options(selectinload(Task.custom_status), selectinload(Task.assignee))
        .where(Task.assignee_id == user_id, Task.status == TaskStatus.done)
        .order_by(desc(Task.completed_at))
        .limit(5)
    )
    recent_tasks_result = await db.execute(recent_tasks_stmt)
    recent_tasks = recent_tasks_result.scalars().all()

    # Status Logic
    active_tasks = m.active_tasks
    if m.overdue_count > 0 or active_tasks > 10:
        status = "red"
    elif m.due_soon_count > 0 or active_tasks > 7:
        status = "yellow"
    else:
        status = "green"

    on_time_rate = (
        (m.on_time_count / m.total_completed_with_due_date * 100)
        if m.total_completed_with_due_date > 0
        else 100.0
    )

    performance = TeamMemberPerformance(
        user_id=user.id,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        active_tasks=active_tasks,
        completed_30d=m.completed_30d,
        avg_cycle_time=round(m.avg_cycle_time, 1) if m.avg_cycle_time else None,
        on_time_rate=round(on_time_rate, 1),
        collaboration_score=collab_score,
        status=status,
    )

    return UserPerformanceDetail(
        user_id=user.id,
        full_name=user.full_name,
        metrics=performance,
        trend_data=trend_data,
        recent_completed_tasks=recent_tasks,
    )


# ── KPI helper predicates ──────────────────────────────────────────────────────


def _completed_task_filter():
    return [
        Task.completed_at.is_not(None),
        Task.custom_status_id == CustomStatus.id,
        CustomStatus.is_done.is_(True),
    ]


def _active_task_filter():
    return [
        Task.custom_status_id == CustomStatus.id,
        CustomStatus.is_done.is_(False),
    ]


def _scoped_task_select(sub_team: Optional[SubTeam]):
    stmt = select(Task).join(Project, Task.project_id == Project.id)
    if sub_team:
        stmt = stmt.where(Project.sub_team_id == sub_team.id)
    return stmt


def _score_workload(active_tasks: int) -> int:
    if active_tasks <= 7:
        return 100
    elif active_tasks <= 10:
        return 70
    return 40


def _score_velocity(completed_30d: int) -> int:
    return min(100, completed_30d * 10)


def _score_cycle_time(avg_hours: Optional[float]) -> int:
    if avg_hours is None:
        return 40
    if avg_hours <= 48:
        return 100
    elif avg_hours <= 120:
        return 70
    return 40


def _score_on_time(on_time_pct: float) -> int:
    return round(on_time_pct)


def _score_defects(mttr_hours: Optional[float]) -> int:
    if mttr_hours is None:
        return 100
    if mttr_hours <= 72:
        return 100
    elif mttr_hours <= 168:
        return 70
    return 40


# ── KPI overview ───────────────────────────────────────────────────────────────


@router.get("/kpi/overview", response_model=KPIOverviewResponse)
async def get_kpi_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    thirty_days_ago = now - timedelta(days=30)

    weights = await _get_or_create_kpi_weights(db, sub_team)

    # Per-member aggregates
    base = select(
        User.id,
        User.full_name,
        User.avatar_url,
        func.count(Task.id).filter(
            Task.custom_status_id == CustomStatus.id,
            CustomStatus.is_done.is_(False),
        ).label("active_tasks"),
        func.count(Task.id).filter(
            Task.completed_at.is_not(None),
            Task.completed_at >= thirty_days_ago,
            Task.custom_status_id == CustomStatus.id,
            CustomStatus.is_done.is_(True),
        ).label("completed_30d"),
        func.avg(
            extract("epoch", Task.completed_at - Task.created_at) / 3600
        ).filter(
            Task.completed_at.is_not(None),
            Task.custom_status_id == CustomStatus.id,
            CustomStatus.is_done.is_(True),
        ).label("avg_cycle_time"),
        func.count(Task.id).filter(
            Task.completed_at.is_not(None),
            Task.due_date.is_not(None),
            Task.completed_at <= Task.due_date,
            Task.custom_status_id == CustomStatus.id,
            CustomStatus.is_done.is_(True),
        ).label("on_time_count"),
        func.count(Task.id).filter(
            Task.due_date.is_not(None),
            Task.custom_status_id == CustomStatus.id,
            CustomStatus.is_done.is_(True),
        ).label("total_with_due"),
        func.count(Task.id).filter(
            Task.type == TaskType.bug,
            Task.completed_at.is_not(None),
            Task.custom_status_id == CustomStatus.id,
            CustomStatus.is_done.is_(True),
        ).label("bugs_closed"),
        func.avg(
            extract("epoch", Task.completed_at - Task.created_at) / 3600
        ).filter(
            Task.type == TaskType.bug,
            Task.completed_at.is_not(None),
            Task.custom_status_id == CustomStatus.id,
            CustomStatus.is_done.is_(True),
        ).label("bug_mttr"),
    ).join(Task, User.id == Task.assignee_id, isouter=True).outerjoin(
        CustomStatus, Task.custom_status_id == CustomStatus.id
    )

    if sub_team:
        base = base.join(Project, Task.project_id == Project.id, isouter=True).where(
            Project.sub_team_id == sub_team.id
        )

    base = base.group_by(User.id)
    rows = (await db.execute(base)).all()

    scorecards = []
    total_active = 0
    total_completed = 0
    cycle_times = []
    total_bugs = 0

    for row in rows:
        on_time_pct = (
            (row.on_time_count / row.total_with_due * 100)
            if row.total_with_due
            else 100.0
        )
        ws = _score_workload(row.active_tasks)
        vs = _score_velocity(row.completed_30d)
        cs = _score_cycle_time(row.avg_cycle_time)
        ots = _score_on_time(on_time_pct)
        ds = _score_defects(row.bug_mttr)

        kpi_score = round(
            ws * weights.workload_weight / 100
            + vs * weights.velocity_weight / 100
            + cs * weights.cycle_time_weight / 100
            + ots * weights.on_time_weight / 100
            + ds * weights.defect_weight / 100
        )

        reasons = []
        if ws < 70:
            reasons.append(KPIReason(label="High workload", severity="warning" if ws == 70 else "critical"))
        if vs < 70:
            reasons.append(KPIReason(label="Low velocity", severity="warning" if vs == 70 else "critical"))
        if cs < 70:
            reasons.append(KPIReason(label="Slow cycle time", severity="warning" if cs == 70 else "critical"))
        if ots < 70:
            reasons.append(KPIReason(label="Low on-time rate", severity="warning"))
        if ds < 70:
            reasons.append(KPIReason(label="High bug MTTR", severity="warning" if ds == 70 else "critical"))

        trend = "stable"
        if kpi_score >= 80:
            trend = "up"
        elif kpi_score < 60:
            trend = "down"

        scorecards.append(KPIMemberScorecard(
            user_id=row.id,
            full_name=row.full_name,
            avatar_url=row.avatar_url,
            kpi_score=kpi_score,
            trend=trend,
            reasons=reasons,
            breakdown=KPIScoreBreakdown(
                workload=ws,
                velocity=vs,
                cycle_time=cs,
                on_time=ots,
                defects=ds,
            ),
        ))

        total_active += row.active_tasks
        total_completed += row.completed_30d
        if row.avg_cycle_time is not None:
            cycle_times.append(row.avg_cycle_time)
        total_bugs += row.bugs_closed or 0

    needs_attention = [s for s in scorecards if s.kpi_score < 70 or any(r.severity == "critical" for r in s.reasons)]
    avg_score = round(sum(s.kpi_score for s in scorecards) / len(scorecards)) if scorecards else 0
    avg_cycle = round(sum(cycle_times) / len(cycle_times), 1) if cycle_times else None

    await db.commit()
    return KPIOverviewResponse(
        scorecards=scorecards,
        needs_attention=needs_attention,
        summary=KPIOverviewSummary(
            average_score=avg_score,
            active_tasks=total_active,
            completed_tasks=total_completed,
            average_cycle_time_hours=avg_cycle,
            defect_count=total_bugs,
        ),
        weights=weights,
    )


# ── KPI sprint ─────────────────────────────────────────────────────────────────


@router.get("/kpi/sprint", response_model=KPISprintResponse)
async def get_kpi_sprint(
    sprint_id: Optional[int] = None,
    project_id: Optional[int] = None,
    member_id: Optional[int] = None,
    task_type: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    # Last 6 sprints for velocity
    sprints_stmt = select(Sprint).order_by(desc(Sprint.start_date)).limit(6)
    sprints = (await db.execute(sprints_stmt)).scalars().all()
    sprint_ids = [s.id for s in sprints]

    # Velocity: completed tasks per member per sprint
    vel_stmt = select(
        Task.sprint_id,
        User.full_name,
        func.count(Task.id).label("count"),
    ).join(User, Task.assignee_id == User.id).outerjoin(
        CustomStatus, Task.custom_status_id == CustomStatus.id
    ).where(
        Task.sprint_id.in_(sprint_ids),
        Task.completed_at.is_not(None),
        CustomStatus.is_done.is_(True),
    )
    if sub_team:
        vel_stmt = vel_stmt.join(Project, Task.project_id == Project.id).where(
            Project.sub_team_id == sub_team.id
        )
    if member_id:
        vel_stmt = vel_stmt.where(Task.assignee_id == member_id)
    if project_id:
        vel_stmt = vel_stmt.where(Task.project_id == project_id)
    vel_stmt = vel_stmt.group_by(Task.sprint_id, User.full_name)
    vel_rows = (await db.execute(vel_stmt)).all()

    # Group velocity by member
    vel_by_member: dict = {}
    sprint_label_map = {s.id: s.name for s in sprints}
    for row in vel_rows:
        name = row.full_name
        if name not in vel_by_member:
            vel_by_member[name] = {}
        vel_by_member[name][row.sprint_id] = row.count

    velocity_series = [
        KPIChartSeries(
            name=name,
            points=[
                KPIChartPoint(
                    label=sprint_label_map.get(sid, str(sid)),
                    value=counts.get(sid, 0),
                )
                for sid in sprint_ids
            ],
        )
        for name, counts in vel_by_member.items()
    ]

    # Burndown for selected or most recent active sprint
    target_sprint = None
    if sprint_id:
        sr = await db.execute(select(Sprint).where(Sprint.id == sprint_id))
        target_sprint = sr.scalar_one_or_none()
    if not target_sprint:
        active_r = await db.execute(
            select(Sprint)
            .where(Sprint.status.in_([SprintStatus.active, SprintStatus.closed]))
            .order_by(desc(Sprint.start_date))
            .limit(1)
        )
        target_sprint = active_r.scalar_one_or_none()

    burndown_series = []
    if target_sprint and target_sprint.start_date and target_sprint.end_date:
        s_start = target_sprint.start_date.date()
        s_end = target_sprint.end_date.date()
        total_tasks_r = await db.execute(
            select(func.count(Task.id)).where(Task.sprint_id == target_sprint.id)
        )
        total_tasks = total_tasks_r.scalar() or 0
        points = []
        day = s_start
        while day <= s_end:
            remaining_r = await db.execute(
                select(func.count(Task.id)).where(
                    Task.sprint_id == target_sprint.id,
                    (Task.completed_at.is_(None)) | (func.date(Task.completed_at) > day),
                )
            )
            remaining = remaining_r.scalar() or 0
            points.append(KPIChartPoint(label=str(day), value=remaining))
            day = day + timedelta(days=1)
        burndown_series = [KPIChartSeries(name="Remaining", points=points)]

    # Filter options
    all_sprints = (await db.execute(select(Sprint).order_by(desc(Sprint.start_date)).limit(20))).scalars().all()
    filter_options = KPIFilterOptions(
        sprints=[{"id": s.id, "name": s.name} for s in all_sprints],
    )

    return KPISprintResponse(
        velocity_series=velocity_series,
        burndown_series=burndown_series,
        filter_options=filter_options,
    )


# ── KPI quality ────────────────────────────────────────────────────────────────


@router.get("/kpi/quality", response_model=KPIQualityResponse)
async def get_kpi_quality(
    project_id: Optional[int] = None,
    member_id: Optional[int] = None,
    task_type: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    date_start = start or (now - timedelta(days=30))
    date_end = end or now

    bug_base = select(
        func.date(Task.created_at).label("date"),
        func.count(Task.id).label("reported"),
    ).where(
        Task.type == TaskType.bug,
        Task.created_at >= date_start,
        Task.created_at <= date_end,
    )
    if sub_team:
        bug_base = bug_base.join(Project, Task.project_id == Project.id).where(
            Project.sub_team_id == sub_team.id
        )
    if member_id:
        bug_base = bug_base.where(Task.assignee_id == member_id)
    if project_id:
        bug_base = bug_base.where(Task.project_id == project_id)
    bug_base = bug_base.group_by(func.date(Task.created_at)).order_by(func.date(Task.created_at))
    bug_rows = (await db.execute(bug_base)).all()

    resolved_base = select(
        func.date(Task.completed_at).label("date"),
        func.count(Task.id).label("resolved"),
    ).outerjoin(CustomStatus, Task.custom_status_id == CustomStatus.id).where(
        Task.type == TaskType.bug,
        Task.completed_at.is_not(None),
        CustomStatus.is_done.is_(True),
        Task.completed_at >= date_start,
        Task.completed_at <= date_end,
    )
    if sub_team:
        resolved_base = resolved_base.join(Project, Task.project_id == Project.id).where(
            Project.sub_team_id == sub_team.id
        )
    if member_id:
        resolved_base = resolved_base.where(Task.assignee_id == member_id)
    if project_id:
        resolved_base = resolved_base.where(Task.project_id == project_id)
    resolved_base = resolved_base.group_by(func.date(Task.completed_at)).order_by(func.date(Task.completed_at))
    resolved_rows = (await db.execute(resolved_base)).all()

    bugs_series = [
        KPIChartSeries(
            name="Reported",
            points=[KPIChartPoint(label=str(r.date), value=r.reported) for r in bug_rows],
        ),
        KPIChartSeries(
            name="Resolved",
            points=[KPIChartPoint(label=str(r.date), value=r.resolved) for r in resolved_rows],
        ),
    ]

    # MTTR by member
    mttr_stmt = select(
        User.full_name,
        func.avg(
            extract("epoch", Task.completed_at - Task.created_at) / 3600
        ).label("mttr"),
    ).join(User, Task.assignee_id == User.id).outerjoin(
        CustomStatus, Task.custom_status_id == CustomStatus.id
    ).where(
        Task.type == TaskType.bug,
        Task.completed_at.is_not(None),
        CustomStatus.is_done.is_(True),
        Task.completed_at >= date_start,
        Task.completed_at <= date_end,
    )
    if sub_team:
        mttr_stmt = mttr_stmt.join(Project, Task.project_id == Project.id).where(
            Project.sub_team_id == sub_team.id
        )
    if member_id:
        mttr_stmt = mttr_stmt.where(Task.assignee_id == member_id)
    mttr_stmt = mttr_stmt.group_by(User.full_name)
    mttr_rows = (await db.execute(mttr_stmt)).all()

    mttr_series = [KPIChartSeries(
        name="MTTR (hours)",
        points=[KPIChartPoint(label=r.full_name, value=round(r.mttr or 0, 1)) for r in mttr_rows],
    )]

    return KPIQualityResponse(
        bugs_series=bugs_series,
        mttr_series=mttr_series,
        filter_options=KPIFilterOptions(),
    )


# ── KPI members ────────────────────────────────────────────────────────────────


@router.get("/kpi/members", response_model=KPIMembersResponse)
async def get_kpi_members(
    project_id: Optional[int] = None,
    member_id: Optional[int] = None,
    task_type: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    eight_weeks_ago = now - timedelta(weeks=8)
    three_months_ago = now - timedelta(days=90)
    tp_start = start or eight_weeks_ago
    tp_end = end or now
    ct_start = start or three_months_ago
    ct_end = end or now

    # Throughput by member and task type
    tp_stmt = select(
        User.full_name,
        Task.type,
        func.count(Task.id).label("count"),
    ).join(User, Task.assignee_id == User.id).outerjoin(
        CustomStatus, Task.custom_status_id == CustomStatus.id
    ).where(
        Task.completed_at.is_not(None),
        CustomStatus.is_done.is_(True),
        Task.completed_at >= tp_start,
        Task.completed_at <= tp_end,
    )
    if sub_team:
        tp_stmt = tp_stmt.join(Project, Task.project_id == Project.id).where(
            Project.sub_team_id == sub_team.id
        )
    if member_id:
        tp_stmt = tp_stmt.where(Task.assignee_id == member_id)
    if project_id:
        tp_stmt = tp_stmt.where(Task.project_id == project_id)
    if task_type:
        tp_stmt = tp_stmt.where(Task.type == task_type)
    tp_stmt = tp_stmt.group_by(User.full_name, Task.type)
    tp_rows = (await db.execute(tp_stmt)).all()

    tp_by_type: dict = {}
    for row in tp_rows:
        t = str(row.type.value) if row.type else "unknown"
        if t not in tp_by_type:
            tp_by_type[t] = {}
        tp_by_type[t][row.full_name] = row.count

    all_members = list({r.full_name for r in tp_rows})
    throughput_series = [
        KPIChartSeries(
            name=t,
            points=[KPIChartPoint(label=m, value=counts.get(m, 0)) for m in all_members],
        )
        for t, counts in tp_by_type.items()
    ]

    # Cycle time by task type
    ct_stmt = select(
        Task.type,
        func.avg(
            extract("epoch", Task.completed_at - Task.created_at) / 3600
        ).label("avg_hours"),
    ).outerjoin(CustomStatus, Task.custom_status_id == CustomStatus.id).where(
        Task.completed_at.is_not(None),
        CustomStatus.is_done.is_(True),
        Task.completed_at >= ct_start,
        Task.completed_at <= ct_end,
    )
    if sub_team:
        ct_stmt = ct_stmt.join(Project, Task.project_id == Project.id).where(
            Project.sub_team_id == sub_team.id
        )
    if member_id:
        ct_stmt = ct_stmt.where(Task.assignee_id == member_id)
    ct_stmt = ct_stmt.group_by(Task.type)
    ct_rows = (await db.execute(ct_stmt)).all()

    cycle_time_series = [KPIChartSeries(
        name="Cycle Time (hours)",
        points=[KPIChartPoint(label=str(r.type.value) if r.type else "unknown", value=round(r.avg_hours or 0, 1)) for r in ct_rows],
    )]

    return KPIMembersResponse(
        throughput_series=throughput_series,
        cycle_time_series=cycle_time_series,
        filter_options=KPIFilterOptions(),
    )


# ── KPI drilldown ──────────────────────────────────────────────────────────────


@router.get("/kpi/drilldown", response_model=KPIDrilldownResponse)
async def get_kpi_drilldown(
    metric: str,
    sprint_id: Optional[int] = None,
    project_id: Optional[int] = None,
    member_id: Optional[int] = None,
    task_type: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_supervisor),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    stmt = (
        select(
            Task.id,
            Task.title,
            Task.type,
            Task.created_at,
            Task.completed_at,
            User.full_name.label("assignee"),
            Project.name.label("project"),
            Sprint.name.label("sprint"),
            CustomStatus.name.label("status"),
        )
        .outerjoin(User, Task.assignee_id == User.id)
        .join(Project, Task.project_id == Project.id)
        .outerjoin(Sprint, Task.sprint_id == Sprint.id)
        .outerjoin(CustomStatus, Task.custom_status_id == CustomStatus.id)
    )

    if sub_team:
        stmt = stmt.where(Project.sub_team_id == sub_team.id)
    if member_id:
        stmt = stmt.where(Task.assignee_id == member_id)
    if project_id:
        stmt = stmt.where(Task.project_id == project_id)
    if sprint_id:
        stmt = stmt.where(Task.sprint_id == sprint_id)
    if task_type:
        stmt = stmt.where(Task.type == task_type)
    if start:
        stmt = stmt.where(Task.created_at >= start)
    if end:
        stmt = stmt.where(Task.created_at <= end)

    stmt = stmt.order_by(desc(Task.created_at)).limit(200)
    rows = (await db.execute(stmt)).all()

    tasks = [
        KPIDrilldownTask(
            id=r.id,
            title=r.title,
            task_type=str(r.type.value) if r.type else None,
            assignee=r.assignee,
            project=r.project,
            sprint=r.sprint,
            status=r.status,
            created_at=r.created_at,
            completed_at=r.completed_at,
        )
        for r in rows
    ]

    return KPIDrilldownResponse(tasks=tasks, total=len(tasks))
