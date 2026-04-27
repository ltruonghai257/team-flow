# Structure

*Mapped: 2026-04-22*

## Directory Layout

```
windsurf-project/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py             # App factory, router registration, lifespan
│   │   ├── config.py           # Settings (pydantic-settings, .env)
│   │   ├── database.py         # SQLAlchemy async engine + session factory
│   │   ├── models.py           # All SQLAlchemy ORM models
│   │   ├── schemas.py          # Pydantic request/response schemas
│   │   ├── auth.py             # JWT creation, cookie/bearer auth dependencies
│   │   ├── scheduler_jobs.py   # APScheduler background jobs
│   │   ├── routers/            # One file per domain (11 routers)
│   │   │   ├── ai.py
│   │   │   ├── auth.py
│   │   │   ├── chat.py
│   │   │   ├── dashboard.py
│   │   │   ├── milestones.py
│   │   │   ├── notifications.py
│   │   │   ├── projects.py
│   │   │   ├── schedules.py
│   │   │   ├── tasks.py
│   │   │   ├── users.py
│   │   │   └── websocket.py
│   │   └── websocket/
│   │       └── manager.py      # ConnectionManager singleton
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # SvelteKit frontend
│   ├── src/
│   │   ├── app.html            # HTML shell
│   │   ├── app.css             # Global CSS (Tailwind imports)
│   │   ├── lib/
│   │   │   ├── api.ts          # Typed fetch wrapper (all API calls)
│   │   │   ├── utils.ts        # Shared utilities
│   │   │   ├── websocket.ts    # WebSocket client singleton
│   │   │   ├── stores/
│   │   │   │   ├── auth.ts     # Auth state store
│   │   │   │   ├── chat.ts     # Chat state store
│   │   │   │   └── notifications.ts  # Notification polling store
│   │   │   └── components/
│   │   │       ├── NotificationBell.svelte
│   │   │       ├── chat/
│   │   │       │   └── UserPresenceIndicator.svelte
│   │   │       ├── statuses/                 # Status-set management and transition rules
│   │   │       │   ├── StatusSetManager.svelte
│   │   │       │   ├── StatusTransitionEditor.svelte
│   │   │       │   └── StatusTransitionPreview.svelte
│   │   │       └── tasks/
│   │   │           ├── AgileView.svelte      # Sprint board view
│   │   │           ├── AiTaskInput.svelte    # Natural language task creation
│   │   │           ├── KanbanBoard.svelte    # Drag-and-drop kanban
│   │   │           └── KanbanCard.svelte     # Task card
│   │   └── routes/
│   │       ├── +layout.svelte   # Root layout (sidebar nav, auth guard)
│   │       ├── +page.svelte     # Dashboard
│   │       ├── ai/+page.svelte
│   │       ├── login/+page.svelte
│   │       ├── milestones/+page.svelte
│   │       ├── projects/+page.svelte
│   │       ├── register/+page.svelte
│   │       ├── schedule/+page.svelte
│   │       ├── tasks/+page.svelte
│   │       └── team/+page.svelte
│   ├── package.json
│   ├── svelte.config.js        # adapter-node
│   ├── vite.config.ts          # Proxy config for /api, /ws
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── openspec/                   # OpenSpec change management
│   ├── config.yaml
│   ├── changes/                # Active + archived change specs
│   └── specs/                  # Global spec library
│
├── src/lib/components/         # Root-level src (appears partially duplicated/unused)
│   └── tasks/                  # Empty — likely a leftover artifact
│
├── docker-compose.yml          # Full-stack dev/prod orchestration
├── package.json                # Root (no scripts — likely workspace root)
├── README.md
└── .gitignore
```

## Key Locations

| What | Where |
|------|-------|
| App entry (backend) | `backend/app/main.py` |
| All DB models | `backend/app/models.py` |
| All API schemas | `backend/app/schemas.py` |
| Auth logic | `backend/app/auth.py` |
| Environment config | `backend/app/config.py` + `backend/.env` |
| WebSocket hub | `backend/app/websocket/manager.py` |
| API client (frontend) | `frontend/src/lib/api.ts` |
| WS client (frontend) | `frontend/src/lib/websocket.ts` |
| Auth store (frontend) | `frontend/src/lib/stores/auth.ts` |
| Root layout / nav | `frontend/src/routes/+layout.svelte` |
| Docker orchestration | `docker-compose.yml` |

## Naming Conventions

- **Backend files**: snake_case Python modules, one router per domain
- **Frontend files**: PascalCase for `.svelte` components, camelCase for `.ts` modules
- **Routes**: lowercase directory names matching URL paths
- **Stores**: named `*Store` (e.g. `authStore`, `notificationStore`)
- **API modules**: named by resource domain (`auth`, `tasks`, `projects`, etc.)

## Notable Structural Issues

- `src/lib/components/tasks/` at root level — appears to be a leftover from project scaffolding, not used by frontend
- Root `package.json` / `yarn.lock` at top level — no scripts defined; frontend has its own `package.json`
- No test directories found in either backend or frontend
- No Alembic `migrations/` directory — schema managed via `create_all`
