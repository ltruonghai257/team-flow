"""Seed demo data for local development.

Creates:
  - 2 sub-teams (Engineering Team, Product Team)
  - 1 manager, 2 supervisors, 1 assistant manager
  - members across both sub-teams (alice, bob, carol, latruonghai, doanduckien)
  - 1 StatusSet + 5 CustomStatuses (is_done semantics for KPI)
  - 2 projects (scoped to the sub-team)
  - 4 milestones
  - 2 sprints for reminder demo coverage
  - 3 knowledge sessions with scope-aware reminders
  - reminder settings + generated reminder notifications
  - KPI-targeted tasks per member producing realistic score distribution:
      Alice       ~92  Good
      Bob         ~73  Fair
      Carol       ~68  Fair
      La Truong Hai ~74  Fair
      Doan Duc Kien ~37  At Risk
  - Weekly board posts, appends, and summary
  - Standup template with custom field types and standup posts
  - Schedules, chat channels/messages, DMs, notifications, invite

Run from the backend directory:
    python -m app.scripts.seed_demo

Safe to re-run — clears app tables before reseeding.
"""

import asyncio
import secrets
from datetime import datetime, timedelta, timezone


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _days(n: float) -> datetime:
    return _now() + timedelta(days=n)


def _h(hours_ago: float) -> datetime:
    """Return a datetime that is `hours_ago` hours in the past."""
    return _now() - timedelta(hours=hours_ago)


async def _clear_database(db) -> None:
    from sqlalchemy import text

    # Check if users table exists
    try:
        result = await db.execute(
            text(
                "SELECT 1 FROM information_schema.tables WHERE table_name = 'users' LIMIT 1"
            )
        )
        has_users = result.scalar() is not None
    except:
        has_users = False

    if not has_users:
        return  # No tables exist, nothing to clear

    from app.database import Base

    table_names = ", ".join(
        f'"{table.name}"' for table in Base.metadata.tables.values()
    )
    if table_names:
        await db.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"))


async def _create_schema(db) -> None:
    from app.database import Base, engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main() -> None:
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models import (
        User,
        UserRole,
        SubTeam,
        SubTeamReminderSettings,
        StatusSet,
        StatusSetScope,
        CustomStatus,
        Project,
        Milestone,
        MilestoneStatus,
        Sprint,
        SprintStatus,
        Task,
        TaskStatus,
        TaskPriority,
        TaskType,
        NotificationStatus,
        NotificationEventType,
        EventNotification,
        KnowledgeSession,
        KnowledgeSessionType,
        Schedule,
        ChatChannel,
        ChatChannelMember,
        ChatConversation,
        ChatMessage,
        TeamInvite,
        InviteStatus,
        WeeklyPost,
        WeeklyPostAppend,
        WeeklyBoardSummary,
        StandupPost,
        StandupTemplate,
        StandupSettings,
    )
    from app.auth import hash_password
    from app.services.knowledge_sessions import (
        serialize_tags,
        sync_knowledge_session_notifications,
    )
    from app.services.reminder_notifications import (
        rebuild_milestone_reminders,
        rebuild_sprint_reminders,
    )

    async with AsyncSessionLocal() as db:
        await _create_schema(db)

        # ------------------------------------------------------------------
        # Users
        # ------------------------------------------------------------------
        users_data = [
            dict(
                email="manager@demo.com",
                username="manager",
                full_name="Morgan Manager",
                role=UserRole.manager,
            ),
            dict(
                email="supervisor@demo.com",
                username="supervisor",
                full_name="Sam Supervisor",
                role=UserRole.supervisor,
            ),
            dict(
                email="assistant@demo.com",
                username="assistant",
                full_name="Avery Assistant",
                role=UserRole.assistant_manager,
            ),
            dict(
                email="product.supervisor@demo.com",
                username="product_supervisor",
                full_name="Priya Product",
                role=UserRole.supervisor,
            ),
            dict(
                email="alice@demo.com",
                username="alice",
                full_name="Alice Chen",
                role=UserRole.member,
            ),
            dict(
                email="bob@demo.com",
                username="bob",
                full_name="Bob Kim",
                role=UserRole.member,
            ),
            dict(
                email="carol@demo.com",
                username="carol",
                full_name="Carol Davis",
                role=UserRole.member,
            ),
            dict(
                email="latruonghai@gmail.com",
                username="latruonghai",
                full_name="La Truong Hai",
                role=UserRole.member,
            ),
            dict(
                email="doanduckien.2001@gmail.com",
                username="doanduckien",
                full_name="Doan Duc Kien",
                role=UserRole.member,
            ),
        ]
        users: dict[str, User] = {}
        for ud in users_data:
            result = await db.execute(select(User).where(User.email == ud["email"]))
            u = result.scalar_one_or_none()
            if not u:
                u = User(
                    **ud, hashed_password=hash_password("password123"), is_active=True
                )
                db.add(u)
                await db.flush()
                print(f"  created user: {ud['username']}")
            else:
                print(f"  skipped user (exists): {ud['username']}")
            users[ud["username"]] = u

        # ------------------------------------------------------------------
        # Sub-teams
        # ------------------------------------------------------------------
        result = await db.execute(
            select(SubTeam).where(SubTeam.name == "Engineering Team")
        )
        sub_team = result.scalar_one_or_none()
        if not sub_team:
            sub_team = SubTeam(
                name="Engineering Team", supervisor_id=users["supervisor"].id
            )
            db.add(sub_team)
            await db.flush()
            print("  created sub-team: Engineering Team")
        else:
            print("  skipped sub-team (exists)")

        result = await db.execute(select(SubTeam).where(SubTeam.name == "Product Team"))
        product_sub_team = result.scalar_one_or_none()
        if not product_sub_team:
            product_sub_team = SubTeam(
                name="Product Team", supervisor_id=users["product_supervisor"].id
            )
            db.add(product_sub_team)
            await db.flush()
            print("  created sub-team: Product Team")
        else:
            print("  skipped sub-team (exists): Product Team")

        # Assign leaders and members to their sub-team scopes. Managers remain org-wide.
        for username in ("supervisor", "assistant", "alice", "bob", "latruonghai"):
            u = users[username]
            if u.sub_team_id != sub_team.id:
                u.sub_team_id = sub_team.id
        for username in ("product_supervisor", "carol", "doanduckien"):
            u = users[username]
            if u.sub_team_id != product_sub_team.id:
                u.sub_team_id = product_sub_team.id
        await db.flush()

        # ------------------------------------------------------------------
        # Reminder Settings
        # ------------------------------------------------------------------
        result = await db.execute(
            select(SubTeamReminderSettings).where(
                SubTeamReminderSettings.sub_team_id == sub_team.id
            )
        )
        reminder_settings = result.scalar_one_or_none()
        if not reminder_settings:
            reminder_settings = SubTeamReminderSettings(
                sub_team_id=sub_team.id,
                lead_time_days=2,
                sprint_reminders_enabled=True,
                milestone_reminders_enabled=True,
            )
            db.add(reminder_settings)
            await db.flush()
            print("  created reminder settings")
        else:
            print("  skipped reminder settings (exists)")

        # ------------------------------------------------------------------
        # StatusSet + CustomStatuses
        # ------------------------------------------------------------------
        result = await db.execute(
            select(StatusSet).where(
                StatusSet.scope == StatusSetScope.sub_team_default,
                StatusSet.sub_team_id == sub_team.id,
            )
        )
        status_set = result.scalar_one_or_none()
        if not status_set:
            status_set = StatusSet(
                scope=StatusSetScope.sub_team_default, sub_team_id=sub_team.id
            )
            db.add(status_set)
            await db.flush()
            print("  created status set")
        else:
            print("  skipped status set (exists)")

        cs_specs = [
            dict(name="To Do", slug="todo", color="#64748b", is_done=False, position=0),
            dict(
                name="In Progress",
                slug="in_progress",
                color="#3b82f6",
                is_done=False,
                position=1,
            ),
            dict(
                name="In Review",
                slug="in_review",
                color="#a855f7",
                is_done=False,
                position=2,
            ),
            dict(name="Done", slug="done", color="#22c55e", is_done=True, position=3),
            dict(
                name="Blocked",
                slug="blocked",
                color="#ef4444",
                is_done=False,
                position=4,
            ),
        ]
        cs: dict[str, CustomStatus] = {}
        for spec in cs_specs:
            result = await db.execute(
                select(CustomStatus).where(
                    CustomStatus.status_set_id == status_set.id,
                    CustomStatus.slug == spec["slug"],
                )
            )
            c = result.scalar_one_or_none()
            if not c:
                c = CustomStatus(**spec, status_set_id=status_set.id)
                db.add(c)
                await db.flush()
                print(f"  created custom status: {spec['name']}")
            else:
                print(f"  skipped custom status (exists): {spec['name']}")
            cs[spec["slug"]] = c

        # ------------------------------------------------------------------
        # Projects  (scoped to sub-team so KPI filters work)
        # ------------------------------------------------------------------
        projects_data = [
            dict(
                name="TeamFlow Backend",
                color="#6366f1",
                description="API & database layer",
            ),
            dict(name="Mobile App", color="#f59e0b", description="iOS/Android client"),
        ]
        projects: list[Project] = []
        for pd in projects_data:
            result = await db.execute(select(Project).where(Project.name == pd["name"]))
            p = result.scalar_one_or_none()
            if not p:
                p = Project(**pd, sub_team_id=sub_team.id)
                db.add(p)
                await db.flush()
                print(f"  created project: {pd['name']}")
            else:
                if p.sub_team_id != sub_team.id:
                    p.sub_team_id = sub_team.id
                print(f"  skipped project (exists): {pd['name']}")
            projects.append(p)

        proj_backend, proj_mobile = projects

        # ------------------------------------------------------------------
        # Milestones (Phase 27: added descriptions and completed_at for timeline clarity)
        # ------------------------------------------------------------------
        ms_data = [
            dict(
                title="v1.0 Launch",
                description="Production-ready team management platform with core features",
                project=proj_backend,
                status=MilestoneStatus.in_progress,
                start_date=_days(-30),
                due_date=_days(14),
            ),
            dict(
                title="Auth & RBAC",
                description="Authentication, authorization, and role-based access control system",
                project=proj_backend,
                status=MilestoneStatus.completed,
                start_date=_days(-60),
                due_date=_days(-10),
                completed_at=_days(-10),
            ),
            dict(
                title="MVP Release",
                description="Initial mobile app release with core user features",
                project=proj_mobile,
                status=MilestoneStatus.planned,
                start_date=_days(-5),
                due_date=_days(1),
            ),
            dict(
                title="Design System",
                description="Component library, typography, color palette, and design tokens",
                project=proj_mobile,
                status=MilestoneStatus.in_progress,
                start_date=_days(-20),
                due_date=_days(7),
            ),
        ]
        milestones: list[Milestone] = []
        for md in ms_data:
            proj = md.pop("project")
            result = await db.execute(
                select(Milestone).where(
                    Milestone.title == md["title"], Milestone.project_id == proj.id
                )
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
        # Sprints
        # ------------------------------------------------------------------
        sprints_data = [
            dict(
                name="Release Sprint",
                project=proj_backend,
                milestone=ms_launch,
                status=SprintStatus.active,
                start_date=_days(-6),
                end_date=_days(1),
            ),
            dict(
                name="Mobile Sprint",
                project=proj_mobile,
                milestone=ms_mvp,
                status=SprintStatus.active,
                start_date=_days(-4),
                end_date=_days(8),
            ),
        ]
        sprints: dict[str, Sprint] = {}
        for sd in sprints_data:
            milestone = sd.pop("milestone")
            sd.pop("project")
            result = await db.execute(
                select(Sprint).where(
                    Sprint.name == sd["name"],
                    Sprint.milestone_id == milestone.id,
                )
            )
            sprint = result.scalar_one_or_none()
            if not sprint:
                sprint = Sprint(**sd, milestone_id=milestone.id)
                db.add(sprint)
                await db.flush()
                print(f"  created sprint: {sd['name']}")
            else:
                print(f"  skipped sprint (exists): {sd['name']}")
            sprints[sd["name"]] = sprint

        # ------------------------------------------------------------------
        # Tasks
        #
        # Each task dict keys:
        #   title, project, milestone (opt), assignee (opt),
        #   priority, status (legacy), type (opt),
        #   custom_slug: key into cs dict
        #   due_date (opt), created_at_h: hours ago, completed_at_h (opt)
        #
        # KPI target scores (default weights 20/25/20/20/15):
        #   Alice       workload=100 vel=80  ct=100 ot=88  def=100  → ~92 Good
        #   Bob         workload=100 vel=60  ct=70  ot=67  def=70   → ~73 Fair
        #   Carol       workload=70  vel=40  ct=70  ot=75  def=100  → ~68 Fair
        #   La Truong Hai workload=100 vel=50 ct=70 ot=60  def=100  → ~74 Fair
        #   Doan Duc Kien workload=40 vel=30 ct=40  ot=33  def=40   → ~37 At Risk
        # ------------------------------------------------------------------
        tasks_raw = [
            # ── Alice Chen  (target ~92 Good) ─────────────────────────────
            # 3 active tasks → workload score 100
            dict(
                title="Set up CI/CD pipeline",
                description="Configure GitHub Actions for automated testing and deployment",
                tags="infrastructure,automation,devops",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["alice"],
                priority=TaskPriority.high,
                status=TaskStatus.in_progress,
                custom_slug="in_progress",
                due_date=_days(10),
                created_at_h=48,
            ),
            dict(
                title="Login screen UI",
                description="Design and implement the mobile app login interface with form validation",
                tags="mobile,ui,authentication",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["alice"],
                priority=TaskPriority.high,
                status=TaskStatus.in_progress,
                custom_slug="in_progress",
                due_date=_days(20),
                created_at_h=24,
            ),
            dict(
                title="Color palette finalization",
                description="Finalize the design system color palette with accessibility considerations",
                tags="design,accessibility,ui",
                project=proj_mobile,
                milestone=ms_design,
                assignee=users["alice"],
                priority=TaskPriority.medium,
                status=TaskStatus.review,
                custom_slug="in_review",
                due_date=_days(5),
                created_at_h=36,
            ),
            # 8 completed in 30d → velocity 80; avg cycle 36h → ct 100; 7/8 on-time → ot 88
            dict(
                title="JWT auth middleware",
                project=proj_backend,
                milestone=ms_auth,
                assignee=users["alice"],
                priority=TaskPriority.high,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=244,
                completed_at_h=208,
                due_date=_h(205),
            ),  # due after completion → on time
            dict(
                title="User registration flow",
                project=proj_backend,
                milestone=ms_auth,
                assignee=users["alice"],
                priority=TaskPriority.medium,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=220,
                completed_at_h=184,
                due_date=_h(180),
            ),  # on time
            dict(
                title="Password reset endpoint",
                project=proj_backend,
                milestone=ms_auth,
                assignee=users["alice"],
                priority=TaskPriority.medium,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=196,
                completed_at_h=160,
                due_date=_h(155),
            ),  # on time
            dict(
                title="OAuth2 token validation",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["alice"],
                priority=TaskPriority.high,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=172,
                completed_at_h=136,
                due_date=_h(130),
            ),  # on time
            dict(
                title="API rate limiting",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["alice"],
                priority=TaskPriority.medium,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=148,
                completed_at_h=112,
                due_date=_h(108),
            ),  # on time
            dict(
                title="Request logging middleware",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["alice"],
                priority=TaskPriority.low,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=124,
                completed_at_h=88,
                due_date=_h(84),
            ),  # on time
            dict(
                title="Health check endpoint",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["alice"],
                priority=TaskPriority.low,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=100,
                completed_at_h=64,
                due_date=_h(60),
            ),  # on time
            dict(
                title="Fix overdue scheduler bug",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["alice"],
                priority=TaskPriority.critical,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=76,
                completed_at_h=40,
                due_date=_h(48),
            ),  # LATE: due 48h ago, completed 40h ago → completed after due
            # ── Bob Kim  (target ~73 Fair) ────────────────────────────────
            # 7 active tasks → workload 100
            dict(
                title="Write API documentation",
                description="Create comprehensive API documentation using OpenAPI/Swagger specification",
                tags="documentation,api,swagger",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["bob"],
                priority=TaskPriority.medium,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(12),
                created_at_h=48,
            ),
            dict(
                title="Push notification setup",
                description="Integrate FCM and APNS for cross-platform push notifications",
                tags="mobile,notifications,integration",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["bob"],
                priority=TaskPriority.medium,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(25),
                created_at_h=36,
            ),
            dict(
                title="Icon library integration",
                description="Integrate and configure icon library for mobile app components",
                tags="mobile,ui,icons",
                project=proj_mobile,
                milestone=ms_design,
                assignee=users["bob"],
                priority=TaskPriority.low,
                status=TaskStatus.in_progress,
                custom_slug="in_progress",
                due_date=_days(6),
                created_at_h=24,
            ),
            dict(
                title="Backend Swagger docs",
                description="Generate and publish Swagger documentation for backend endpoints",
                tags="documentation,backend,api",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["bob"],
                priority=TaskPriority.low,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(15),
                created_at_h=12,
            ),
            dict(
                title="Database backup scripts",
                description="Create automated database backup and restore scripts",
                tags="infrastructure,database,devops",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["bob"],
                priority=TaskPriority.medium,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(18),
                created_at_h=8,
            ),
            dict(
                title="Error handling middleware",
                description="Implement centralized error handling and logging middleware",
                tags="backend,middleware,logging",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["bob"],
                priority=TaskPriority.medium,
                status=TaskStatus.in_progress,
                custom_slug="in_progress",
                due_date=_days(9),
                created_at_h=16,
            ),
            dict(
                title="App analytics integration",
                description="Integrate analytics SDK for user behavior tracking",
                tags="mobile,analytics,monitoring",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["bob"],
                priority=TaskPriority.low,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(22),
                created_at_h=4,
            ),
            # 6 completed in 30d → velocity 60; avg cycle ~63h → ct 70; 4/6 on-time; 1 bug MTTR 80h → def 70
            dict(
                title="Implement JWT refresh tokens",
                project=proj_backend,
                milestone=ms_auth,
                assignee=users["bob"],
                priority=TaskPriority.high,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=360,
                completed_at_h=300,  # cycle 60h
                due_date=_h(295),
            ),  # on time
            dict(
                title="Role-based route guards",
                project=proj_backend,
                milestone=ms_auth,
                assignee=users["bob"],
                priority=TaskPriority.medium,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=336,
                completed_at_h=276,  # cycle 60h
                due_date=_h(270),
            ),  # on time
            dict(
                title="Session invalidation logic",
                project=proj_backend,
                milestone=ms_auth,
                assignee=users["bob"],
                priority=TaskPriority.medium,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=312,
                completed_at_h=252,  # cycle 60h
                due_date=_h(248),
            ),  # on time
            dict(
                title="Token blacklist cache",
                project=proj_backend,
                milestone=ms_auth,
                assignee=users["bob"],
                priority=TaskPriority.low,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=288,
                completed_at_h=228,  # cycle 60h
                due_date=_h(230),
            ),  # LATE: due 230h ago, completed 228h ago → completed after due
            dict(
                title="Push payload schema",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["bob"],
                priority=TaskPriority.medium,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=264,
                completed_at_h=204,  # cycle 60h
                due_date=_h(210),
            ),  # LATE
            dict(
                title="Fix crash on null token",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["bob"],
                priority=TaskPriority.critical,
                status=TaskStatus.done,
                custom_slug="done",
                type=TaskType.bug,
                created_at_h=320,
                completed_at_h=240,  # cycle 80h = MTTR 80h
                due_date=_h(235),
            ),  # on time
            # ── Carol Davis  (target ~68 Fair) ────────────────────────────
            # 9 active tasks → workload 70
            dict(
                title="Performance load testing",
                description="Execute load testing to identify performance bottlenecks under stress",
                tags="testing,performance,qa",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["carol"],
                priority=TaskPriority.high,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(3),
                created_at_h=48,
            ),
            dict(
                title="App store listing copy",
                description="Write compelling app store description and marketing copy",
                tags="mobile,marketing,copywriting",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["carol"],
                priority=TaskPriority.low,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(28),
                created_at_h=24,
            ),
            dict(
                title="Onboarding flow wireframes",
                description="Create wireframes for user onboarding and tutorial flows",
                tags="mobile,ux,design",
                project=proj_mobile,
                milestone=ms_design,
                assignee=users["carol"],
                priority=TaskPriority.medium,
                status=TaskStatus.in_progress,
                custom_slug="in_progress",
                due_date=_days(8),
                created_at_h=36,
            ),
            dict(
                title="Accessibility audit",
                description="Conduct WCAG compliance audit and fix accessibility issues",
                tags="accessibility,qa,compliance",
                project=proj_mobile,
                milestone=ms_design,
                assignee=users["carol"],
                priority=TaskPriority.medium,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(10),
                created_at_h=12,
            ),
            dict(
                title="Localization strings",
                description="Extract and prepare strings for multi-language support",
                tags="mobile,i18n,localization",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["carol"],
                priority=TaskPriority.low,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(22),
                created_at_h=8,
            ),
            dict(
                title="Dark mode theme tokens",
                description="Define design tokens for dark mode color scheme",
                tags="design,ui,theming",
                project=proj_mobile,
                milestone=ms_design,
                assignee=users["carol"],
                priority=TaskPriority.medium,
                status=TaskStatus.in_progress,
                custom_slug="in_progress",
                due_date=_days(6),
                created_at_h=20,
            ),
            dict(
                title="Figma component export",
                description="Export design components from Figma to development format",
                tags="design,figma,handoff",
                project=proj_mobile,
                milestone=ms_design,
                assignee=users["carol"],
                priority=TaskPriority.low,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(14),
                created_at_h=6,
            ),
            dict(
                title="Sprint retrospective notes",
                description="Document sprint retrospective outcomes and action items",
                tags="process,agile,documentation",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["carol"],
                priority=TaskPriority.low,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(5),
                created_at_h=4,
            ),
            dict(
                title="QA test plan v2",
                description="Create comprehensive QA test plan for v2.0 release",
                tags="testing,qa,planning",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["carol"],
                priority=TaskPriority.medium,
                status=TaskStatus.in_progress,
                custom_slug="in_progress",
                due_date=_days(7),
                created_at_h=10,
            ),
            # 4 completed in 30d → velocity 40; avg cycle 100h → ct 70; 3/4 on-time → ot 75
            dict(
                title="Typography tokens",
                project=proj_mobile,
                milestone=ms_design,
                assignee=users["carol"],
                priority=TaskPriority.medium,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=400,
                completed_at_h=300,  # cycle 100h
                due_date=_h(295),
            ),  # on time
            dict(
                title="Button component library",
                project=proj_mobile,
                milestone=ms_design,
                assignee=users["carol"],
                priority=TaskPriority.medium,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=380,
                completed_at_h=280,  # cycle 100h
                due_date=_h(275),
            ),  # on time
            dict(
                title="Icon set finalization",
                project=proj_mobile,
                milestone=ms_design,
                assignee=users["carol"],
                priority=TaskPriority.low,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=360,
                completed_at_h=260,  # cycle 100h
                due_date=_h(255),
            ),  # on time
            dict(
                title="Spacing system doc",
                project=proj_mobile,
                milestone=ms_design,
                assignee=users["carol"],
                priority=TaskPriority.low,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=340,
                completed_at_h=240,  # cycle 100h
                due_date=_h(250),
            ),  # LATE: due 250h ago, completed 240h ago
            # ── La Truong Hai  (target ~74 Fair) ──────────────────────────
            # 5 active tasks → workload 100
            dict(
                title="API gateway config",
                description="Configure API gateway for rate limiting and routing",
                tags="infrastructure,api,gateway",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["latruonghai"],
                priority=TaskPriority.medium,
                status=TaskStatus.in_progress,
                custom_slug="in_progress",
                due_date=_days(8),
                created_at_h=48,
            ),
            dict(
                title="Mobile deep-link routing",
                description="Implement deep-link routing for mobile app navigation",
                tags="mobile,routing,deep-links",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["latruonghai"],
                priority=TaskPriority.medium,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(18),
                created_at_h=24,
            ),
            dict(
                title="Notification permission flow",
                description="Implement in-app notification permission request flow",
                tags="mobile,permissions,ux",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["latruonghai"],
                priority=TaskPriority.low,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(20),
                created_at_h=12,
            ),
            dict(
                title="Crash analytics setup",
                description="Integrate crash reporting SDK for production monitoring",
                tags="mobile,analytics,monitoring",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["latruonghai"],
                priority=TaskPriority.medium,
                status=TaskStatus.in_progress,
                custom_slug="in_progress",
                due_date=_days(12),
                created_at_h=16,
            ),
            dict(
                title="Search indexing spike",
                description="Research and prototype search indexing strategy",
                tags="research,search,spike",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["latruonghai"],
                priority=TaskPriority.low,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(15),
                created_at_h=8,
            ),
            # 5 completed in 30d → velocity 50; avg cycle 80h → ct 70; 3/5 on-time → ot 60
            dict(
                title="User profile endpoint",
                project=proj_backend,
                milestone=ms_auth,
                assignee=users["latruonghai"],
                priority=TaskPriority.medium,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=360,
                completed_at_h=280,  # cycle 80h
                due_date=_h(275),
            ),  # on time
            dict(
                title="Avatar upload service",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["latruonghai"],
                priority=TaskPriority.low,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=340,
                completed_at_h=260,  # cycle 80h
                due_date=_h(255),
            ),  # on time
            dict(
                title="Email verification flow",
                project=proj_backend,
                milestone=ms_auth,
                assignee=users["latruonghai"],
                priority=TaskPriority.medium,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=300,
                completed_at_h=220,  # cycle 80h
                due_date=_h(215),
            ),  # on time
            dict(
                title="Feed pagination logic",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["latruonghai"],
                priority=TaskPriority.low,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=280,
                completed_at_h=200,  # cycle 80h
                due_date=_h(210),
            ),  # LATE: due 210h ago, completed 200h ago
            dict(
                title="Websocket reconnect logic",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["latruonghai"],
                priority=TaskPriority.medium,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=260,
                completed_at_h=180,  # cycle 80h
                due_date=_h(190),
            ),  # LATE: due 190h ago, completed 180h ago
            # ── Doan Duc Kien  (target ~37 At Risk) ───────────────────────
            # 12 active tasks → workload 40
            dict(
                title="Multi-language support",
                description="Implement i18n framework and translation support",
                tags="mobile,i18n,localization",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["doanduckien"],
                priority=TaskPriority.medium,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(14),
                created_at_h=48,
            ),
            dict(
                title="Offline data sync",
                description="Implement offline data synchronization with conflict resolution",
                tags="mobile,offline,sync",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["doanduckien"],
                priority=TaskPriority.high,
                status=TaskStatus.in_progress,
                custom_slug="in_progress",
                due_date=_days(10),
                created_at_h=72,
            ),
            dict(
                title="Payment gateway integration",
                description="Integrate payment gateway SDK and checkout flow",
                tags="mobile,payments,integration",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["doanduckien"],
                priority=TaskPriority.critical,
                status=TaskStatus.blocked,
                custom_slug="blocked",
                due_date=_days(-2),
                created_at_h=96,
            ),
            dict(
                title="Biometric auth module",
                description="Implement fingerprint and face ID authentication",
                tags="mobile,security,biometrics",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["doanduckien"],
                priority=TaskPriority.high,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(20),
                created_at_h=24,
            ),
            dict(
                title="App theme switcher",
                description="Implement light/dark theme switcher with persistence",
                tags="mobile,ui,theming",
                project=proj_mobile,
                milestone=ms_design,
                assignee=users["doanduckien"],
                priority=TaskPriority.low,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(12),
                created_at_h=16,
            ),
            dict(
                title="Gesture navigation support",
                description="Add swipe gestures for navigation and actions",
                tags="mobile,ux,gestures",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["doanduckien"],
                priority=TaskPriority.medium,
                status=TaskStatus.in_progress,
                custom_slug="in_progress",
                due_date=_days(8),
                created_at_h=36,
            ),
            dict(
                title="Background task scheduler",
                description="Implement background task scheduling and execution",
                tags="backend,infrastructure,scheduling",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["doanduckien"],
                priority=TaskPriority.high,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(6),
                created_at_h=20,
            ),
            dict(
                title="File storage abstraction",
                description="Create abstraction layer for file storage providers",
                tags="backend,storage,infrastructure",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["doanduckien"],
                priority=TaskPriority.medium,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(9),
                created_at_h=12,
            ),
            dict(
                title="Video playback component",
                description="Implement video player component with streaming support",
                tags="mobile,video,media",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["doanduckien"],
                priority=TaskPriority.medium,
                status=TaskStatus.blocked,
                custom_slug="blocked",
                due_date=_days(-5),
                created_at_h=120,
            ),
            dict(
                title="Cache invalidation strategy",
                description="Design and implement cache invalidation strategy",
                tags="backend,performance,caching",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["doanduckien"],
                priority=TaskPriority.low,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(16),
                created_at_h=6,
            ),
            dict(
                title="Permissions matrix doc",
                description="Document role-based permission matrix and access rules",
                tags="documentation,security,rbac",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["doanduckien"],
                priority=TaskPriority.low,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=_days(11),
                created_at_h=4,
            ),
            dict(
                title="CDN config for assets",
                description="Configure CDN for static asset delivery",
                tags="infrastructure,cdn,performance",
                project=proj_backend,
                milestone=ms_launch,
                assignee=users["doanduckien"],
                priority=TaskPriority.medium,
                status=TaskStatus.in_progress,
                custom_slug="in_progress",
                due_date=_days(7),
                created_at_h=8,
            ),
            # 3 completed in 30d → velocity 30; avg cycle 160h → ct 40; 1/3 on-time → ot 33; bug MTTR 200h → def 40
            dict(
                title="App crash on startup fix",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["doanduckien"],
                priority=TaskPriority.critical,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=440,
                completed_at_h=300,  # cycle 140h
                due_date=_h(295),
            ),  # on time
            dict(
                title="Login timeout bug",
                project=proj_backend,
                milestone=ms_auth,
                assignee=users["doanduckien"],
                priority=TaskPriority.high,
                status=TaskStatus.done,
                custom_slug="done",
                created_at_h=420,
                completed_at_h=280,  # cycle 140h
                due_date=_h(290),
            ),  # LATE: due 290h ago, completed 280h ago
            dict(
                title="Memory leak in image loader",
                project=proj_mobile,
                milestone=ms_mvp,
                assignee=users["doanduckien"],
                priority=TaskPriority.high,
                status=TaskStatus.done,
                custom_slug="done",
                type=TaskType.bug,
                created_at_h=460,
                completed_at_h=260,  # cycle 200h = bug MTTR 200h
                due_date=_h(275),
            ),  # LATE: due 275h ago, completed 260h ago
            # ── Unassigned / backlog
            dict(
                title="Backlog: API versioning research",
                description="Research API versioning strategies and implementation approaches",
                tags="research,api,architecture",
                project=proj_backend,
                milestone=None,
                assignee=None,
                priority=TaskPriority.low,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=None,
                created_at_h=72,
            ),
            dict(
                title="Spike: offline mode feasibility",
                description="Spike to assess technical feasibility of offline mode",
                tags="spike,research,offline",
                project=proj_mobile,
                milestone=None,
                assignee=users["bob"],
                priority=TaskPriority.medium,
                status=TaskStatus.todo,
                custom_slug="todo",
                due_date=None,
                created_at_h=48,
            ),
        ]

        tasks_by_title: dict[str, Task] = {}
        for td in tasks_raw:
            project = td.pop("project")
            milestone = td.pop("milestone")
            assignee = td.pop("assignee")
            custom_slug = td.pop("custom_slug")
            created_at_h = td.pop("created_at_h", None)
            completed_at_h = td.pop("completed_at_h", None)
            task_type = td.pop("type", TaskType.task)

            result = await db.execute(select(Task).where(Task.title == td["title"]))
            t = result.scalar_one_or_none()
            if not t:
                t = Task(
                    **td,
                    type=task_type,
                    project_id=project.id,
                    milestone_id=milestone.id if milestone else None,
                    assignee_id=assignee.id if assignee else None,
                    creator_id=users["supervisor"].id,
                    custom_status_id=cs[custom_slug].id,
                    created_at=_h(created_at_h) if created_at_h else _now(),
                    completed_at=_h(completed_at_h) if completed_at_h else None,
                )
                db.add(t)
                print(f"  created task: {td['title']}")
            else:
                print(f"  skipped task (exists): {td['title']}")
            tasks_by_title[td["title"]] = t

        await db.flush()

        # Attach a few tasks to sprints so the reminder feature has demo data.
        result = await db.execute(
            select(Task).where(
                Task.title.in_(
                    [
                        "Set up CI/CD pipeline",
                        "Write API documentation",
                        "Error handling middleware",
                    ]
                )
            )
        )
        for task in result.scalars().all():
            task.sprint_id = sprints["Release Sprint"].id

        result = await db.execute(
            select(Task).where(
                Task.title.in_(
                    [
                        "Login screen UI",
                        "Push notification setup",
                        "Onboarding flow wireframes",
                    ]
                )
            )
        )
        for task in result.scalars().all():
            task.sprint_id = sprints["Mobile Sprint"].id

        await db.flush()

        # ------------------------------------------------------------------
        # Schedules
        # ------------------------------------------------------------------
        schedules_data = [
            dict(
                user=users["supervisor"],
                title="Sprint Planning",
                start_time=_days(1),
                end_time=_days(1) + timedelta(hours=1),
                color="#6366f1",
                description="Plan the upcoming sprint",
            ),
            dict(
                user=users["supervisor"],
                title="1:1 with Alice",
                start_time=_days(2),
                end_time=_days(2) + timedelta(hours=1),
                color="#f59e0b",
                description="Weekly check-in",
            ),
            dict(
                user=users["supervisor"],
                title="Release Review",
                start_time=_days(14),
                end_time=_days(14) + timedelta(hours=2),
                color="#10b981",
                description="v1.0 launch review",
            ),
            dict(
                user=users["alice"],
                title="API Design Session",
                start_time=_days(1),
                end_time=_days(1) + timedelta(hours=2),
                color="#6366f1",
                description="Design REST endpoints",
            ),
            dict(
                user=users["alice"],
                title="Code Review",
                start_time=_days(3),
                end_time=_days(3) + timedelta(hours=1),
                color="#f59e0b",
            ),
            dict(
                user=users["bob"],
                title="Backend Sync",
                start_time=_days(1),
                end_time=_days(1) + timedelta(hours=1),
                color="#6366f1",
            ),
            dict(
                user=users["bob"],
                title="Push Notification Spike",
                start_time=_days(5),
                end_time=_days(5) + timedelta(hours=3),
                color="#ef4444",
                description="Research FCM / APNS setup",
            ),
            dict(
                user=users["carol"],
                title="Design Review",
                start_time=_days(2),
                end_time=_days(2) + timedelta(hours=1),
                color="#a855f7",
                description="Review new color palette",
            ),
            dict(
                user=users["carol"],
                title="All Hands",
                start_time=_days(7),
                end_time=_days(7) + timedelta(hours=1),
                color="#10b981",
            ),
        ]
        schedule_objs: list[Schedule] = []
        for sd in schedules_data:
            user = sd.pop("user")
            result = await db.execute(
                select(Schedule).where(
                    Schedule.title == sd["title"], Schedule.user_id == user.id
                )
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
        # Knowledge Sessions
        # ------------------------------------------------------------------
        knowledge_sessions_data = [
            dict(
                topic="Architecture Review & Demo",
                description="Walk through the new API and data flow with the team.",
                references="Architecture notes, API contract doc, and demo checklist.",
                session_type=KnowledgeSessionType.demo,
                start_time=_days(2).replace(hour=10, minute=0, second=0, microsecond=0),
                duration_minutes=60,
                tags=["architecture", "demo"],
                presenter=users["supervisor"],
                sub_team_id=None,
                recipients=[u.id for u in users.values()],
                offsets=[15, 60],
            ),
            dict(
                topic="Frontend QA Workshop",
                description="Hands-on workshop to cover QA flows and edge cases.",
                references="QA checklist, staging URL, and test account list.",
                session_type=KnowledgeSessionType.workshop,
                start_time=_days(4).replace(hour=14, minute=0, second=0, microsecond=0),
                duration_minutes=90,
                tags=["qa", "frontend"],
                presenter=users["alice"],
                sub_team_id=sub_team.id,
                recipients=[
                    users["supervisor"].id,
                    users["alice"].id,
                    users["bob"].id,
                    users["carol"].id,
                    users["latruonghai"].id,
                    users["doanduckien"].id,
                ],
                offsets=[30, 1440],
            ),
            dict(
                topic="Release Q&A Office Hours",
                description="Open Q&A for release blockers, rollout timing, and support questions.",
                references="Release checklist, launch notes, and open questions board.",
                session_type=KnowledgeSessionType.qa,
                start_time=_days(7).replace(
                    hour=16, minute=30, second=0, microsecond=0
                ),
                duration_minutes=45,
                tags=["release", "qa"],
                presenter=users["bob"],
                sub_team_id=sub_team.id,
                recipients=[
                    users["supervisor"].id,
                    users["alice"].id,
                    users["bob"].id,
                    users["carol"].id,
                    users["latruonghai"].id,
                    users["doanduckien"].id,
                ],
                offsets=[15, 60],
            ),
        ]
        for kd in knowledge_sessions_data:
            result = await db.execute(
                select(KnowledgeSession).where(
                    KnowledgeSession.topic == kd["topic"],
                    KnowledgeSession.presenter_id == kd["presenter"].id,
                )
            )
            session = result.scalar_one_or_none()
            if not session:
                session = KnowledgeSession(
                    topic=kd["topic"],
                    description=kd["description"],
                    references=kd["references"],
                    session_type=kd["session_type"],
                    start_time=kd["start_time"],
                    duration_minutes=kd["duration_minutes"],
                    tags=serialize_tags(kd["tags"]),
                    presenter_id=kd["presenter"].id,
                    sub_team_id=kd["sub_team_id"],
                    created_by_id=users["supervisor"].id,
                )
                db.add(session)
                await db.flush()
                print(f"  created knowledge session: {kd['topic']}")
                await sync_knowledge_session_notifications(
                    db,
                    session,
                    kd["recipients"],
                    kd["offsets"],
                )
            else:
                print(f"  skipped knowledge session (exists): {kd['topic']}")

        # ------------------------------------------------------------------
        # Event Notifications
        # ------------------------------------------------------------------
        result = await db.execute(
            select(EventNotification).where(
                EventNotification.user_id == users["supervisor"].id,
                EventNotification.event_type == NotificationEventType.schedule,
                EventNotification.event_ref_id == schedule_objs[0].id,
            )
        )
        if not result.scalars().first():
            notif_data = [
                dict(
                    user=users["supervisor"],
                    title="Fix overdue bug is past due!",
                    event_type=NotificationEventType.task,
                    event_ref_id=tasks_by_title["Fix overdue scheduler bug"].id,
                    start_at=_days(-3),
                    remind_at=_days(-3),
                    status=NotificationStatus.sent,
                ),
                dict(
                    user=users["supervisor"],
                    title="Reminder: Release Review in 15 min",
                    event_type=NotificationEventType.schedule,
                    event_ref_id=schedule_objs[0].id,
                    start_at=_days(1),
                    remind_at=_now() - timedelta(minutes=5),
                    status=NotificationStatus.sent,
                ),
                dict(
                    user=users["alice"],
                    title="Reminder: Code Review starts soon",
                    event_type=NotificationEventType.schedule,
                    event_ref_id=schedule_objs[4].id,
                    start_at=_days(3),
                    remind_at=_now() - timedelta(minutes=2),
                    status=NotificationStatus.sent,
                ),
                dict(
                    user=users["bob"],
                    title="Backend Sync starts in 15 min",
                    event_type=NotificationEventType.schedule,
                    event_ref_id=schedule_objs[5].id,
                    start_at=_days(1),
                    remind_at=_now() - timedelta(minutes=1),
                    status=NotificationStatus.sent,
                ),
                dict(
                    user=users["carol"],
                    title="Design Review: reminder",
                    event_type=NotificationEventType.schedule,
                    event_ref_id=schedule_objs[7].id,
                    start_at=_days(2),
                    remind_at=_now() - timedelta(minutes=3),
                    status=NotificationStatus.sent,
                ),
                dict(
                    user=users["supervisor"],
                    title="Sprint Planning starts in 15 min",
                    event_type=NotificationEventType.schedule,
                    event_ref_id=schedule_objs[0].id,
                    start_at=_days(1),
                    remind_at=_days(1) - timedelta(minutes=15),
                    status=NotificationStatus.pending,
                ),
                dict(
                    user=users["alice"],
                    title="API Design Session in 15 min",
                    event_type=NotificationEventType.schedule,
                    event_ref_id=schedule_objs[3].id,
                    start_at=_days(1),
                    remind_at=_days(1) - timedelta(minutes=15),
                    status=NotificationStatus.pending,
                ),
            ]
            for nd in notif_data:
                user = nd.pop("user")
                start = nd.pop("start_at")
                status = nd.pop("status")
                db.add(
                    EventNotification(
                        user_id=user.id,
                        event_type=nd["event_type"],
                        event_ref_id=nd["event_ref_id"],
                        title_cache=nd["title"],
                        start_at_cache=start,
                        remind_at=nd["remind_at"],
                        status=status,
                    )
                )
            await db.flush()
            print("  created event notifications")
        else:
            print("  skipped notifications (exist)")

        await rebuild_sprint_reminders(db, sprints["Release Sprint"].id)
        await rebuild_sprint_reminders(db, sprints["Mobile Sprint"].id)
        await rebuild_milestone_reminders(db, ms_mvp.id)

        # ------------------------------------------------------------------
        # Chat channels
        # ------------------------------------------------------------------
        channels_data = [
            dict(name="general", description="Team-wide announcements and discussion"),
            dict(name="backend", description="Backend engineering channel"),
            dict(name="design", description="Design and frontend channel"),
            dict(name="random", description="Off-topic and fun"),
        ]
        channels: dict[str, ChatChannel] = {}
        for cd in channels_data:
            result = await db.execute(
                select(ChatChannel).where(ChatChannel.name == cd["name"])
            )
            ch = result.scalar_one_or_none()
            if not ch:
                ch = ChatChannel(**cd, created_by=users["supervisor"].id)
                db.add(ch)
                await db.flush()
                print(f"  created channel: #{cd['name']}")
            else:
                print(f"  skipped channel (exists): #{cd['name']}")
            channels[cd["name"]] = ch

        memberships = [
            (
                channels["general"],
                [
                    users["supervisor"],
                    users["alice"],
                    users["bob"],
                    users["carol"],
                    users["latruonghai"],
                    users["doanduckien"],
                ],
            ),
            (
                channels["backend"],
                [
                    users["supervisor"],
                    users["alice"],
                    users["bob"],
                    users["latruonghai"],
                    users["doanduckien"],
                ],
            ),
            (channels["design"], [users["supervisor"], users["alice"], users["carol"]]),
            (
                channels["random"],
                [
                    users["supervisor"],
                    users["alice"],
                    users["bob"],
                    users["carol"],
                    users["latruonghai"],
                    users["doanduckien"],
                ],
            ),
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

        result = await db.execute(
            select(ChatMessage).where(ChatMessage.channel_id == channels["general"].id)
        )
        if not result.scalars().first():
            msgs = [
                (
                    users["supervisor"],
                    channels["general"],
                    "Hey team! Sprint 3 kicks off today. Check the board for your tasks.",
                ),
                (
                    users["alice"],
                    channels["general"],
                    "On it! I'll start with the CI/CD pipeline setup.",
                ),
                (
                    users["bob"],
                    channels["general"],
                    "I'll pick up the API documentation.",
                ),
                (
                    users["carol"],
                    channels["general"],
                    "Starting the performance load tests. Will update by EOD.",
                ),
                (
                    users["latruonghai"],
                    channels["general"],
                    "Starting on the API gateway config today.",
                ),
                (
                    users["doanduckien"],
                    channels["general"],
                    "Working through the offline sync — it's complex but making progress.",
                ),
                (
                    users["supervisor"],
                    channels["backend"],
                    "Alice, can you take a look at the scheduler bug? It's marked critical.",
                ),
                (
                    users["alice"],
                    channels["backend"],
                    "Already on it — looks like a timezone edge case. Fix ready tomorrow.",
                ),
                (
                    users["bob"],
                    channels["backend"],
                    "I can help review the fix once it's ready.",
                ),
                (
                    users["latruonghai"],
                    channels["backend"],
                    "Finished the user profile endpoint — PR is up.",
                ),
                (
                    users["doanduckien"],
                    channels["backend"],
                    "Need help with the payment gateway integration — blocked on vendor docs.",
                ),
                (
                    users["alice"],
                    channels["design"],
                    "Color palette PR is up for review.",
                ),
                (
                    users["carol"],
                    channels["design"],
                    "Looks great! Left some comments on contrast ratios.",
                ),
                (
                    users["supervisor"],
                    channels["random"],
                    "Anyone catch the game last night? 🏀",
                ),
                (
                    users["bob"],
                    channels["random"],
                    "Missed it — was deep in push notification docs 😅",
                ),
                (
                    users["doanduckien"],
                    channels["random"],
                    "Same, too many tasks on my plate rn 😬",
                ),
            ]
            offset = 120
            for sender, ch, content in msgs:
                db.add(
                    ChatMessage(
                        sender_id=sender.id,
                        channel_id=ch.id,
                        content=content,
                        created_at=_now() - timedelta(minutes=offset),
                    )
                )
                offset -= 7
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
                user_a_id=users["supervisor"].id, user_b_id=users["alice"].id
            )
            db.add(dm)
            await db.flush()
            dm_msgs = [
                (
                    users["supervisor"],
                    "Hey Alice, how's the scheduler bug coming along?",
                ),
                (
                    users["alice"],
                    "Almost done — UTC vs local time mismatch. Fix ready for review shortly.",
                ),
                (
                    users["supervisor"],
                    "Great, that's the blocker for the release. Thanks!",
                ),
                (users["alice"], "No worries, I'll tag you in the PR."),
            ]
            offset = 45
            for sender, content in dm_msgs:
                db.add(
                    ChatMessage(
                        sender_id=sender.id,
                        conversation_id=dm.id,
                        content=content,
                        created_at=_now() - timedelta(minutes=offset),
                    )
                )
                offset -= 10
            await db.flush()
            print("  created DM: supervisor <-> alice")
        else:
            print("  skipped DM (exists)")

        # ------------------------------------------------------------------
        # Pending team invite
        # ------------------------------------------------------------------
        result = await db.execute(
            select(TeamInvite).where(TeamInvite.email == "newmember@demo.com")
        )
        if not result.scalar_one_or_none():
            db.add(
                TeamInvite(
                    email="newmember@demo.com",
                    role=UserRole.member,
                    token=secrets.token_urlsafe(32),
                    validation_code="482910",
                    status=InviteStatus.pending,
                    invited_by_id=users["supervisor"].id,
                    sub_team_id=sub_team.id,
                    expires_at=_days(3),
                )
            )
            await db.flush()
            print("  created pending invite: newmember@demo.com")
        else:
            print("  skipped invite (exists)")

        # ------------------------------------------------------------------
        # Weekly Board Posts
        # ------------------------------------------------------------------
        # Calculate current and last week using datetime
        now = _now()
        current_week_start = now - timedelta(days=now.weekday())
        last_week_start = current_week_start - timedelta(days=7)

        # Get ISO year and week
        current_iso_year = now.isocalendar()[0]
        current_iso_week = now.isocalendar()[1]
        last_week_date = last_week_start
        last_iso_year = last_week_date.isocalendar()[0]
        last_iso_week = last_week_date.isocalendar()[1]

        weekly_posts_data = [
            dict(
                author=users["alice"],
                sub_team=sub_team,
                iso_year=last_iso_year,
                iso_week=last_iso_week,
                week_start_date=last_week_start.date(),
                content="This week I focused on CI/CD pipeline setup and JWT auth middleware. Made good progress on the token refresh logic. Next week I'll tackle the API rate limiting and request logging.",
            ),
            dict(
                author=users["bob"],
                sub_team=sub_team,
                iso_year=last_iso_year,
                iso_week=last_iso_week,
                week_start_date=last_week_start.date(),
                content="Worked on API documentation and push notification setup. Completed the role-based route guards. Need to finish the session invalidation logic next week.",
            ),
            dict(
                author=users["carol"],
                sub_team=sub_team,
                iso_year=current_iso_year,
                iso_week=current_iso_week,
                week_start_date=current_week_start.date(),
                content="Started performance load testing and accessibility audit. Completed typography tokens and button component library. This week focusing on icon set finalization and spacing system.",
            ),
        ]

        weekly_posts: dict[str, WeeklyPost] = {}
        for wpd in weekly_posts_data:
            author = wpd.pop("author")
            sub_team = wpd.pop("sub_team")
            result = await db.execute(
                select(WeeklyPost).where(
                    WeeklyPost.author_id == author.id,
                    WeeklyPost.iso_year == wpd["iso_year"],
                    WeeklyPost.iso_week == wpd["iso_week"],
                )
            )
            wp = result.scalar_one_or_none()
            if not wp:
                wp = WeeklyPost(
                    author_id=author.id,
                    sub_team_id=sub_team.id,
                    **wpd,
                )
                db.add(wp)
                await db.flush()
                print(
                    f"  created weekly post for {author.username} (week {wpd['iso_year']}-{wpd['iso_week']})"
                )
            else:
                print(
                    f"  skipped weekly post (exists): {author.username} (week {wpd['iso_year']}-{wpd['iso_week']})"
                )
            weekly_posts[f"{author.username}_{wpd['iso_year']}-{wpd['iso_week']}"] = wp

        # Weekly Post Appends
        appends_data = [
            dict(
                post=weekly_posts[f"alice_{last_iso_year}-{last_iso_week}"],
                author=users["supervisor"],
                content="Great progress on the auth system! The token refresh logic is critical for security.",
            ),
            dict(
                post=weekly_posts[f"bob_{last_iso_year}-{last_iso_week}"],
                author=users["alice"],
                content="I can help review the session invalidation logic when you're ready.",
            ),
        ]

        for ad in appends_data:
            post = ad.pop("post")
            author = ad.pop("author")
            result = await db.execute(
                select(WeeklyPostAppend).where(
                    WeeklyPostAppend.post_id == post.id,
                    WeeklyPostAppend.author_id == author.id,
                )
            )
            append = result.scalar_one_or_none()
            if not append:
                append = WeeklyPostAppend(
                    post_id=post.id,
                    author_id=author.id,
                    **ad,
                )
                db.add(append)
                await db.flush()
                print(f"  created weekly post append by {author.username}")
            else:
                print(f"  skipped weekly post append (exists)")

        # Weekly Board Summary
        result = await db.execute(
            select(WeeklyBoardSummary).where(
                WeeklyBoardSummary.sub_team_id == sub_team.id,
                WeeklyBoardSummary.iso_year == last_iso_year,
                WeeklyBoardSummary.iso_week == last_iso_week,
            )
        )
        summary = result.scalar_one_or_none()
        if not summary:
            summary = WeeklyBoardSummary(
                sub_team_id=sub_team.id,
                iso_year=last_iso_year,
                iso_week=last_iso_week,
                week_start_date=last_week_start.date(),
                summary_text="Team made solid progress on authentication system and API infrastructure. CI/CD pipeline setup completed, with JWT auth middleware and token refresh logic implemented. Push notification research underway. Design team completed typography and button components. Blockers: Payment gateway integration blocked on vendor docs.",
                source_post_count=2,
                generated_by_mode="manual",
                generated_at=_now(),
            )
            db.add(summary)
            await db.flush()
            print(
                f"  created weekly board summary for week {last_iso_year}-{last_iso_week}"
            )
        else:
            print(f"  skipped weekly board summary (exists)")

        # ------------------------------------------------------------------
        # Standup Posts
        # ------------------------------------------------------------------
        # Check if standup template exists for sub-team
        result = await db.execute(
            select(StandupTemplate).where(StandupTemplate.sub_team_id == sub_team.id)
        )
        standup_template = result.scalar_one_or_none()
        if not standup_template:
            # Create template with custom field types
            standup_template = StandupTemplate(
                sub_team_id=sub_team.id,
                fields=[
                    "Pending Tasks",
                    "Future Tasks",
                    "Blockers",
                    "Need Help From",
                    "Critical Timeline",
                    "Release Date",
                ],
                field_types={
                    "Pending Tasks": "richtext",
                    "Future Tasks": "richtext",
                    "Blockers": "text",
                    "Need Help From": "text",
                    "Critical Timeline": "datetime",
                    "Release Date": "datetime",
                },
            )
            db.add(standup_template)
            await db.flush()
            print("  created standup template for sub-team")
        else:
            print("  skipped standup template (exists)")

        standup_posts_data = [
            dict(
                author=users["alice"],
                sub_team=sub_team,
                field_values={
                    "Pending Tasks": "CI/CD pipeline setup, API rate limiting",
                    "Future Tasks": "Request logging middleware, health check endpoint",
                    "Blockers": "None",
                    "Need Help From": "Bob for API documentation review",
                    "Critical Timeline": (_days(5)).isoformat(),
                    "Release Date": (_days(14)).isoformat(),
                },
                task_snapshot={"active": 3, "completed": 8, "blocked": 0},
            ),
            dict(
                author=users["bob"],
                sub_team=sub_team,
                field_values={
                    "Pending Tasks": "API documentation, push notification setup",
                    "Future Tasks": "Database backup scripts, error handling middleware",
                    "Blockers": "Waiting on vendor docs for payment gateway",
                    "Need Help From": "Alice for auth system review",
                    "Critical Timeline": (_days(7)).isoformat(),
                    "Release Date": (_days(18)).isoformat(),
                },
                task_snapshot={"active": 7, "completed": 6, "blocked": 1},
            ),
            dict(
                author=users["carol"],
                sub_team=sub_team,
                field_values={
                    "Pending Tasks": "Performance load testing, accessibility audit",
                    "Future Tasks": "App store listing copy, localization strings",
                    "Blockers": "None",
                    "Need Help From": "Alice for color palette review",
                    "Critical Timeline": (_days(3)).isoformat(),
                    "Release Date": (_days(10)).isoformat(),
                },
                task_snapshot={"active": 9, "completed": 4, "blocked": 0},
            ),
        ]

        for spd in standup_posts_data:
            author = spd.pop("author")
            sub_team = spd.pop("sub_team")
            result = await db.execute(
                select(StandupPost).where(
                    StandupPost.author_id == author.id,
                    StandupPost.created_at > _now() - timedelta(days=1),
                )
            )
            sp = result.scalar_one_or_none()
            if not sp:
                sp = StandupPost(
                    author_id=author.id,
                    sub_team_id=sub_team.id,
                    **spd,
                )
                db.add(sp)
                await db.flush()
                print(f"  created standup post for {author.username}")
            else:
                print(f"  skipped standup post (exists): {author.username}")

        await db.commit()
        print("\nDone. Login with:")
        print("  manager            / password123  (role: manager, org-wide)")
        print(
            "  supervisor         / password123  (role: supervisor, Engineering Team)"
        )
        print(
            "  assistant          / password123  (role: assistant_manager, Engineering Team)"
        )
        print("  product_supervisor / password123  (role: supervisor, Product Team)")
        print(
            "  alice              / password123  (role: member, Engineering Team, KPI ~92 Good)"
        )
        print(
            "  bob                / password123  (role: member, Engineering Team, KPI ~73 Fair)"
        )
        print(
            "  carol              / password123  (role: member, Product Team, KPI ~68 Fair)"
        )
        print(
            "  latruonghai        / password123  (role: member, Engineering Team, KPI ~74 Fair)"
        )
        print(
            "  doanduckien        / password123  (role: member, Product Team, KPI ~37 At Risk)"
        )


if __name__ == "__main__":
    asyncio.run(main())
