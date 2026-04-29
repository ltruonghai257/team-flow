from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.auth import (
    get_current_user,
    get_sub_team,
    require_leader_or_manager,
    require_manager,
)
from app.db.database import get_db
from app.models import (
    EventNotification,
    NotificationEventType,
    NotificationStatus,
    ReminderProposalStatus,
    ReminderSettingsProposal,
    SubTeam,
    User,
    UserRole,
)
from app.schemas import (
    ReminderSettingsOut,
    ReminderSettingsProposalCreate,
    ReminderSettingsProposalOut,
    ReminderSettingsProposalReview,
    ReminderSettingsUpdate,
    SubTeamCreate,
    SubTeamOut,
    SubTeamUpdate,
)
from app.services.reminder_notifications import get_or_create_reminder_settings
from app.services.visibility import (
    is_leader,
    is_manager,
    scoped_sub_team_filter,
    visible_sub_team_ids,
)

router = APIRouter(prefix="/api/sub-teams", tags=["sub-teams"])


def _active_sub_team_or_error(
    current_user: User, sub_team: Optional[SubTeam]
) -> SubTeam:
    if sub_team is None:
        raise HTTPException(status_code=400, detail="Active sub-team required")
    return sub_team


async def _notify_managers_of_proposal(
    db: AsyncSession, proposal: ReminderSettingsProposal
) -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    result = await db.execute(
        select(User.id).where(User.role == UserRole.manager, User.is_active.is_(True))
    )
    for (manager_id,) in result.all():
        db.add(
            EventNotification(
                user_id=manager_id,
                event_type=NotificationEventType.reminder_settings_proposal,
                event_ref_id=proposal.id,
                title_cache="Reminder settings proposal pending review on /team",
                start_at_cache=now,
                remind_at=now,
                offset_minutes=0,
                status=NotificationStatus.pending,
            )
        )


@router.get("/reminder-settings/current", response_model=ReminderSettingsOut)
async def get_reminder_settings_current(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    target_sub_team = _active_sub_team_or_error(current_user, sub_team)
    settings = await get_or_create_reminder_settings(db, target_sub_team.id)
    return settings


@router.patch("/reminder-settings/current", response_model=ReminderSettingsOut)
async def update_reminder_settings_current(
    payload: ReminderSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    if not is_manager(current_user):
        raise HTTPException(status_code=403, detail="Manager access required")
    target_sub_team = _active_sub_team_or_error(current_user, sub_team)
    settings = await get_or_create_reminder_settings(db, target_sub_team.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    await db.commit()
    await db.refresh(settings)
    return settings


@router.post("/reminder-settings/proposals", response_model=ReminderSettingsProposalOut, status_code=201)
async def create_reminder_settings_proposal(
    payload: ReminderSettingsProposalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    if not is_leader(current_user):
        raise HTTPException(status_code=403, detail="Leader access required")
    target_sub_team = _active_sub_team_or_error(current_user, sub_team)
    proposal = ReminderSettingsProposal(
        sub_team_id=target_sub_team.id,
        proposed_by_id=current_user.id,
        **payload.model_dump(),
    )
    db.add(proposal)
    await db.flush()
    await _notify_managers_of_proposal(db, proposal)
    await db.commit()
    await db.refresh(proposal)
    return proposal


@router.get("/reminder-settings/proposals", response_model=List[ReminderSettingsProposalOut])
async def list_reminder_settings_proposals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    if not is_manager(current_user):
        raise HTTPException(status_code=403, detail="Manager access required")
    target_sub_team = _active_sub_team_or_error(current_user, sub_team)
    result = await db.execute(
        select(ReminderSettingsProposal)
        .where(
            ReminderSettingsProposal.sub_team_id == target_sub_team.id,
            ReminderSettingsProposal.status == ReminderProposalStatus.pending,
        )
        .order_by(ReminderSettingsProposal.created_at.desc())
    )
    return result.scalars().all()


@router.post("/reminder-settings/proposals/{proposal_id}/review", response_model=ReminderSettingsProposalOut)
async def review_reminder_settings_proposal(
    proposal_id: int,
    payload: ReminderSettingsProposalReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    if not is_manager(current_user):
        raise HTTPException(status_code=403, detail="Manager access required")
    target_sub_team = _active_sub_team_or_error(current_user, sub_team)
    result = await db.execute(
        select(ReminderSettingsProposal).where(ReminderSettingsProposal.id == proposal_id)
    )
    proposal = result.scalar_one_or_none()
    if not proposal or proposal.sub_team_id != target_sub_team.id:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.status != ReminderProposalStatus.pending:
        raise HTTPException(status_code=409, detail="Proposal already reviewed")

    proposal.reviewed_by_id = current_user.id
    proposal.reviewed_at = datetime.now(timezone.utc).replace(tzinfo=None)

    if payload.decision == "approve":
        settings = await get_or_create_reminder_settings(db, target_sub_team.id)
        if proposal.lead_time_days is not None:
            settings.lead_time_days = proposal.lead_time_days
        if proposal.sprint_reminders_enabled is not None:
            settings.sprint_reminders_enabled = proposal.sprint_reminders_enabled
        if proposal.milestone_reminders_enabled is not None:
            settings.milestone_reminders_enabled = proposal.milestone_reminders_enabled
        proposal.status = ReminderProposalStatus.approved
    else:
        proposal.status = ReminderProposalStatus.rejected

    await db.commit()
    await db.refresh(proposal)
    return proposal


@router.post("/", response_model=SubTeamOut, status_code=201)
async def create_sub_team(
    sub_team: SubTeamCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_manager),
):
    new_sub_team = SubTeam(**sub_team.model_dump())
    db.add(new_sub_team)
    await db.commit()
    await db.refresh(new_sub_team)
    return new_sub_team


@router.get("/", response_model=List[SubTeamOut])
async def list_sub_teams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader_or_manager),
):
    allowed_ids = await visible_sub_team_ids(db, current_user)
    result = await db.execute(
        select(SubTeam).where(scoped_sub_team_filter(SubTeam.id, current_user, allowed_ids))
    )
    return result.scalars().all()


@router.put("/{sub_team_id}", response_model=SubTeamOut)
async def update_sub_team(
    sub_team_id: int,
    sub_team_update: SubTeamUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_manager),
):
    result = await db.execute(select(SubTeam).where(SubTeam.id == sub_team_id))
    sub_team = result.scalar_one_or_none()
    if not sub_team:
        raise HTTPException(status_code=404, detail="Sub-team not found")
    for field, value in sub_team_update.model_dump(exclude_unset=True).items():
        setattr(sub_team, field, value)
    await db.commit()
    await db.refresh(sub_team)
    return sub_team


@router.delete("/{sub_team_id}", status_code=204)
async def delete_sub_team(
    sub_team_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_manager),
):
    result = await db.execute(select(SubTeam).where(SubTeam.id == sub_team_id))
    sub_team = result.scalar_one_or_none()
    if not sub_team:
        raise HTTPException(status_code=404, detail="Sub-team not found")
    await db.delete(sub_team)
    await db.commit()
