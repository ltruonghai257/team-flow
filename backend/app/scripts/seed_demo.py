"""Seed demo data for local development / timeline verification.

Creates:
  - 1 supervisor user  (supervisor / password123)
  - 3 member users     (alice, bob, carol / password123)
  - 2 projects with distinct colors
  - 2 milestones per project
  - ~16 tasks spread across milestones and assignees, with varied
    statuses, due dates (past, present, future), and one unscheduled task

Run from the backend directory:
    python -m app.scripts.seed_demo

Safe to re-run — skips creation if data already exists (checks by email).
"""

import asyncio
from datetime import datetime, timedelta, timezone


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _days(n: int) -> datetime:
    return (_now() + timedelta(days=n))


async def main() -> None:
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models import (
        User, UserRole, Project, Milestone, MilestoneStatus, Task,
        TaskStatus, TaskPriority,
    )
    from app.auth import hash_password

    async with AsyncSessionLocal() as db:

        # ------------------------------------------------------------------
        # Users
        # ------------------------------------------------------------------
        users_data = [
            dict(email="supervisor@demo.com", username="supervisor", full_name="Sam Supervisor", role=UserRole.supervisor),
            dict(email="alice@demo.com",      username="alice",      full_name="Alice Chen",     role=UserRole.member),
            dict(email="bob@demo.com",        username="bob",        full_name="Bob Kim",        role=UserRole.member),
            dict(email="carol@demo.com",      username="carol",      full_name="Carol Davis",    role=UserRole.member),
        ]
        users: dict[str, User] = {}
        for ud in users_data:
            result = await db.execute(select(User).where(User.email == ud["email"]))
            u = result.scalar_one_or_none()
            if not u:
                u = User(
                    **ud,
                    hashed_password=hash_password("password123"),
                    is_active=True,
                )
                db.add(u)
                await db.flush()
                print(f"  created user: {ud['username']}")
            else:
                print(f"  skipped user (exists): {ud['username']}")
            users[ud["username"]] = u

        # ------------------------------------------------------------------
        # Projects
        # ------------------------------------------------------------------
        projects_data = [
            dict(name="TeamFlow Backend", color="#6366f1", description="API & database layer"),
            dict(name="Mobile App",       color="#f59e0b", description="iOS/Android client"),
        ]
        projects: list[Project] = []
        for pd in projects_data:
            result = await db.execute(select(Project).where(Project.name == pd["name"]))
            p = result.scalar_one_or_none()
            if not p:
                p = Project(**pd)
                db.add(p)
                await db.flush()
                print(f"  created project: {pd['name']}")
            else:
                print(f"  skipped project (exists): {pd['name']}")
            projects.append(p)

        proj_backend, proj_mobile = projects

        # ------------------------------------------------------------------
        # Milestones
        # ------------------------------------------------------------------
        ms_data = [
            dict(title="v1.0 Launch",    project=proj_backend, status=MilestoneStatus.in_progress,
                 start_date=_days(-30), due_date=_days(14)),
            dict(title="Auth & RBAC",    project=proj_backend, status=MilestoneStatus.completed,
                 start_date=_days(-60), due_date=_days(-10)),
            dict(title="MVP Release",    project=proj_mobile,  status=MilestoneStatus.planned,
                 start_date=_days(-5),  due_date=_days(30)),
            dict(title="Design System",  project=proj_mobile,  status=MilestoneStatus.in_progress,
                 start_date=_days(-20), due_date=_days(7)),
        ]
        milestones: list[Milestone] = []
        for md in ms_data:
            proj = md.pop("project")
            result = await db.execute(
                select(Milestone).where(Milestone.title == md["title"], Milestone.project_id == proj.id)
            )
            m = result.scalar_one_or_none()
            if not m:
                m = Milestone(**md, project_id=proj.id)
                db.add(m)
                await db.flush()
                print(f"  created milestone: {md['title']}")
            else:
                print(f"  skipped milestone (exists): {md['title']}")
            milestones.append(m)

        ms_launch, ms_auth, ms_mvp, ms_design = milestones

        # ------------------------------------------------------------------
        # Tasks
        # ------------------------------------------------------------------
        tasks_data = [
            # Backend / v1.0 Launch milestone
            dict(title="Set up CI/CD pipeline",        milestone=ms_launch,  project=proj_backend,
                 assignee=users["alice"],  status=TaskStatus.in_progress, priority=TaskPriority.high,
                 due_date=_days(10)),
            dict(title="Write API documentation",      milestone=ms_launch,  project=proj_backend,
                 assignee=users["bob"],    status=TaskStatus.todo,        priority=TaskPriority.medium,
                 due_date=_days(12)),
            dict(title="Performance load testing",     milestone=ms_launch,  project=proj_backend,
                 assignee=users["carol"],  status=TaskStatus.todo,        priority=TaskPriority.high,
                 due_date=_days(3)),
            dict(title="Fix overdue bug in scheduler", milestone=ms_launch,  project=proj_backend,
                 assignee=users["alice"],  status=TaskStatus.blocked,     priority=TaskPriority.critical,
                 due_date=_days(-3)),   # overdue
            # Backend / Auth & RBAC milestone (completed)
            dict(title="Implement JWT refresh tokens", milestone=ms_auth,    project=proj_backend,
                 assignee=users["bob"],    status=TaskStatus.done,        priority=TaskPriority.high,
                 due_date=_days(-12), completed_at=_days(-13)),
            dict(title="Role-based route guards",      milestone=ms_auth,    project=proj_backend,
                 assignee=users["carol"],  status=TaskStatus.done,        priority=TaskPriority.medium,
                 due_date=_days(-11), completed_at=_days(-11)),
            # Mobile / MVP Release milestone
            dict(title="Login screen UI",              milestone=ms_mvp,     project=proj_mobile,
                 assignee=users["alice"],  status=TaskStatus.in_progress, priority=TaskPriority.high,
                 due_date=_days(20)),
            dict(title="Push notification setup",      milestone=ms_mvp,     project=proj_mobile,
                 assignee=users["bob"],    status=TaskStatus.todo,        priority=TaskPriority.medium,
                 due_date=_days(25)),
            dict(title="App store listing copy",       milestone=ms_mvp,     project=proj_mobile,
                 assignee=users["carol"],  status=TaskStatus.todo,        priority=TaskPriority.low,
                 due_date=_days(28)),
            # Mobile / Design System milestone
            dict(title="Typography tokens",            milestone=ms_design,  project=proj_mobile,
                 assignee=users["carol"],  status=TaskStatus.done,        priority=TaskPriority.medium,
                 due_date=_days(-2), completed_at=_days(-3)),
            dict(title="Color palette finalization",   milestone=ms_design,  project=proj_mobile,
                 assignee=users["alice"],  status=TaskStatus.review,      priority=TaskPriority.medium,
                 due_date=_days(5)),
            dict(title="Icon library integration",     milestone=ms_design,  project=proj_mobile,
                 assignee=users["bob"],    status=TaskStatus.in_progress, priority=TaskPriority.low,
                 due_date=_days(6)),
            # Unassigned / no-milestone tasks (tests unscheduled bar + unassigned_tasks list)
            dict(title="Backlog: API versioning research", milestone=None, project=proj_backend,
                 assignee=None, status=TaskStatus.todo, priority=TaskPriority.low,
                 due_date=None),   # unscheduled — appears as dashed bar
            dict(title="Spike: offline mode feasibility",  milestone=None, project=proj_mobile,
                 assignee=users["bob"], status=TaskStatus.todo, priority=TaskPriority.medium,
                 due_date=None),   # unscheduled
        ]

        for td in tasks_data:
            milestone = td.pop("milestone")
            project   = td.pop("project")
            assignee  = td.pop("assignee")
            completed_at = td.pop("completed_at", None)

            result = await db.execute(
                select(Task).where(Task.title == td["title"])
            )
            t = result.scalar_one_or_none()
            if not t:
                t = Task(
                    **td,
                    milestone_id=milestone.id if milestone else None,
                    project_id=project.id,
                    assignee_id=assignee.id if assignee else None,
                    creator_id=users["supervisor"].id,
                    completed_at=completed_at,
                )
                db.add(t)
                print(f"  created task: {td['title']}")
            else:
                print(f"  skipped task (exists): {td['title']}")

        await db.commit()
        print("\nDone. Login with:")
        print("  supervisor / password123  (role: supervisor)")
        print("  alice      / password123  (role: member)")
        print("  bob        / password123  (role: member)")
        print("  carol      / password123  (role: member)")


if __name__ == "__main__":
    asyncio.run(main())
