import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models import Milestone, Project, Sprint, SprintStatus, SubTeam, Task, User, UserRole
from app.utils.auth import hash_password


@pytest.mark.asyncio
async def test_create_sprint_as_admin(db_session, async_client: AsyncClient, sub_team):
    """Test that admin can create a sprint"""
    # Create admin user
    admin = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        hashed_password=hash_password("password"),
        role=UserRole.admin,
        sub_team_id=sub_team.id
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    # Create project and milestone
    project = Project(name="Test Project", sub_team_id=sub_team.id)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    milestone = Milestone(
        title="Test Milestone",
        status="planned",
        project_id=project.id
    )
    db_session.add(milestone)
    await db_session.commit()
    await db_session.refresh(milestone)

    # Login as admin
    login_response = await async_client.post("/api/auth/token", data={
        "username": "admin",
        "password": "password"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create sprint
    response = await async_client.post("/api/sprints/", json={
        "name": "Test Sprint",
        "start_date": "2026-04-27T00:00:00",
        "end_date": "2026-05-10T23:59:59",
        "milestone_id": milestone.id
    }, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Sprint"
    assert data["status"] == "planned"
    assert data["milestone_id"] == milestone.id


@pytest.mark.asyncio
async def test_create_sprint_as_member_forbidden(db_session, async_client: AsyncClient, sub_team):
    """Test that member cannot create a sprint (403 Forbidden)"""
    # Create member user
    member = User(
        email="member@example.com",
        username="member",
        full_name="Member User",
        hashed_password=hash_password("password"),
        role=UserRole.member,
        sub_team_id=sub_team.id
    )
    db_session.add(member)
    await db_session.commit()
    await db_session.refresh(member)

    # Create project and milestone
    project = Project(name="Test Project", sub_team_id=sub_team.id)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    milestone = Milestone(
        title="Test Milestone",
        status="planned",
        project_id=project.id
    )
    db_session.add(milestone)
    await db_session.commit()
    await db_session.refresh(milestone)

    # Login as member
    login_response = await async_client.post("/api/auth/token", data={
        "username": "member",
        "password": "password"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Try to create sprint
    response = await async_client.post("/api/sprints/", json={
        "name": "Test Sprint",
        "start_date": "2026-04-27T00:00:00",
        "end_date": "2026-05-10T23:59:59",
        "milestone_id": milestone.id
    }, headers=headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_sprints_filters_by_sub_team(db_session, async_client: AsyncClient, sub_team):
    """Test that sprint list is filtered by user's sub-team"""
    # Create another sub-team
    other_team = SubTeam(name="Other Team", supervisor_id=None)
    db_session.add(other_team)
    await db_session.commit()
    await db_session.refresh(other_team)

    # Create admin user
    admin = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        hashed_password=hash_password("password"),
        role=UserRole.admin,
        sub_team_id=sub_team.id
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    # Create projects for both teams
    project1 = Project(name="Project 1", sub_team_id=sub_team.id)
    project2 = Project(name="Project 2", sub_team_id=other_team.id)
    db_session.add_all([project1, project2])
    await db_session.commit()
    await db_session.refresh(project1)
    await db_session.refresh(project2)

    # Create milestones
    milestone1 = Milestone(title="Milestone 1", status="planned", project_id=project1.id)
    milestone2 = Milestone(title="Milestone 2", status="planned", project_id=project2.id)
    db_session.add_all([milestone1, milestone2])
    await db_session.commit()
    await db_session.refresh(milestone1)
    await db_session.refresh(milestone2)

    # Create sprints for both teams
    sprint1 = Sprint(name="Sprint 1", start_date="2026-04-27T00:00:00", end_date="2026-05-10T23:59:59", milestone_id=milestone1.id, status=SprintStatus.planned)
    sprint2 = Sprint(name="Sprint 2", start_date="2026-04-27T00:00:00", end_date="2026-05-10T23:59:59", milestone_id=milestone2.id, status=SprintStatus.planned)
    db_session.add_all([sprint1, sprint2])
    await db_session.commit()

    # Login as admin (sub_team 1)
    login_response = await async_client.post("/api/auth/token", data={
        "username": "admin",
        "password": "password"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # List sprints - should only see sprint1 from sub_team 1
    response = await async_client.get("/api/sprints/", headers=headers)
    assert response.status_code == 200
    sprints = response.json()
    assert len(sprints) == 1
    assert sprints[0]["name"] == "Sprint 1"


@pytest.mark.asyncio
async def test_close_sprint_with_task_mapping(db_session, async_client: AsyncClient, sub_team):
    """Test that closing a sprint moves tasks according to mapping"""
    # Create admin user
    admin = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        hashed_password=hash_password("password"),
        role=UserRole.admin,
        sub_team_id=sub_team.id
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    # Create project, milestone, and two sprints
    project = Project(name="Test Project", sub_team_id=sub_team.id)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    milestone = Milestone(title="Test Milestone", status="planned", project_id=project.id)
    db_session.add(milestone)
    await db_session.commit()
    await db_session.refresh(milestone)

    sprint1 = Sprint(name="Sprint 1", start_date="2026-04-27T00:00:00", end_date="2026-05-10T23:59:59", milestone_id=milestone.id, status=SprintStatus.planned)
    sprint2 = Sprint(name="Sprint 2", start_date="2026-05-11T00:00:00", end_date="2026-05-24T23:59:59", milestone_id=milestone.id, status=SprintStatus.planned)
    db_session.add_all([sprint1, sprint2])
    await db_session.commit()
    await db_session.refresh(sprint1)
    await db_session.refresh(sprint2)

    # Create tasks in sprint1
    task1 = Task(title="Task 1", status="todo", project_id=project.id, milestone_id=milestone.id, sprint_id=sprint1.id, creator_id=admin.id)
    task2 = Task(title="Task 2", status="todo", project_id=project.id, milestone_id=milestone.id, sprint_id=sprint1.id, creator_id=admin.id)
    task3 = Task(title="Task 3", status="todo", project_id=project.id, milestone_id=milestone.id, sprint_id=sprint1.id, creator_id=admin.id)
    db_session.add_all([task1, task2, task3])
    await db_session.commit()
    await db_session.refresh(task1)
    await db_session.refresh(task2)
    await db_session.refresh(task3)

    # Login as admin
    login_response = await async_client.post("/api/auth/token", data={
        "username": "admin",
        "password": "password"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Close sprint1 with mapping: task1 -> sprint2, task2 -> backlog (null), task3 -> sprint2
    response = await async_client.post(f"/api/sprints/{sprint1.id}/close", json={
        "task_mapping": {
            str(task1.id): sprint2.id,
            str(task2.id): None,
            str(task3.id): sprint2.id
        }
    }, headers=headers)

    assert response.status_code == 200

    # Verify task reassignments
    await db_session.refresh(task1)
    await db_session.refresh(task2)
    await db_session.refresh(task3)
    await db_session.refresh(sprint1)

    assert task1.sprint_id == sprint2.id
    assert task2.sprint_id is None  # Backlog
    assert task3.sprint_id == sprint2.id
    assert sprint1.status == SprintStatus.closed


@pytest.mark.asyncio
async def test_close_sprint_partial_mapping(db_session, async_client: AsyncClient, sub_team):
    """Test that sprint close handles partial mappings (some tasks moved, others to backlog)"""
    # Create admin user
    admin = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        hashed_password=hash_password("password"),
        role=UserRole.admin,
        sub_team_id=sub_team.id
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    # Create project, milestone, and sprint
    project = Project(name="Test Project", sub_team_id=sub_team.id)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    milestone = Milestone(title="Test Milestone", status="planned", project_id=project.id)
    db_session.add(milestone)
    await db_session.commit()
    await db_session.refresh(milestone)

    sprint1 = Sprint(name="Sprint 1", start_date="2026-04-27T00:00:00", end_date="2026-05-10T23:59:59", milestone_id=milestone.id, status=SprintStatus.planned)
    db_session.add(sprint1)
    await db_session.commit()
    await db_session.refresh(sprint1)

    # Create tasks
    task1 = Task(title="Task 1", status="todo", project_id=project.id, milestone_id=milestone.id, sprint_id=sprint1.id, creator_id=admin.id)
    task2 = Task(title="Task 2", status="todo", project_id=project.id, milestone_id=milestone.id, sprint_id=sprint1.id, creator_id=admin.id)
    task3 = Task(title="Task 3", status="todo", project_id=project.id, milestone_id=milestone.id, sprint_id=sprint1.id, creator_id=admin.id)
    db_session.add_all([task1, task2, task3])
    await db_session.commit()
    await db_session.refresh(task1)
    await db_session.refresh(task2)
    await db_session.refresh(task3)

    # Login as admin
    login_response = await async_client.post("/api/auth/token", data={
        "username": "admin",
        "password": "password"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Close sprint with partial mapping: only task1 mapped, others omitted (should stay or go to backlog?)
    response = await async_client.post(f"/api/sprints/{sprint1.id}/close", json={
        "task_mapping": {
            str(task1.id): None  # Task 1 to backlog
        }
    }, headers=headers)

    assert response.status_code == 200

    # Verify task1 moved to backlog, task2 and task3 unchanged
    await db_session.refresh(task1)
    await db_session.refresh(task2)
    await db_session.refresh(task3)

    assert task1.sprint_id is None
    # task2 and task3 should remain in sprint1 (not moved)
    assert task2.sprint_id == sprint1.id
    assert task3.sprint_id == sprint1.id


@pytest.mark.asyncio
async def test_sprint_create_with_end_date_triggers_reminder_rebuild(db_session, async_client: AsyncClient, sub_team):
    """Test that creating a sprint with end_date triggers reminder rebuild."""
    from app.models import EventNotification, NotificationEventType, NotificationStatus
    
    # Create admin user
    admin = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        hashed_password=hash_password("password"),
        role=UserRole.admin,
        sub_team_id=sub_team.id
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    # Create project and milestone
    project = Project(name="Test Project", sub_team_id=sub_team.id)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    milestone = Milestone(
        title="Test Milestone",
        status="planned",
        project_id=project.id
    )
    db_session.add(milestone)
    await db_session.commit()
    await db_session.refresh(milestone)

    # Create a task with assignee to enable reminder generation
    task = Task(
        title="Test Task",
        status="todo",
        project_id=project.id,
        milestone_id=milestone.id,
        assignee_id=admin.id,
        creator_id=admin.id
    )
    db_session.add(task)
    await db_session.commit()

    # Login as admin
    login_response = await async_client.post("/api/auth/token", data={
        "username": "admin",
        "password": "password"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create sprint with end_date
    response = await async_client.post("/api/sprints/", json={
        "name": "Test Sprint",
        "start_date": "2026-04-27T00:00:00",
        "end_date": "2026-05-10T23:59:59",
        "milestone_id": milestone.id
    }, headers=headers)

    assert response.status_code == 201
    sprint_id = response.json()["id"]

    # Verify reminder was created
    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.event_type == NotificationEventType.sprint_end,
            EventNotification.event_ref_id == sprint_id,
            EventNotification.user_id == admin.id,
            EventNotification.status == NotificationStatus.pending
        )
    )
    reminder = result.scalar_one_or_none()
    assert reminder is not None


@pytest.mark.asyncio
async def test_sprint_update_end_date_triggers_reminder_rebuild(db_session, async_client: AsyncClient, sub_team):
    """Test that updating sprint end_date triggers reminder rebuild."""
    from app.models import EventNotification, NotificationEventType, NotificationStatus
    from datetime import datetime, timedelta, timezone
    
    # Create admin user
    admin = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        hashed_password=hash_password("password"),
        role=UserRole.admin,
        sub_team_id=sub_team.id
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    # Create project and milestone
    project = Project(name="Test Project", sub_team_id=sub_team.id)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    milestone = Milestone(
        title="Test Milestone",
        status="planned",
        project_id=project.id
    )
    db_session.add(milestone)
    await db_session.commit()
    await db_session.refresh(milestone)

    # Create a task with assignee
    task = Task(
        title="Test Task",
        status="todo",
        project_id=project.id,
        milestone_id=milestone.id,
        assignee_id=admin.id,
        creator_id=admin.id
    )
    db_session.add(task)
    await db_session.commit()

    # Login as admin
    login_response = await async_client.post("/api/auth/token", data={
        "username": "admin",
        "password": "password"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create sprint with end_date
    response = await async_client.post("/api/sprints/", json={
        "name": "Test Sprint",
        "start_date": "2026-04-27T00:00:00",
        "end_date": "2026-05-10T23:59:59",
        "milestone_id": milestone.id
    }, headers=headers)

    assert response.status_code == 201
    sprint_id = response.json()["id"]

    # Get initial reminder
    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.event_type == NotificationEventType.sprint_end,
            EventNotification.event_ref_id == sprint_id,
        )
    )
    initial_reminders = result.scalars().all()
    initial_count = len(initial_reminders)

    # Update sprint end_date
    response = await async_client.patch(f"/api/sprints/{sprint_id}", json={
        "end_date": "2026-05-15T23:59:59"
    }, headers=headers)

    assert response.status_code == 200

    # Verify reminders were rebuilt (pending deleted and recreated)
    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.event_type == NotificationEventType.sprint_end,
            EventNotification.event_ref_id == sprint_id,
            EventNotification.status == NotificationStatus.pending
        )
    )
    pending_reminders = result.scalars().all()
    assert len(pending_reminders) == initial_count


@pytest.mark.asyncio
async def test_milestone_update_due_date_triggers_reminder_rebuild(db_session, async_client: AsyncClient, sub_team):
    """Test that updating milestone due_date triggers reminder rebuild."""
    from app.models import EventNotification, NotificationEventType, NotificationStatus
    
    # Create admin user
    admin = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        hashed_password=hash_password("password"),
        role=UserRole.admin,
        sub_team_id=sub_team.id
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    # Create project and milestone
    project = Project(name="Test Project", sub_team_id=sub_team.id)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    milestone = Milestone(
        title="Test Milestone",
        status="planned",
        due_date="2026-05-10T23:59:59",
        project_id=project.id
    )
    db_session.add(milestone)
    await db_session.commit()
    await db_session.refresh(milestone)

    # Create a task with assignee
    task = Task(
        title="Test Task",
        status="todo",
        project_id=project.id,
        milestone_id=milestone.id,
        assignee_id=admin.id,
        creator_id=admin.id
    )
    db_session.add(task)
    await db_session.commit()

    # Login as admin
    login_response = await async_client.post("/api/auth/token", data={
        "username": "admin",
        "password": "password"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create milestone (triggers initial reminder build)
    response = await async_client.post("/api/milestones/", json={
        "title": "Another Milestone",
        "status": "planned",
        "due_date": "2026-05-10T23:59:59",
        "project_id": project.id
    }, headers=headers)

    assert response.status_code == 201
    milestone_id = response.json()["id"]

    # Get initial reminder count
    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.event_type == NotificationEventType.milestone_due,
            EventNotification.event_ref_id == milestone_id,
        )
    )
    initial_reminders = result.scalars().all()
    initial_count = len(initial_reminders)

    # Update milestone due_date
    response = await async_client.patch(f"/api/milestones/{milestone_id}", json={
        "due_date": "2026-05-15T23:59:59"
    }, headers=headers)

    assert response.status_code == 200

    # Verify reminders were rebuilt (pending deleted and recreated)
    result = await db_session.execute(
        select(EventNotification).where(
            EventNotification.event_type == NotificationEventType.milestone_due,
            EventNotification.event_ref_id == milestone_id,
            EventNotification.status == NotificationStatus.pending
        )
    )
    pending_reminders = result.scalars().all()
    assert len(pending_reminders) == initial_count
