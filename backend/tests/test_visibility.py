from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from fastapi import Response
from fastapi import HTTPException
from sqlalchemy import select

from app.models import InviteStatus, SubTeam, TeamInvite, User, UserRole
from app.routers.invites import accept_invite
from app.routers.users import (
    get_user as get_user_endpoint,
    list_users,
    update_user,
    update_user_role,
)
from app.schemas import InviteAcceptRequest, UserRoleUpdate, UserUpdate
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


async def _login(async_client, username: str) -> str:
    async_client.cookies.clear()
    response = await async_client.post(
        "/api/auth/token",
        data={"username": username, "password": "password"},
    )
    assert response.status_code == 200
    async_client.cookies.clear()
    return response.json()["access_token"]


def _invite(
    *,
    email: str,
    role: UserRole,
    invited_by_id: int,
    sub_team_id: int | None,
) -> TeamInvite:
    return TeamInvite(
        email=email,
        role=role,
        token=f"token-{email}",
        validation_code="123456",
        status=InviteStatus.pending,
        invited_by_id=invited_by_id,
        sub_team_id=sub_team_id,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=1),
    )


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


@pytest.mark.asyncio
async def test_user_list_endpoint_uses_phase_29_visibility(db_session, visibility_graph):
    member_users = await list_users(
        db=db_session,
        current_user=visibility_graph["alpha_member"],
        sub_team=visibility_graph["alpha"],
    )
    assistant_users = await list_users(
        db=db_session,
        current_user=visibility_graph["alpha_assistant"],
        sub_team=visibility_graph["alpha"],
    )
    manager_users = await list_users(
        db=db_session,
        current_user=visibility_graph["manager"],
        sub_team=None,
    )

    assert {user.username for user in member_users} == {
        "alpha_supervisor",
        "alpha_assistant",
        "alpha_member",
    }
    assert {user.username for user in assistant_users} == {
        "alpha_supervisor",
        "alpha_assistant",
        "alpha_member",
    }
    assert {user.username for user in manager_users} == {
        "manager",
        "alpha_supervisor",
        "alpha_assistant",
        "beta_supervisor",
        "alpha_member",
        "beta_member",
        "unscoped_member",
    }


@pytest.mark.asyncio
async def test_user_detail_blocks_out_of_scope_records(db_session, visibility_graph):
    visible = await get_user_endpoint(
        visibility_graph["alpha_assistant"].id,
        db=db_session,
        current_user=visibility_graph["alpha_member"],
    )

    assert visible.username == "alpha_assistant"

    with pytest.raises(HTTPException) as exc_info:
        await get_user_endpoint(
            visibility_graph["beta_member"].id,
            db=db_session,
            current_user=visibility_graph["alpha_member"],
        )
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_manager_only_leadership_role_assignment(db_session, visibility_graph):
    promoted = await update_user_role(
        visibility_graph["alpha_member"].id,
        UserRoleUpdate(role=UserRole.assistant_manager),
        db=db_session,
        current_user=visibility_graph["manager"],
    )

    assert promoted.role == UserRole.assistant_manager

    with pytest.raises(HTTPException) as exc_info:
        await update_user(
            visibility_graph["beta_member"].id,
            UserUpdate(role=UserRole.supervisor),
            db=db_session,
            current_user=visibility_graph["alpha_supervisor"],
        )
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_leaders_manage_only_scoped_members(db_session, visibility_graph):
    updated = await update_user(
        visibility_graph["alpha_member"].id,
        UserUpdate(full_name="Updated Alpha Member", role=UserRole.member),
        db=db_session,
        current_user=visibility_graph["alpha_assistant"],
    )

    assert updated.full_name == "Updated Alpha Member"

    with pytest.raises(HTTPException) as peer_exc:
        await update_user(
            visibility_graph["alpha_supervisor"].id,
            UserUpdate(full_name="Peer Update"),
            db=db_session,
            current_user=visibility_graph["alpha_assistant"],
        )
    assert peer_exc.value.status_code == 403

    with pytest.raises(HTTPException) as scope_exc:
        await update_user(
            visibility_graph["beta_member"].id,
            UserUpdate(full_name="Out Of Scope"),
            db=db_session,
            current_user=visibility_graph["alpha_assistant"],
        )
    assert scope_exc.value.status_code == 403


@pytest.mark.asyncio
async def test_member_profile_update_cannot_change_role_or_scope(
    db_session, visibility_graph
):
    updated = await update_user(
        visibility_graph["alpha_member"].id,
        UserUpdate(full_name="Self Updated"),
        db=db_session,
        current_user=visibility_graph["alpha_member"],
    )

    assert updated.full_name == "Self Updated"

    with pytest.raises(HTTPException) as exc_info:
        await update_user(
            visibility_graph["alpha_member"].id,
            UserUpdate(role=UserRole.manager),
            db=db_session,
            current_user=visibility_graph["alpha_member"],
        )
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_invite_role_assignment_is_manager_only(async_client, visibility_graph):
    alpha_id = visibility_graph["alpha"].id
    beta_id = visibility_graph["beta"].id
    manager_token = await _login(async_client, visibility_graph["manager"].username)
    assistant_token = await _login(async_client, visibility_graph["alpha_assistant"].username)

    response = await async_client.post(
        "/api/teams/invite",
        json={
            "email": "new.supervisor@example.com",
            "role": "supervisor",
            "sub_team_id": alpha_id,
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert response.status_code == 201
    assert response.json()["role"] == "supervisor"
    assert response.json()["sub_team_id"] == alpha_id

    async_client.cookies.clear()
    response = await async_client.post(
        "/api/teams/invite",
        json={
            "email": "blocked.leader@example.com",
            "role": "assistant_manager",
            "sub_team_id": alpha_id,
        },
        headers={"Authorization": f"Bearer {assistant_token}"},
    )
    assert response.status_code == 403

    response = await async_client.post(
        "/api/teams/invite",
        json={
            "email": "scoped.member@example.com",
            "role": "member",
            "sub_team_id": alpha_id,
        },
        headers={"Authorization": f"Bearer {assistant_token}"},
    )
    assert response.status_code == 201
    assert response.json()["role"] == "member"

    response = await async_client.post(
        "/api/teams/invite",
        json={
            "email": "out.scope.member@example.com",
            "role": "member",
            "sub_team_id": beta_id,
        },
        headers={"Authorization": f"Bearer {assistant_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_direct_add_role_assignment_is_manager_only(async_client, visibility_graph):
    alpha_member_id = visibility_graph["alpha_member"].id
    unscoped_member_id = visibility_graph["unscoped_member"].id
    manager_token = await _login(async_client, visibility_graph["manager"].username)
    assistant_token = await _login(async_client, visibility_graph["alpha_assistant"].username)

    response = await async_client.post(
        "/api/teams/add",
        json={
            "user_id": unscoped_member_id,
            "role": "manager",
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "manager"

    async_client.cookies.clear()
    response = await async_client.post(
        "/api/teams/add",
        json={
            "user_id": alpha_member_id,
            "role": "supervisor",
        },
        headers={"Authorization": f"Bearer {assistant_token}"},
    )
    assert response.status_code == 403

    response = await async_client.post(
        "/api/teams/add",
        json={
            "user_id": alpha_member_id,
            "role": "member",
        },
        headers={"Authorization": f"Bearer {assistant_token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_pending_invites_are_scoped_and_cancellation_is_guarded(
    async_client, db_session, visibility_graph
):
    manager_username = visibility_graph["manager"].username
    assistant_username = visibility_graph["alpha_assistant"].username
    alpha_invite = _invite(
        email="alpha.pending@example.com",
        role=UserRole.member,
        invited_by_id=visibility_graph["manager"].id,
        sub_team_id=visibility_graph["alpha"].id,
    )
    beta_invite = _invite(
        email="beta.pending@example.com",
        role=UserRole.member,
        invited_by_id=visibility_graph["manager"].id,
        sub_team_id=visibility_graph["beta"].id,
    )
    db_session.add_all([alpha_invite, beta_invite])
    await db_session.commit()
    beta_invite_id = beta_invite.id

    assistant_token = await _login(async_client, assistant_username)
    response = await async_client.get(
        "/api/invites/pending",
        headers={"Authorization": f"Bearer {assistant_token}"},
    )
    assert response.status_code == 200
    assert [invite["email"] for invite in response.json()] == ["alpha.pending@example.com"]

    response = await async_client.delete(
        f"/api/invites/{beta_invite_id}",
        headers={"Authorization": f"Bearer {assistant_token}"},
    )
    assert response.status_code == 403

    async_client.cookies.clear()
    manager_token = await _login(async_client, manager_username)
    response = await async_client.get(
        "/api/invites/pending",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert response.status_code == 200
    assert {invite["email"] for invite in response.json()} == {
        "alpha.pending@example.com",
        "beta.pending@example.com",
    }

    response = await async_client.delete(
        f"/api/invites/{beta_invite_id}",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_invite_acceptance_assigns_stored_role_and_scope(
    db_session, visibility_graph
):
    invite = _invite(
        email="accepted.assistant@example.com",
        role=UserRole.assistant_manager,
        invited_by_id=visibility_graph["manager"].id,
        sub_team_id=visibility_graph["alpha"].id,
    )
    db_session.add(invite)
    await db_session.commit()

    user = await accept_invite(
        InviteAcceptRequest(
            token=invite.token,
            validation_code=invite.validation_code,
            username="accepted_assistant",
            full_name="Accepted Assistant",
            password="password",
        ),
        response=Response(),
        db=db_session,
    )

    assert user.role == UserRole.assistant_manager
    assert user.sub_team_id == visibility_graph["alpha"].id
