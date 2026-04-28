from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import inspect as sa_inspect, select

from app.utils.auth import create_access_token, hash_password
from app.models import (
    EventNotification,
    KnowledgeSession,
    NotificationEventType,
    NotificationStatus,
    SubTeam,
    User,
    UserRole,
)


def _auth_headers(user: User) -> dict[str, str]:
    token = create_access_token({"sub": str(sa_inspect(user).identity[0])})
    return {"Authorization": f"Bearer {token}"}


async def _create_user(
    db_session,
    *,
    email: str,
    username: str,
    full_name: str,
    role: UserRole,
    sub_team_id: int | None,
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


async def _build_graph(db_session):
    alpha = SubTeam(name="Alpha Team", supervisor_id=None)
    beta = SubTeam(name="Beta Team", supervisor_id=None)
    db_session.add_all([alpha, beta])
    await db_session.commit()
    await db_session.refresh(alpha)
    await db_session.refresh(beta)

    admin = await _create_user(
        db_session,
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        role=UserRole.admin,
        sub_team_id=None,
    )
    supervisor_alpha = await _create_user(
        db_session,
        email="alpha-lead@example.com",
        username="alpha-lead",
        full_name="Alpha Lead",
        role=UserRole.supervisor,
        sub_team_id=alpha.id,
    )
    supervisor_beta = await _create_user(
        db_session,
        email="beta-lead@example.com",
        username="beta-lead",
        full_name="Beta Lead",
        role=UserRole.supervisor,
        sub_team_id=beta.id,
    )
    member_alpha = await _create_user(
        db_session,
        email="alpha-member@example.com",
        username="alpha-member",
        full_name="Alpha Member",
        role=UserRole.member,
        sub_team_id=alpha.id,
    )
    member_beta = await _create_user(
        db_session,
        email="beta-member@example.com",
        username="beta-member",
        full_name="Beta Member",
        role=UserRole.member,
        sub_team_id=beta.id,
    )

    alpha.supervisor_id = supervisor_alpha.id
    beta.supervisor_id = supervisor_beta.id
    db_session.add_all([alpha, beta])
    await db_session.commit()
    await db_session.refresh(alpha)
    await db_session.refresh(beta)

    return {
        "admin": admin,
        "alpha": alpha,
        "beta": beta,
        "supervisor_alpha": supervisor_alpha,
        "supervisor_beta": supervisor_beta,
        "member_alpha": member_alpha,
        "member_beta": member_beta,
    }


def _session_payload(
    *,
    topic: str,
    start_time: datetime,
    duration_minutes: int = 60,
    presenter_id: int | None = None,
    tags: list[str] | None = None,
    offset_minutes_list: list[int] | None = None,
    session_type: str = "presentation",
):
    payload = {
        "topic": topic,
        "description": f"{topic} description",
        "references": "https://example.com/notes",
        "session_type": session_type,
        "duration_minutes": duration_minutes,
        "start_time": start_time.isoformat(),
        "tags": tags or [],
        "offset_minutes_list": offset_minutes_list or [],
    }
    if presenter_id is not None:
        payload["presenter_id"] = presenter_id
    return payload


@pytest.mark.asyncio
async def test_admin_org_wide_session_defaults_presenter_and_notifies_scope(
    async_client: AsyncClient, db_session
):
    graph = await _build_graph(db_session)
    headers = _auth_headers(graph["admin"])

    response = await async_client.post(
        "/api/knowledge-sessions/",
        json=_session_payload(
            topic="Org Wide Kickoff",
            start_time=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=2),
            tags=["Alpha", "alpha", "Beta"],
        ),
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["presenter_id"] == graph["admin"].id
    assert data["created_by_id"] == graph["admin"].id
    assert data["sub_team_id"] is None
    assert data["tags"] == ["Alpha", "Beta"]

    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.event_type == NotificationEventType.knowledge_session,
            EventNotification.event_ref_id == data["id"],
        )
    )
    rows = result.scalars().all()
    assert len(rows) == 5
    assert {row.status for row in rows} == {NotificationStatus.sent}
    assert {row.user_id for row in rows} == {
        graph["admin"].id,
        graph["supervisor_alpha"].id,
        graph["supervisor_beta"].id,
        graph["member_alpha"].id,
        graph["member_beta"].id,
    }


@pytest.mark.asyncio
async def test_supervisor_session_scoped_to_sub_team_and_rejects_foreign_presenter(
    async_client: AsyncClient, db_session
):
    graph = await _build_graph(db_session)
    headers = _auth_headers(graph["supervisor_alpha"])

    response = await async_client.post(
        "/api/knowledge-sessions/",
        json=_session_payload(
            topic="Alpha Workshop",
            start_time=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=3),
            presenter_id=graph["supervisor_alpha"].id,
            offset_minutes_list=[15, 30],
        ),
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["sub_team_id"] == graph["alpha"].id
    assert data["presenter_id"] == graph["supervisor_alpha"].id

    response = await async_client.post(
        "/api/knowledge-sessions/",
        json=_session_payload(
            topic="Invalid Presenter",
            start_time=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=4),
            presenter_id=graph["member_beta"].id,
        ),
        headers=headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_member_visibility_excludes_sibling_sessions(
    async_client: AsyncClient, db_session
):
    graph = await _build_graph(db_session)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    org_session = KnowledgeSession(
        topic="Org Session",
        description="d",
        references=None,
        session_type="presentation",
        start_time=now + timedelta(days=2),
        duration_minutes=60,
        tags=None,
        presenter_id=graph["admin"].id,
        sub_team_id=None,
        created_by_id=graph["admin"].id,
    )
    alpha_session = KnowledgeSession(
        topic="Alpha Sync",
        description="d",
        references=None,
        session_type="presentation",
        start_time=now + timedelta(days=3),
        duration_minutes=60,
        tags=None,
        presenter_id=graph["supervisor_alpha"].id,
        sub_team_id=graph["alpha"].id,
        created_by_id=graph["supervisor_alpha"].id,
    )
    beta_session = KnowledgeSession(
        topic="Beta Sync",
        description="d",
        references=None,
        session_type="presentation",
        start_time=now + timedelta(days=4),
        duration_minutes=60,
        tags=None,
        presenter_id=graph["supervisor_beta"].id,
        sub_team_id=graph["beta"].id,
        created_by_id=graph["supervisor_beta"].id,
    )
    db_session.add_all([org_session, alpha_session, beta_session])
    await db_session.commit()
    await db_session.refresh(org_session)
    await db_session.refresh(alpha_session)
    await db_session.refresh(beta_session)

    member_headers = _auth_headers(graph["member_alpha"])

    response = await async_client.get("/api/knowledge-sessions/", headers=member_headers)
    assert response.status_code == 200
    sessions = response.json()
    assert [session["topic"] for session in sessions] == ["Org Session", "Alpha Sync"]

    response = await async_client.get(
        f"/api/knowledge-sessions/{beta_session.id}", headers=member_headers
    )
    assert response.status_code == 404

    response = await async_client.get(
        "/api/knowledge-sessions/", headers=_auth_headers(graph["admin"])
    )
    assert response.status_code == 200
    assert {session["topic"] for session in response.json()} == {
        "Org Session",
        "Alpha Sync",
        "Beta Sync",
    }


@pytest.mark.asyncio
async def test_creation_notifications_and_reminder_replacement(
    async_client: AsyncClient, db_session
):
    graph = await _build_graph(db_session)
    headers = _auth_headers(graph["supervisor_alpha"])

    start_time = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=5)
    response = await async_client.post(
        "/api/knowledge-sessions/",
        json=_session_payload(
            topic="Reminder Planning",
            start_time=start_time,
            offset_minutes_list=[15, 30],
        ),
        headers=headers,
    )
    assert response.status_code == 201
    session_id = response.json()["id"]

    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.event_type == NotificationEventType.knowledge_session,
            EventNotification.event_ref_id == session_id,
        )
    )
    rows = result.scalars().all()
    creation_rows = [row for row in rows if row.offset_minutes == 0]
    reminder_rows = [row for row in rows if row.offset_minutes in {15, 30}]
    assert len(creation_rows) == 2
    assert {row.status for row in creation_rows} == {NotificationStatus.sent}
    assert len(reminder_rows) == 4
    assert {row.status for row in reminder_rows} == {NotificationStatus.pending}

    response = await async_client.patch(
        f"/api/knowledge-sessions/{session_id}",
        json={
            "offset_minutes_list": [10],
        },
        headers=headers,
    )
    assert response.status_code == 200

    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.event_type == NotificationEventType.knowledge_session,
            EventNotification.event_ref_id == session_id,
        )
    )
    rows = result.scalars().all()
    creation_rows = [row for row in rows if row.offset_minutes == 0]
    reminder_rows = [row for row in rows if row.offset_minutes == 10]
    assert len(creation_rows) == 2
    assert len(reminder_rows) == 2
    assert {row.status for row in reminder_rows} == {NotificationStatus.pending}


@pytest.mark.asyncio
async def test_notification_resolver_honors_session_scope(
    async_client: AsyncClient, db_session
):
    graph = await _build_graph(db_session)
    headers = _auth_headers(graph["supervisor_alpha"])

    response = await async_client.post(
        "/api/knowledge-sessions/",
        json=_session_payload(
            topic="Resolver Check",
            start_time=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=3),
            offset_minutes_list=[15],
        ),
        headers=headers,
    )
    assert response.status_code == 201
    session_id = response.json()["id"]

    visible_headers = _auth_headers(graph["member_alpha"])
    response = await async_client.get(
        "/api/notifications/by-event",
        params={"event_type": "knowledge_session", "event_ref_id": session_id},
        headers=visible_headers,
    )
    assert response.status_code == 200
    items = response.json()
    assert items
    assert all(item["event_type"] == "knowledge_session" for item in items)

    hidden_headers = _auth_headers(graph["member_beta"])
    response = await async_client.get(
        "/api/notifications/by-event",
        params={"event_type": "knowledge_session", "event_ref_id": session_id},
        headers=hidden_headers,
    )
    assert response.status_code in (403, 404)
