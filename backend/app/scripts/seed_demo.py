"""Seed demo data for local development / timeline verification.

Creates:
  - 1 supervisor user  (supervisor / password123)
  - 3 member users     (alice, bob, carol / password123)
  - 2 projects with distinct colors
  - 2 milestones per project
  - ~16 tasks spread across milestones and assignees, with varied
    statuses, due dates (past, present, future), and one unscheduled task
  - notifications for each user
  - chat messages across projects
  - schedules for each user
  - 1 pending team invite

Run from the backend directory:
    python -m app.scripts.seed_demo

Safe to re-run — skips creation if data already exists (checks by email).
"""

import asyncio
import secrets
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
        TaskStatus, TaskPriority, NotificationStatus, NotificationEventType,
        EventNotification, Schedule, ChatChannel, ChatChannelMember,
        ChatConversation, ChatMessage, TeamInvite, InviteStatus,
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

        # ------------------------------------------------------------------
        # Schedules
        # ------------------------------------------------------------------
        schedules_data = [
            dict(user=users["supervisor"], title="Sprint Planning",        start_time=_days(1),  end_time=_days(1)  + timedelta(hours=1),   color="#6366f1", description="Plan the upcoming sprint with the team"),
            dict(user=users["supervisor"], title="1:1 with Alice",         start_time=_days(2),  end_time=_days(2)  + timedelta(hours=1),   color="#f59e0b", description="Weekly check-in"),
            dict(user=users["supervisor"], title="Release Review",         start_time=_days(14), end_time=_days(14) + timedelta(hours=2),   color="#10b981", description="v1.0 launch review meeting"),
            dict(user=users["alice"],      title="API Design Session",     start_time=_days(1),  end_time=_days(1)  + timedelta(hours=2),   color="#6366f1", description="Design REST endpoints for mobile"),
            dict(user=users["alice"],      title="Code Review",            start_time=_days(3),  end_time=_days(3)  + timedelta(hours=1),   color="#f59e0b"),
            dict(user=users["bob"],        title="Backend Sync",           start_time=_days(1),  end_time=_days(1)  + timedelta(hours=1),   color="#6366f1"),
            dict(user=users["bob"],        title="Push Notification Spike", start_time=_days(5), end_time=_days(5)  + timedelta(hours=3),   color="#ef4444", description="Research FCM / APNS setup"),
            dict(user=users["carol"],      title="Design Review",          start_time=_days(2),  end_time=_days(2)  + timedelta(hours=1),   color="#a855f7", description="Review new color palette"),
            dict(user=users["carol"],      title="All Hands",              start_time=_days(7),  end_time=_days(7)  + timedelta(hours=1),   color="#10b981", all_day=False),
        ]
        schedule_objs: list[Schedule] = []
        for sd in schedules_data:
            user = sd.pop("user")
            result = await db.execute(
                select(Schedule).where(Schedule.title == sd["title"], Schedule.user_id == user.id)
            )
            s = result.scalar_one_or_none()
            if not s:
                s = Schedule(**sd, user_id=user.id)
                db.add(s)
                await db.flush()
                print(f"  created schedule: {sd['title']} for {user.username}")
            else:
                print(f"  skipped schedule (exists): {sd['title']}")
            schedule_objs.append(s)

        # ------------------------------------------------------------------
        # Event Notifications (reminders)
        # ------------------------------------------------------------------
        result = await db.execute(
            select(EventNotification).where(EventNotification.user_id == users["supervisor"].id)
        )
        if not result.scalars().first():
            notif_data = [
                # sent (past remind_at) — show immediately in the bell
                dict(user=users["supervisor"], title="Fix overdue bug is past due!",
                     event_type=NotificationEventType.task,    event_ref_id=1,
                     start_at=_days(-3), remind_at=_days(-3),  status=NotificationStatus.sent),
                dict(user=users["supervisor"], title="Reminder: Release Review in 15 min",
                     event_type=NotificationEventType.schedule, event_ref_id=schedule_objs[0].id,
                     start_at=_days(1),  remind_at=_now() - timedelta(minutes=5), status=NotificationStatus.sent),
                dict(user=users["alice"],      title="Reminder: Code Review starts soon",
                     event_type=NotificationEventType.schedule, event_ref_id=schedule_objs[4].id,
                     start_at=_days(3),  remind_at=_now() - timedelta(minutes=2), status=NotificationStatus.sent),
                dict(user=users["bob"],        title="Backend Sync starts in 15 min",
                     event_type=NotificationEventType.schedule, event_ref_id=schedule_objs[5].id,
                     start_at=_days(1),  remind_at=_now() - timedelta(minutes=1), status=NotificationStatus.sent),
                dict(user=users["carol"],      title="Design Review: reminder",
                     event_type=NotificationEventType.schedule, event_ref_id=schedule_objs[7].id,
                     start_at=_days(2),  remind_at=_now() - timedelta(minutes=3), status=NotificationStatus.sent),
                # pending (future remind_at) — activated by scheduler later
                dict(user=users["supervisor"], title="Sprint Planning starts in 15 min",
                     event_type=NotificationEventType.schedule, event_ref_id=schedule_objs[0].id,
                     start_at=_days(1),  remind_at=_days(1) - timedelta(minutes=15), status=NotificationStatus.pending),
                dict(user=users["alice"],      title="API Design Session in 15 min",
                     event_type=NotificationEventType.schedule, event_ref_id=schedule_objs[3].id,
                     start_at=_days(1),  remind_at=_days(1) - timedelta(minutes=15), status=NotificationStatus.pending),
            ]
            for nd in notif_data:
                user   = nd.pop("user")
                start  = nd.pop("start_at")
                status = nd.pop("status")
                db.add(EventNotification(
                    user_id=user.id,
                    event_type=nd["event_type"],
                    event_ref_id=nd["event_ref_id"],
                    title_cache=nd["title"],
                    start_at_cache=start,
                    remind_at=nd["remind_at"],
                    status=status,
                ))
            await db.flush()
            print("  created event notifications")
        else:
            print("  skipped notifications (exist)")

        # ------------------------------------------------------------------
        # Chat channels
        # ------------------------------------------------------------------
        channels_data = [
            dict(name="general",   description="Team-wide announcements and discussion"),
            dict(name="backend",   description="Backend engineering channel"),
            dict(name="design",    description="Design and frontend channel"),
            dict(name="random",    description="Off-topic and fun"),
        ]
        channels: dict[str, ChatChannel] = {}
        for cd in channels_data:
            result = await db.execute(select(ChatChannel).where(ChatChannel.name == cd["name"]))
            ch = result.scalar_one_or_none()
            if not ch:
                ch = ChatChannel(**cd, created_by=users["supervisor"].id)
                db.add(ch)
                await db.flush()
                print(f"  created channel: #{cd['name']}")
            else:
                print(f"  skipped channel (exists): #{cd['name']}")
            channels[cd["name"]] = ch

        # Add all users to general; relevant users to other channels
        memberships = [
            (channels["general"], [users["supervisor"], users["alice"], users["bob"], users["carol"]]),
            (channels["backend"], [users["supervisor"], users["alice"], users["bob"]]),
            (channels["design"],  [users["supervisor"], users["alice"], users["carol"]]),
            (channels["random"],  [users["supervisor"], users["alice"], users["bob"], users["carol"]]),
        ]
        for ch, members in memberships:
            for u in members:
                result = await db.execute(
                    select(ChatChannelMember).where(
                        ChatChannelMember.channel_id == ch.id,
                        ChatChannelMember.user_id == u.id,
                    )
                )
                if not result.scalar_one_or_none():
                    db.add(ChatChannelMember(channel_id=ch.id, user_id=u.id))
        await db.flush()

        # Channel messages
        result = await db.execute(
            select(ChatMessage).where(ChatMessage.channel_id == channels["general"].id)
        )
        if not result.scalars().first():
            msgs = [
                (users["supervisor"], channels["general"], "Hey team! Sprint 3 kicks off today. Check the board for your tasks."),
                (users["alice"],      channels["general"], "On it! I'll start with the CI/CD pipeline setup."),
                (users["bob"],        channels["general"], "I'll pick up the API documentation."),
                (users["carol"],      channels["general"], "Starting the performance load tests. Will update by EOD."),
                (users["supervisor"], channels["backend"],  "Alice, can you take a look at the scheduler bug? It's marked critical."),
                (users["alice"],      channels["backend"],  "Already on it — looks like a timezone edge case. Will have a fix by tomorrow."),
                (users["bob"],        channels["backend"],  "I can help review the fix once it's ready."),
                (users["alice"],      channels["design"],   "Color palette PR is up for review — link in the task."),
                (users["carol"],      channels["design"],   "Looks great! Left some comments on the contrast ratios."),
                (users["supervisor"], channels["random"],   "Anyone catch the game last night? 🏀"),
                (users["bob"],        channels["random"],   "Missed it — was deep in push notification docs 😅"),
                (users["carol"],      channels["random"],   "Same, deadline mode activated lol"),
            ]
            offset = 120
            for sender, ch, content in msgs:
                db.add(ChatMessage(
                    sender_id=sender.id,
                    channel_id=ch.id,
                    content=content,
                    created_at=_now() - timedelta(minutes=offset),
                ))
                offset -= 8
            await db.flush()
            print("  created channel messages")
        else:
            print("  skipped channel messages (exist)")

        # ------------------------------------------------------------------
        # Direct messages (supervisor <-> alice)
        # ------------------------------------------------------------------
        result = await db.execute(
            select(ChatConversation).where(
                ChatConversation.user_a_id == users["supervisor"].id,
                ChatConversation.user_b_id == users["alice"].id,
            )
        )
        dm = result.scalar_one_or_none()
        if not dm:
            dm = ChatConversation(
                user_a_id=users["supervisor"].id,
                user_b_id=users["alice"].id,
            )
            db.add(dm)
            await db.flush()
            dm_msgs = [
                (users["supervisor"], "Hey Alice, how's the scheduler bug coming along?"),
                (users["alice"],      "Almost done — it's a UTC vs local time mismatch. Fix ready for review shortly."),
                (users["supervisor"], "Great, that's the blocker for the release. Thanks!"),
                (users["alice"],      "No worries, I'll tag you in the PR."),
            ]
            offset = 45
            for sender, content in dm_msgs:
                db.add(ChatMessage(
                    sender_id=sender.id,
                    conversation_id=dm.id,
                    content=content,
                    created_at=_now() - timedelta(minutes=offset),
                ))
                offset -= 10
            await db.flush()
            print("  created DM conversation (supervisor <-> alice)")
        else:
            print("  skipped DM (exists)")

        # ------------------------------------------------------------------
        # Pending team invite
        # ------------------------------------------------------------------
        result = await db.execute(
            select(TeamInvite).where(TeamInvite.email == "newmember@demo.com")
        )
        if not result.scalar_one_or_none():
            db.add(TeamInvite(
                email="newmember@demo.com",
                role=UserRole.member,
                token=secrets.token_urlsafe(32),
                validation_code="482910",
                status=InviteStatus.pending,
                invited_by_id=users["supervisor"].id,
                expires_at=_days(3),
            ))
            await db.flush()
            print("  created pending invite: newmember@demo.com")
        else:
            print("  skipped invite (exists)")

        await db.commit()
        print("\nDone. Login with:")
        print("  supervisor / password123  (role: supervisor)")
        print("  alice      / password123  (role: member)")
        print("  bob        / password123  (role: member)")
        print("  carol      / password123  (role: member)")


if __name__ == "__main__":
    asyncio.run(main())
