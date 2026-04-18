# TeamFlow — Private Team & Personal Task Manager

A full-stack private project management app with AI integration.

**Stack:** SvelteKit + Bun · FastAPI (Python) · PostgreSQL · LiteLLM

---

## Features

- **Dashboard** — stats overview, upcoming milestones, recent tasks
- **Projects** — organize tasks and milestones under projects
- **Tasks** — create/assign/filter tasks with priority, status, due dates, tags
- **Milestones** — track releases and major deliverables with timeline progress
- **Team** — view team members and their assigned workload
- **My Schedule** — personal calendar with event creation (visual calendar view)
- **AI Assistant** — persistent chat with LiteLLM (supports OpenAI, Anthropic, Ollama, etc.)

---

## Local Development

### Prerequisites
- Python 3.11+
- Bun (`brew install oven-sh/bun/bun`)
- PostgreSQL (local or via Docker)

### 1. Start PostgreSQL (Docker)
```bash
docker compose up postgres -d
```

### 2. Backend
```bash
cd backend
cp .env.example .env        # edit with your DB URL and AI API key
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Tables are auto-created on startup via SQLAlchemy.

### 3. Frontend
```bash
cd frontend
bun install
bun run dev                 # runs on http://localhost:5173
```

### 4. Register your first user
Visit `http://localhost:5173/register` and create an account.

---

## AI Configuration

Edit `backend/.env` — set `AI_MODEL` to any LiteLLM-supported model:

| Provider | Example value |
|---|---|
| OpenAI | `gpt-4o` |
| Anthropic | `claude-3-5-sonnet-20241022` |
| Ollama (local) | `ollama/llama3` |
| Gemini | `gemini/gemini-1.5-pro` |

Set the corresponding API key env var (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.).

---

## Docker (Full Stack)

```bash
cp backend/.env.example backend/.env  # edit AI keys
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Project Structure

```
windsurf-project/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app + lifespan
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── auth.py          # JWT auth
│   │   ├── config.py        # Settings
│   │   ├── database.py      # Async DB engine
│   │   └── routers/         # auth, users, projects, tasks, milestones, schedules, ai, dashboard
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── routes/          # +page.svelte for each section
│   │   ├── lib/
│   │   │   ├── api.ts       # API client
│   │   │   ├── utils.ts     # Helpers
│   │   │   └── stores/      # auth store
│   │   └── app.css          # Tailwind base
│   ├── package.json
│   ├── bunfig.toml
│   └── Dockerfile
└── docker-compose.yml
```
