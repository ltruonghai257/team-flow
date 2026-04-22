# Directory Structure

```
windsurf-project/
|-- backend/
|   |-- app/
|   |   |-- __init__.py
|   |   |-- main.py              # FastAPI app entry point
|   |   |-- config.py            # Settings configuration
|   |   |-- database.py          # SQLAlchemy setup
|   |   |-- auth.py              # Auth utilities & dependencies
|   |   |-- models.py            # SQLAlchemy models
|   |   |-- schemas.py           # Pydantic schemas
|   |   |-- routers/             # API route modules
|   |   |   |-- ai.py
|   |   |   |-- auth.py
|   |   |   |-- chat.py
|   |   |   |-- dashboard.py
|   |   |   |-- milestones.py
|   |   |   |-- notifications.py
|   |   |   |-- projects.py
|   |   |   |-- schedules.py
|   |   |   |-- tasks.py
|   |   |   |-- users.py
|   |   |   |-- websocket.py
|   |   |-- scheduler_jobs.py    # APScheduler jobs
|   |-- requirements.txt
|   |-- Dockerfile
|   |-- .env
|
|-- frontend/
|   |-- src/
|   |   |-- app.css              # Global styles
|   |   |-- app.html             # HTML template
|   |   |-- lib/
|   |   |   |-- api.ts           # API client
|   |   |   |-- stores/          # Svelte stores
|   |   |   |   |-- auth.ts
|   |   |   |   |-- notifications.ts
|   |   |   |-- components/      # Reusable components
|   |   |-- routes/              # SvelteKit routes
|   |       |-- +layout.svelte   # Main layout with nav
|   |       |-- +page.svelte     # Dashboard
|   |       |-- login/
|   |       |-- register/
|   |       |-- projects/
|   |       |-- tasks/
|   |       |-- milestones/
|   |       |-- team/
|   |       |-- schedule/
|   |       |-- ai/
|   |-- package.json
|   |-- svelte.config.js
|   |-- vite.config.ts
|   |-- tailwind.config.js
|   |-- tsconfig.json
|
|-- docker-compose.yml
|-- README.md
```

## Key Patterns
- Backend uses `app/` as Python package root
- Frontend uses `$lib` alias pointing to `src/lib`
- API routes follow RESTful conventions
- Frontend routes mirror backend API structure
