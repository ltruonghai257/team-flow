import os
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ.setdefault(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{Path(__file__).resolve().parent / 'test.db'}",
)
os.environ.setdefault("RUN_MIGRATIONS", "false")
os.environ.setdefault("COOKIE_SECURE", "false")

from app.utils.auth import hash_password
from app.db.database import Base, get_db
from app.api.main import app  # canonical app target
from app.models import SubTeam, User, UserRole


@pytest_asyncio.fixture
async def db_session(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=False)
    session_local = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async with session_local() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    async def override_get_db():
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client

    app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture
async def sub_team(db_session):
    sub_team = SubTeam(name="Test Team", supervisor_id=None)
    db_session.add(sub_team)
    await db_session.commit()
    await db_session.refresh(sub_team)
    yield sub_team


@pytest_asyncio.fixture
async def user_with_sub_team(db_session, sub_team):
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=hash_password("password"),
        role=UserRole.member,
        sub_team_id=sub_team.id,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    yield user


@pytest_asyncio.fixture
async def member_user(db_session):
    """Fixture for member role user with auth headers"""
    sub_team = SubTeam(name="Test SubTeam")
    db_session.add(sub_team)
    await db_session.flush()

    user = User(
        email="member@example.com",
        username="member_user",
        full_name="Member User",
        hashed_password=hash_password("password"),
        role=UserRole.member,
        sub_team_id=sub_team.id,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    yield {"user": user, "headers": {"Cookie": f"access_token={token}"}}


@pytest_asyncio.fixture
async def supervisor_user(db_session):
    """Fixture for supervisor role user with auth headers"""
    sub_team = SubTeam(name="Test SubTeam")
    db_session.add(sub_team)
    await db_session.flush()

    user = User(
        email="supervisor@example.com",
        username="supervisor_user",
        full_name="Supervisor User",
        hashed_password=hash_password("password"),
        role=UserRole.supervisor,
        sub_team_id=sub_team.id,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    yield {"user": user, "headers": {"Cookie": f"access_token={token}"}}


@pytest_asyncio.fixture
async def assistant_manager_user(db_session):
    """Fixture for assistant_manager role user with auth headers"""
    sub_team = SubTeam(name="Test SubTeam")
    db_session.add(sub_team)
    await db_session.flush()

    user = User(
        email="assistant_manager@example.com",
        username="assistant_manager_user",
        full_name="Assistant Manager User",
        hashed_password=hash_password("password"),
        role=UserRole.assistant_manager,
        sub_team_id=sub_team.id,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    yield {"user": user, "headers": {"Cookie": f"access_token={token}"}}


@pytest_asyncio.fixture
async def manager_user(db_session):
    """Fixture for manager role user with auth headers"""
    sub_team = SubTeam(name="Test SubTeam")
    db_session.add(sub_team)
    await db_session.flush()

    user = User(
        email="manager@example.com",
        username="manager_user",
        full_name="Manager User",
        hashed_password=hash_password("password"),
        role=UserRole.manager,
        sub_team_id=sub_team.id,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    yield {"user": user, "headers": {"Cookie": f"access_token={token}"}}
