import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.utils.auth import hash_password
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


async def _login(async_client: AsyncClient, username: str, password: str) -> str:
    response = await async_client.post(
        "/api/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


async def _create_user(
    db_session,
    *,
    email: str,
    username: str,
    full_name: str,
    role: UserRole,
    sub_team_id: int | None = None,
) -> User:
    user = User(
        email=email,
        username=username,
        full_name=full_name,
        hashed_password=hash_password("password"),
        role=role,
        sub_team_id=sub_team_id,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_reminder_settings_current_default_and_member_read_only(
    async_client: AsyncClient, db_session, sub_team
):
    member = await _create_user(
        db_session,
        email="member@example.com",
        username="member",
        full_name="Member User",
        role=UserRole.member,
        sub_team_id=sub_team.id,
    )
    token = await _login(async_client, member.username, "password")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get("/api/sub-teams/reminder-settings/current", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["sub_team_id"] == sub_team.id
    assert data["lead_time_days"] == 2
    assert data["sprint_reminders_enabled"] is True
    assert data["milestone_reminders_enabled"] is True

    response = await async_client.patch(
        "/api/sub-teams/reminder-settings/current",
        json={"lead_time_days": 4},
        headers=headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_supervisor_proposal_creates_pending_notification_and_preserves_settings(
    async_client: AsyncClient, db_session, sub_team
):
    supervisor = await _create_user(
        db_session,
        email="supervisor@example.com",
        username="supervisor",
        full_name="Supervisor User",
        role=UserRole.supervisor,
        sub_team_id=sub_team.id,
    )
    sub_team.supervisor_id = supervisor.id
    db_session.add(sub_team)
    await db_session.commit()
    manager = await _create_user(
        db_session,
        email="manager@example.com",
        username="manager",
        full_name="Manager User",
        role=UserRole.manager,
    )

    token = await _login(async_client, supervisor.username, "password")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.post(
        "/api/sub-teams/reminder-settings/proposals",
        json={
            "lead_time_days": 5,
            "sprint_reminders_enabled": False,
            "milestone_reminders_enabled": True,
        },
        headers=headers,
    )
    assert response.status_code == 201
    proposal = response.json()
    assert proposal["sub_team_id"] == sub_team.id
    assert proposal["status"] == "pending"

    result = await db_session.execute(
        select(ReminderSettingsProposal).where(ReminderSettingsProposal.id == proposal["id"])
    )
    db_proposal = result.scalar_one_or_none()
    assert db_proposal is not None
    assert db_proposal.status == ReminderProposalStatus.pending

    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.user_id == manager.id,
            EventNotification.event_type == NotificationEventType.reminder_settings_proposal,
            EventNotification.event_ref_id == proposal["id"],
            EventNotification.status == NotificationStatus.pending,
        )
    )
    notifications = result.scalars().all()
    assert len(notifications) == 1
    assert "/team" in notifications[0].title_cache

    response = await async_client.get("/api/sub-teams/reminder-settings/current", headers=headers)
    assert response.status_code == 200
    current = response.json()
    assert current["lead_time_days"] == 2
    assert current["sprint_reminders_enabled"] is True
    assert current["milestone_reminders_enabled"] is True


@pytest.mark.asyncio
async def test_manager_can_update_and_approve_reminder_settings(
    async_client: AsyncClient, db_session, sub_team
):
    manager = await _create_user(
        db_session,
        email="manager2@example.com",
        username="manager2",
        full_name="Manager User",
        role=UserRole.manager,
    )
    supervisor = await _create_user(
        db_session,
        email="supervisor2@example.com",
        username="supervisor2",
        full_name="Supervisor User",
        role=UserRole.supervisor,
        sub_team_id=sub_team.id,
    )
    sub_team.supervisor_id = supervisor.id
    db_session.add(sub_team)
    await db_session.commit()

    manager_token = await _login(async_client, manager.username, "password")
    manager_headers = {
        "Authorization": f"Bearer {manager_token}",
        "X-SubTeam-ID": str(sub_team.id),
    }

    response = await async_client.patch(
        "/api/sub-teams/reminder-settings/current",
        json={"lead_time_days": 3, "sprint_reminders_enabled": False},
        headers=manager_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["lead_time_days"] == 3
    assert data["sprint_reminders_enabled"] is False
    assert data["milestone_reminders_enabled"] is True

    supervisor_token = await _login(async_client, supervisor.username, "password")
    supervisor_headers = {"Authorization": f"Bearer {supervisor_token}"}
    response = await async_client.post(
        "/api/sub-teams/reminder-settings/proposals",
        json={"milestone_reminders_enabled": False},
        headers=supervisor_headers,
    )
    print("RESPONSE:", response.json())
    assert response.status_code == 201
    proposal_id = response.json()["id"]

    async_client.cookies.clear()
    response = await async_client.post(
        f"/api/sub-teams/reminder-settings/proposals/{proposal_id}/review",
        json={"decision": "approve"},
        headers=manager_headers,
    )
    if response.status_code != 200:
        print("REVIEW RESPONSE:", response.json())
    assert response.status_code == 200
    reviewed = response.json()
    assert reviewed["status"] == "approved"

    response = await async_client.get(
        "/api/sub-teams/reminder-settings/current",
        headers=manager_headers,
    )
    assert response.status_code == 200
    current = response.json()
    assert current["lead_time_days"] == 3
    assert current["sprint_reminders_enabled"] is False
    assert current["milestone_reminders_enabled"] is False


@pytest.mark.asyncio
async def test_leaders_list_only_allowed_sub_teams_and_manager_lists_all(
    async_client: AsyncClient, db_session
):
    alpha = SubTeam(name="Alpha", supervisor_id=None)
    beta = SubTeam(name="Beta", supervisor_id=None)
    db_session.add_all([alpha, beta])
    await db_session.flush()

    manager = await _create_user(
        db_session,
        email="team.manager@example.com",
        username="team_manager",
        full_name="Team Manager",
        role=UserRole.manager,
    )
    assistant = await _create_user(
        db_session,
        email="assistant@example.com",
        username="assistant",
        full_name="Assistant Manager",
        role=UserRole.assistant_manager,
        sub_team_id=alpha.id,
    )
    supervisor = await _create_user(
        db_session,
        email="beta.lead@example.com",
        username="beta_lead",
        full_name="Beta Lead",
        role=UserRole.supervisor,
        sub_team_id=beta.id,
    )
    beta.supervisor_id = supervisor.id
    db_session.add(beta)
    await db_session.commit()

    assistant_token = await _login(async_client, assistant.username, "password")
    response = await async_client.get(
        "/api/sub-teams/",
        headers={"Authorization": f"Bearer {assistant_token}"},
    )
    assert response.status_code == 200
    assert [team["name"] for team in response.json()] == ["Alpha"]

    manager_token = await _login(async_client, manager.username, "password")
    response = await async_client.get(
        "/api/sub-teams/",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert response.status_code == 200
    assert {team["name"] for team in response.json()} == {"Alpha", "Beta"}


@pytest.mark.asyncio
async def test_only_manager_can_create_update_and_delete_sub_teams(
    async_client: AsyncClient, db_session, sub_team
):
    manager = await _create_user(
        db_session,
        email="mut.manager@example.com",
        username="mut_manager",
        full_name="Mutation Manager",
        role=UserRole.manager,
    )
    assistant = await _create_user(
        db_session,
        email="mut.assistant@example.com",
        username="mut_assistant",
        full_name="Mutation Assistant",
        role=UserRole.assistant_manager,
        sub_team_id=sub_team.id,
    )
    manager_username = manager.username
    assistant_username = assistant.username

    assistant_token = await _login(async_client, assistant_username, "password")
    assistant_headers = {"Authorization": f"Bearer {assistant_token}"}
    response = await async_client.post(
        "/api/sub-teams/",
        json={"name": "Created By Assistant"},
        headers=assistant_headers,
    )
    assert response.status_code == 403

    manager_token = await _login(async_client, manager_username, "password")
    manager_headers = {"Authorization": f"Bearer {manager_token}"}
    response = await async_client.post(
        "/api/sub-teams/",
        json={"name": "Created By Manager"},
        headers=manager_headers,
    )
    assert response.status_code == 201
    created_id = response.json()["id"]

    response = await async_client.put(
        f"/api/sub-teams/{created_id}",
        json={"name": "Updated By Manager"},
        headers=manager_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated By Manager"

    response = await async_client.delete(
        f"/api/sub-teams/{created_id}",
        headers=manager_headers,
    )
    assert response.status_code == 204
