import pytest

from app.models import SubTeam, User, UserRole
from app.auth import hash_password

@pytest.fixture
async def sub_team(db_session):
    """Create a test sub-team"""
    sub_team = SubTeam(name="Test Team", supervisor_id=None)
    db_session.add(sub_team)
    await db_session.commit()
    await db_session.refresh(sub_team)
    yield sub_team
    await db_session.delete(sub_team)
    await db_session.commit()

@pytest.fixture
async def user_with_sub_team(db_session, sub_team):
    """Create a test user with sub-team assignment"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=hash_password("password"),
        role=UserRole.member,
        sub_team_id=sub_team.id
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    yield user
    await db_session.delete(user)
    await db_session.commit()
