from datetime import date, datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import inspect as sa_inspect, select

from app.models import SubTeam, User, UserRole, WeeklyBoardSummary, WeeklyPost, WeeklyPostAppend
from app.utils.auth import create_access_token, hash_password


def _auth_headers(user: User) -> dict[str, str]:
    token = create_access_token({"sub": str(sa_inspect(user).identity[0])})
    return {"Authorization": f"Bearer {token}"}


async def _create_user(db_session, *, email: str, username: str, full_name: str, role: UserRole, sub_team_id: int) -> User:
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


async def _graph(db_session):
    sub_team = SubTeam(name="Board Team", supervisor_id=None)
    db_session.add(sub_team)
    await db_session.commit()
    await db_session.refresh(sub_team)
    author = await _create_user(
        db_session,
        email="author@example.com",
        username="author",
        full_name="Author User",
        role=UserRole.member,
        sub_team_id=sub_team.id,
    )
    other = await _create_user(
        db_session,
        email="other@example.com",
        username="other",
        full_name="Other User",
        role=UserRole.member,
        sub_team_id=sub_team.id,
    )
    return {"sub_team": sub_team, "author": author, "other": other}


def _week(now: datetime | None = None) -> tuple[int, int, date]:
    now = now or datetime.now(timezone.utc).replace(tzinfo=None)
    iso = now.isocalendar()
    return iso.year, iso.week, date.fromisocalendar(iso.year, iso.week, 1)


@pytest.mark.asyncio
async def test_current_week_primary_post_and_duplicate_rejection(async_client: AsyncClient, db_session, monkeypatch):
    graph = await _graph(db_session)
    year, week, week_start = _week()

    monkeypatch.setattr("app.routers.board.current_board_week", lambda: type("W", (), {"iso_year": year, "iso_week": week, "week_start_date": week_start})())

    response = await async_client.post("/api/board/posts", json={"content": "Hello board"}, headers=_auth_headers(graph["author"]))
    assert response.status_code == 201
    assert response.json()["content"] == "Hello board"

    response = await async_client.post("/api/board/posts", json={"content": "Second post"}, headers=_auth_headers(graph["author"]))
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_week_payload_groups_posts_and_enforces_ownership(async_client: AsyncClient, db_session, monkeypatch):
    graph = await _graph(db_session)
    year, week, week_start = _week()
    monkeypatch.setattr("app.routers.board.current_board_week", lambda: type("W", (), {"iso_year": year, "iso_week": week, "week_start_date": week_start})())

    response = await async_client.post("/api/board/posts", json={"content": "Author post"}, headers=_auth_headers(graph["author"]))
    post_id = response.json()["id"]
    response = await async_client.post(f"/api/board/posts/{post_id}/appends", json={"content": "Follow-up"}, headers=_auth_headers(graph["author"]))
    assert response.status_code == 201

    response = await async_client.get("/api/board/week", headers=_auth_headers(graph["author"]))
    assert response.status_code == 200
    data = response.json()
    assert data["is_current_week"] is True
    assert data["posts"][0]["appends"][0]["content"] == "Follow-up"

    response = await async_client.patch(f"/api/board/posts/{post_id}", json={"content": "Updated"}, headers=_auth_headers(graph["other"]))
    assert response.status_code == 403

    response = await async_client.delete(f"/api/board/posts/{post_id}", headers=_auth_headers(graph["other"]))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_past_week_mutation_rejected(async_client: AsyncClient, db_session, monkeypatch):
    graph = await _graph(db_session)
    year, week, week_start = _week()
    monkeypatch.setattr("app.routers.board.current_board_week", lambda: type("W", (), {"iso_year": year, "iso_week": week, "week_start_date": week_start})())

    response = await async_client.post("/api/board/posts", json={"content": "Current"}, headers=_auth_headers(graph["author"]))
    post_id = response.json()["id"]
    monkeypatch.setattr("app.routers.board.current_board_week", lambda: type("W", (), {"iso_year": year, "iso_week": week - 1, "week_start_date": week_start - timedelta(days=7)})())

    response = await async_client.patch(f"/api/board/posts/{post_id}", json={"content": "Past edit"}, headers=_auth_headers(graph["author"]))
    assert response.status_code == 403

    response = await async_client.post(f"/api/board/posts/{post_id}/appends", json={"content": "Past append"}, headers=_auth_headers(graph["author"]))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_summary_generation_caches_and_short_circuits(async_client: AsyncClient, db_session, monkeypatch):
    graph = await _graph(db_session)
    year, week, week_start = _week()

    monkeypatch.setattr("app.routers.board.current_board_week", lambda: type("W", (), {"iso_year": year, "iso_week": week, "week_start_date": week_start})())

    response = await async_client.post("/api/board/posts", json={"content": "Alpha"}, headers=_auth_headers(graph["author"]))
    post_id = response.json()["id"]

    calls = []

    async def fake_acompletion(**kwargs):
        calls.append(kwargs)
        class R:
            model = "fake"
            choices = [type("C", (), {"message": type("M", (), {"content": "AI digest"})()})()]
        return R()

    monkeypatch.setattr("app.services.weekly_board.acompletion", fake_acompletion)

    response = await async_client.post("/api/board/week/summary", headers=_auth_headers(graph["author"]))
    assert response.status_code == 200
    assert response.json()["summary_text"] == "AI digest"
    assert len(calls) == 1

    response = await async_client.post("/api/board/week/summary", headers=_auth_headers(graph["author"]))
    assert response.status_code == 200
    assert len(calls) == 1

    result = await db_session.execute(select(WeeklyBoardSummary))
    assert result.scalar_one_or_none() is not None

    await db_session.execute(select(WeeklyPostAppend).where(WeeklyPostAppend.post_id == post_id))
    await db_session.execute(select(WeeklyPost))


@pytest.mark.asyncio
async def test_week_payload_is_scoped_by_visible_team(async_client: AsyncClient, db_session):
    team_a = SubTeam(name="Board Team A", supervisor_id=None)
    team_b = SubTeam(name="Board Team B", supervisor_id=None)
    db_session.add_all([team_a, team_b])
    await db_session.commit()
    await db_session.refresh(team_a)
    await db_session.refresh(team_b)

    member_a = await _create_user(
        db_session,
        email="board-a@example.com",
        username="board-a",
        full_name="Board A",
        role=UserRole.member,
        sub_team_id=team_a.id,
    )
    member_b = await _create_user(
        db_session,
        email="board-b@example.com",
        username="board-b",
        full_name="Board B",
        role=UserRole.member,
        sub_team_id=team_b.id,
    )
    manager = await _create_user(
        db_session,
        email="board-manager@example.com",
        username="board-manager",
        full_name="Board Manager",
        role=UserRole.manager,
        sub_team_id=team_a.id,
    )
    year, week, week_start = _week()
    db_session.add_all(
        [
            WeeklyPost(
                author_id=member_a.id,
                sub_team_id=team_a.id,
                iso_year=year,
                iso_week=week,
                week_start_date=week_start,
                content="Alpha board item",
            ),
            WeeklyPost(
                author_id=member_b.id,
                sub_team_id=team_b.id,
                iso_year=year,
                iso_week=week,
                week_start_date=week_start,
                content="Beta board item",
            ),
        ]
    )
    await db_session.commit()

    response = await async_client.get("/api/board/week", headers=_auth_headers(member_a))
    assert response.status_code == 200
    assert [post["content"] for post in response.json()["posts"]] == ["Alpha board item"]

    response = await async_client.get("/api/board/week", headers=_auth_headers(manager))
    assert response.status_code == 200
    assert {post["content"] for post in response.json()["posts"]} == {
        "Alpha board item",
        "Beta board item",
    }
