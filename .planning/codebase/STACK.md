# Technology Stack

## Frontend
- **Framework**: SvelteKit 2.5.7 with Svelte 5.0
- **Language**: TypeScript 5.4.5
- **Styling**: TailwindCSS 3.4.4, PostCSS, Autoprefixer
- **Build Tool**: Vite 6.0.0
- **Icons**: Lucide Svelte
- **UI Components**: svelte-sonner (toast notifications), svelte-dnd-action (drag & drop)
- **Date Handling**: date-fns
- **Package Manager**: Yarn 1.22.22
- **Adapter**: @sveltejs/adapter-node (for production)

## Backend
- **Framework**: FastAPI 0.115.0+
- **Language**: Python 3.x
- **Server**: Uvicorn with standard extras
- **Database**: PostgreSQL 16 (async via asyncpg)
- **ORM**: SQLAlchemy 2.0.36+ (async)
- **Migration Tool**: Alembic
- **Authentication**: JWT (python-jose), bcrypt
- **Validation**: Pydantic 2.10+, pydantic-settings
- **Task Scheduling**: APScheduler
- **AI Integration**: LiteLLM (supports OpenAI, Anthropic, Ollama)
- **HTTP Client**: httpx

## DevOps
- **Containerization**: Docker, Docker Compose
- **Database**: PostgreSQL 16 Alpine
