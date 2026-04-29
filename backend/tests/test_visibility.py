import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy import select

from app.models import SubTeam, User, UserRole
from app.services.visibility import (
    ACTIVE_ROLES,
    can_see_user,
    is_leader,
    is_manager,
    is_member,
    peer_leader_ids,
    scoped_sub_team_filter,
    visible_sub_team_ids,
    visible_user_filter,
)
from app.utils.auth import (
    hash_password,
    get_sub_team,
    require_leader,
    require_leader_or_manager,
    require_manager,
)


async def _create_user(
    db_session,
    *,
    email: str,
    username: str,
    role: UserRole,
    sub_team_id: int | None = None,
) -> User:
    user = User(
        email=email,
        username=username,
        full_name=username.replace("_", " ").title(),
        hashed_password=hash_password("password"),
        role=role,
        sub_team_id=sub_team_id,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def visibility_graph(db_session):
    alpha = SubTeam(name="Alpha", supervisor_id=None)
    beta = SubTeam(name="Beta", supervisor_id=None)
    db_session.add_all([alpha, beta])
    await db_session.flush()

    manager = await _create_user(
        db_session,
        email="manager@example.com",
        username="manager",
        role=UserRole.manager,
    )
    alpha_supervisor = await _create_user(
        db_session,
        email="alpha.supervisor@example.com",
        username="alpha_supervisor",
        role=UserRole.supervisor,
        sub_team_id=alpha.id,
    )
    alpha_assistant = await _create_user(
        db_session,
        email="alpha.assistant@example.com",
        username="alpha_assistant",
        role=UserRole.assistant_manager,
        sub_team_id=alpha.id,
    )
    beta_supervisor = await _create_user(
        db_session,
        email="beta.supervisor@example.com",
        username="beta_supervisor",
        role=UserRole.supervisor,
        sub_team_id=beta.id,
    )
    alpha_member = await _create_user(
        db_session,
        email="alpha.member@example.com",
        username="alpha_member",
        role=UserRole.member,
        sub_team_id=alpha.id,
    )
    beta_member = await _create_user(
        db_session,
        email="beta.member@example.com",
        username="beta_member",
        role=UserRole.member,
        sub_team_id=beta.id,
    )
    unscoped_member = await _create_user(
        db_session,
        email="unscoped.member@example.com",
        username="unscoped_member",
        role=UserRole.member,
    )

    alpha.supervisor_id = alpha_supervisor.id
    beta.supervisor_id = beta_supervisor.id
    db_session.add_all([alpha, beta])
    await db_session.commit()

    return {
        "alpha": alpha,
        "beta": beta,
        "manager": manager,
        "alpha_supervisor": alpha_supervisor,
        "alpha_assistant": alpha_assistant,
        "beta_supervisor": beta_supervisor,
        "alpha_member": alpha_member,
        "beta_member": beta_member,
        "unscoped_member": unscoped_member,
    }


async def _visible_usernames(db_session, current_user: User) -> set[str]:
    allowed_ids = await visible_sub_team_ids(db_session, current_user)
    result = await db_session.execute(
        select(User).where(visible_user_filter(current_user, allowed_ids))
    )
    return {user.username for user in result.scalars().all()}


@pytest.mark.asyncio
async def test_active_role_vocabulary_excludes_admin():
    assert [role.value for role in ACTIVE_ROLES] == [
        "manager",
        "supervisor",
        "assistant_manager",
        "member",
    ]
    assert not hasattr(UserRole, "admin")


@pytest.mark.asyncio
async def test_role_predicates_distinguish_manager_leaders_and_members(visibility_graph):
    assert is_manager(visibility_graph["manager"])
    assert is_leader(visibility_graph["alpha_supervisor"])
    assert is_leader(visibility_graph["alpha_assistant"])
    assert is_member(visibility_graph["alpha_member"])
    assert not is_leader(visibility_graph["manager"])
    assert not is_manager(visibility_graph["alpha_supervisor"])


@pytest.mark.asyncio
async def test_member_visibility_is_sub_team_only(db_session, visibility_graph):
    visible = await _visible_usernames(db_session, visibility_graph["alpha_member"])

    assert visible == {
        "alpha_supervisor",
        "alpha_assistant",
        "alpha_member",
    }
    assert await can_see_user(
        db_session, visibility_graph["alpha_member"], visibility_graph["alpha_assistant"]
    )
    assert not await can_see_user(
        db_session, visibility_graph["alpha_member"], visibility_graph["beta_member"]
    )


@pytest.mark.asyncio
async def test_supervisor_visibility_includes_scoped_members_and_peer_leaders(
    db_session, visibility_graph
):
    visible = await _visible_usernames(db_session, visibility_graph["alpha_supervisor"])
    peers = await peer_leader_ids(db_session, visibility_graph["alpha_supervisor"])

    assert visible == {
        "alpha_supervisor",
        "alpha_assistant",
        "alpha_member",
    }
    assert visibility_graph["alpha_assistant"].id in peers
    assert visibility_graph["beta_supervisor"].id not in peers
    assert "manager" not in visible
    assert "beta_member" not in visible


@pytest.mark.asyncio
async def test_assistant_manager_visibility_matches_supervisor_scope(
    db_session, visibility_graph
):
    visible = await _visible_usernames(db_session, visibility_graph["alpha_assistant"])

    assert visible == {
        "alpha_supervisor",
        "alpha_assistant",
        "alpha_member",
    }
    assert await can_see_user(
        db_session, visibility_graph["alpha_assistant"], visibility_graph["alpha_supervisor"]
    )
    assert not await can_see_user(
        db_session, visibility_graph["alpha_assistant"], visibility_graph["manager"]
    )


@pytest.mark.asyncio
async def test_manager_visibility_can_span_all_or_selected_sub_team(
    db_session, visibility_graph
):
    all_ids = await visible_sub_team_ids(db_session, visibility_graph["manager"])
    selected_ids = await visible_sub_team_ids(
        db_session,
        visibility_graph["manager"],
        requested_sub_team_id=visibility_graph["alpha"].id,
    )
    all_visible = await _visible_usernames(db_session, visibility_graph["manager"])

    assert all_ids is None
    assert selected_ids == [visibility_graph["alpha"].id]
    assert all_visible == {
        "manager",
        "alpha_supervisor",
        "alpha_assistant",
        "beta_supervisor",
        "alpha_member",
        "beta_member",
        "unscoped_member",
    }


@pytest.mark.asyncio
async def test_scoped_sub_team_filter_reuses_visible_scope(db_session, visibility_graph):
    allowed_ids = await visible_sub_team_ids(
        db_session, visibility_graph["alpha_assistant"]
    )
    result = await db_session.execute(
        select(SubTeam).where(
            scoped_sub_team_filter(SubTeam.id, visibility_graph["alpha_assistant"], allowed_ids)
        )
    )

    assert [team.name for team in result.scalars().all()] == ["Alpha"]


@pytest.mark.asyncio
async def test_auth_guards_use_phase_29_roles(db_session, visibility_graph):
    assert await require_manager(visibility_graph["manager"]) == visibility_graph["manager"]
    assert (
        await require_leader_or_manager(visibility_graph["alpha_assistant"])
        == visibility_graph["alpha_assistant"]
    )
    assert await require_leader(visibility_graph["alpha_supervisor"]) == visibility_graph[
        "alpha_supervisor"
    ]

    with pytest.raises(HTTPException):
        await require_manager(visibility_graph["alpha_supervisor"])
    with pytest.raises(HTTPException):
        await require_leader(visibility_graph["manager"])


@pytest.mark.asyncio
async def test_get_sub_team_resolves_member_leader_and_manager_scope(
    db_session, visibility_graph
):
    member_team = await get_sub_team(
        current_user=visibility_graph["alpha_member"],
        x_sub_team_id=None,
        db=db_session,
    )
    leader_team = await get_sub_team(
        current_user=visibility_graph["alpha_assistant"],
        x_sub_team_id=visibility_graph["alpha"].id,
        db=db_session,
    )
    manager_all = await get_sub_team(
        current_user=visibility_graph["manager"],
        x_sub_team_id=None,
        db=db_session,
    )

    assert member_team.id == visibility_graph["alpha"].id
    assert leader_team.id == visibility_graph["alpha"].id
    assert manager_all is None

    with pytest.raises(HTTPException):
        await get_sub_team(
            current_user=visibility_graph["alpha_assistant"],
            x_sub_team_id=visibility_graph["beta"].id,
            db=db_session,
        )
