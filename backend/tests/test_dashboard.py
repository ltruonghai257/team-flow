import pytest
import pytest_asyncio
from datetime import datetime, date, timedelta, timezone

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SubTeam, Task, TaskStatus, TaskPriority, User, UserRole
from app.models.updates import StandupPost
from app.utils.auth import create_access_token, hash_password


async def _make_user(db, *, email, username, role, sub_team_id=None):
    user = User(
        email=email,
        username=username,
        full_name=username.replace("_", " ").title(),
        hashed_password=hash_password("password"),
        role=role,
        sub_team_id=sub_team_id,
    )
    db.add(user)
    await db.flush()
    return user


def _token(user):
    return create_access_token({"sub": str(user.id)})


@pytest.mark.asyncio
async def test_member_dashboard_shape(
    db_session: AsyncSession, async_client: AsyncClient
):
    """D-16 member role: my_tasks and recent_activity present; team_health and kpi_summary absent (key not in response)."""
    sub_team = SubTeam(name="Test SubTeam")
    db_session.add(sub_team)
    await db_session.flush()

    member_user = await _make_user(
        db_session,
        email="member@test.com",
        username="member_user",
        role=UserRole.member,
        sub_team_id=sub_team.id,
    )
    await db_session.commit()

    token = _token(member_user)
    response = await async_client.get(
        "/api/dashboard/",
        headers={"Cookie": f"access_token={token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "my_tasks" in data
    assert "recent_activity" in data
    assert "team_health" not in data
    assert "kpi_summary" not in data
    assert isinstance(data["my_tasks"], list)
    assert isinstance(data["recent_activity"], list)


@pytest.mark.asyncio
async def test_supervisor_dashboard_shape(
    db_session: AsyncSession, async_client: AsyncClient
):
    """D-16 supervisor role: all four keys present with correct shape."""
    sub_team = SubTeam(name="Test SubTeam")
    db_session.add(sub_team)
    await db_session.flush()

    supervisor_user = await _make_user(
        db_session,
        email="supervisor@test.com",
        username="supervisor_user",
        role=UserRole.supervisor,
        sub_team_id=sub_team.id,
    )
    await db_session.commit()

    token = _token(supervisor_user)
    response = await async_client.get(
        "/api/dashboard/",
        headers={"Cookie": f"access_token={token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "my_tasks" in data
    assert "team_health" in data
    assert "kpi_summary" in data
    assert "recent_activity" in data
    assert isinstance(data["team_health"], list)
    assert isinstance(data["kpi_summary"], dict)
    assert "avg_score" in data["kpi_summary"]
    assert "completion_rate" in data["kpi_summary"]
    assert "needs_attention_count" in data["kpi_summary"]


@pytest.mark.asyncio
async def test_my_tasks_urgency_sort(
    db_session: AsyncSession, async_client: AsyncClient
):
    """D-16 my_tasks sort: overdue tasks precede upcoming tasks."""
    sub_team = SubTeam(name="Test SubTeam")
    db_session.add(sub_team)
    await db_session.flush()

    member_user = await _make_user(
        db_session,
        email="member@test.com",
        username="member_user",
        role=UserRole.member,
        sub_team_id=sub_team.id,
    )

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    task_a = Task(
        title="Overdue Task",
        status=TaskStatus.todo,
        assignee_id=member_user.id,
        due_date=(now - timedelta(days=1)).date(),
    )
    task_b = Task(
        title="Upcoming Task",
        status=TaskStatus.todo,
        assignee_id=member_user.id,
        due_date=(now + timedelta(days=3)).date(),
    )
    db_session.add_all([task_a, task_b])
    await db_session.commit()

    token = _token(member_user)
    response = await async_client.get(
        "/api/dashboard/",
        headers={"Cookie": f"access_token={token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data["my_tasks"]) == 2
    assert data["my_tasks"][0]["is_overdue"] is True
    assert data["my_tasks"][1]["is_overdue"] is False


@pytest.mark.asyncio
async def test_my_tasks_excludes_done(
    db_session: AsyncSession, async_client: AsyncClient
):
    """D-05 done exclusion: done tasks are excluded from my_tasks."""
    sub_team = SubTeam(name="Test SubTeam")
    db_session.add(sub_team)
    await db_session.flush()

    member_user = await _make_user(
        db_session,
        email="member@test.com",
        username="member_user",
        role=UserRole.member,
        sub_team_id=sub_team.id,
    )

    task_a = Task(
        title="Active Task",
        status=TaskStatus.todo,
        assignee_id=member_user.id,
    )
    task_b = Task(
        title="Done Task",
        status=TaskStatus.done,
        assignee_id=member_user.id,
    )
    db_session.add_all([task_a, task_b])
    await db_session.commit()

    token = _token(member_user)
    response = await async_client.get(
        "/api/dashboard/",
        headers={"Cookie": f"access_token={token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data["my_tasks"]) == 1
    assert data["my_tasks"][0]["title"] == "Active Task"


@pytest.mark.asyncio
async def test_recent_activity_shape(
    db_session: AsyncSession, async_client: AsyncClient
):
    """D-13 to D-15: recent_activity items have all required fields."""
    sub_team = SubTeam(name="Test SubTeam")
    db_session.add(sub_team)
    await db_session.flush()

    member_user = await _make_user(
        db_session,
        email="member@test.com",
        username="member_user",
        role=UserRole.member,
        sub_team_id=sub_team.id,
    )

    post = StandupPost(
        author_id=member_user.id,
        sub_team_id=sub_team.id,
        field_values={"Pending Tasks": "test"},
        task_snapshot=[],
    )
    db_session.add(post)
    await db_session.commit()

    token = _token(member_user)
    response = await async_client.get(
        "/api/dashboard/",
        headers={"Cookie": f"access_token={token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data["recent_activity"]) == 1
    activity = data["recent_activity"][0]
    assert "post_id" in activity
    assert "author_id" in activity
    assert "author_name" in activity
    assert "created_at" in activity
    assert "field_values" in activity
    assert activity["author_name"] == member_user.full_name
