from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CustomStatus, KPIWeightSettings, Project, SubTeam, Task, TaskType, User


@dataclass
class KpiPerMemberData:
    user_id: int
    full_name: str
    avatar_url: Optional[str]
    active_tasks: int
    completed_30d: int
    overdue_tasks: int
    kpi_score: int


@dataclass
class KpiComputeResult:
    scorecards: list  # list of KPIMemberScorecard
    per_member: list  # list of KpiPerMemberData
    avg_score: int
    needs_attention_count: int
    completion_rate: float


def score_workload(active_tasks: int) -> int:
    if active_tasks <= 7:
        return 100
    elif active_tasks <= 10:
        return 70
    return 40


def score_velocity(completed_30d: int) -> int:
    return min(100, completed_30d * 10)


def score_cycle_time(avg_hours: Optional[float]) -> int:
    if avg_hours is None:
        return 40
    if avg_hours <= 48:
        return 100
    elif avg_hours <= 120:
        return 70
    return 40


def score_on_time(on_time_pct: float) -> int:
    return round(on_time_pct)


def score_defects(mttr_hours: Optional[float]) -> int:
    if mttr_hours is None:
        return 100
    if mttr_hours <= 72:
        return 100
    elif mttr_hours <= 168:
        return 70
    return 40


def completed_task_filter():
    return [
        Task.completed_at.is_not(None),
        Task.custom_status_id == CustomStatus.id,
        CustomStatus.is_done.is_(True),
    ]


def active_task_filter():
    return [
        Task.custom_status_id == CustomStatus.id,
        CustomStatus.is_done.is_(False),
    ]


async def get_or_create_kpi_weights(
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


async def compute_kpi_overview(
    db: AsyncSession, sub_team: Optional[SubTeam]
) -> KpiComputeResult:
    from app.schemas.kpi import (
        KPIOverviewSummary,
        KPIReason,
        KPIMemberScorecard,
        KPIScoreBreakdown,
    )

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    thirty_days_ago = now - timedelta(days=30)

    weights = await get_or_create_kpi_weights(db, sub_team)

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
        # NEW: overdue_tasks aggregate
        func.count(Task.id).filter(
            Task.due_date < now,
            Task.custom_status_id == CustomStatus.id,
            CustomStatus.is_done.is_(False),
        ).label("overdue_tasks"),
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
    per_member_data = []
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
        ws = score_workload(row.active_tasks)
        vs = score_velocity(row.completed_30d)
        cs = score_cycle_time(row.avg_cycle_time)
        ots = score_on_time(on_time_pct)
        ds = score_defects(row.bug_mttr)

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

        # NEW: Build per_member data with overdue_tasks
        per_member_data.append(KpiPerMemberData(
            user_id=row.id,
            full_name=row.full_name,
            avatar_url=row.avatar_url,
            active_tasks=row.active_tasks,
            completed_30d=row.completed_30d,
            overdue_tasks=row.overdue_tasks or 0,
            kpi_score=kpi_score,
        ))

        total_active += row.active_tasks
        total_completed += row.completed_30d
        if row.avg_cycle_time is not None:
            cycle_times.append(row.avg_cycle_time)
        total_bugs += row.bugs_closed or 0

    needs_attention = [s for s in scorecards if s.kpi_score < 70 or any(r.severity == "critical" for r in s.reasons)]
    avg_score = round(sum(s.kpi_score for s in scorecards) / len(scorecards)) if scorecards else 0
    avg_cycle = round(sum(cycle_times) / len(cycle_times), 1) if cycle_times else None

    # NEW: Compute completion_rate
    total_active_sum = sum(m.active_tasks for m in per_member_data)
    total_completed_sum = sum(m.completed_30d for m in per_member_data)
    completion_rate = total_completed_sum / (total_active_sum + total_completed_sum) if (total_active_sum + total_completed_sum) > 0 else 0.0

    return KpiComputeResult(
        scorecards=scorecards,
        per_member=per_member_data,
        avg_score=avg_score,
        needs_attention_count=len(needs_attention),
        completion_rate=round(completion_rate, 4),
    )
