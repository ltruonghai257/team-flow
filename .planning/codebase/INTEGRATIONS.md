# Integrations & External Services

## Database
- **PostgreSQL 16** - Primary data store
- Connection: `postgresql+asyncpg://postgres:password@localhost:5432/taskmanager`
- Managed via SQLAlchemy async ORM

## Authentication
- **JWT-based** with HTTP-only cookies
- Token expiry: 10080 minutes (7 days)
- Algorithm: HS256
- Supports both cookie and bearer token authentication
- Password hashing: bcrypt

## AI Services (via LiteLLM)
- **OpenAI**: GPT-4o (default)
- **Anthropic**: Claude models supported
- **Ollama**: Local models supported (e.g., llama3)
- Configuration via environment variables:
  - `OPENAI_API_KEY`
  - `ANTHROPIC_API_KEY`
  - `AI_MODEL`

## Frontend-Backend Communication
- REST API over HTTP
- WebSocket support for real-time features
- CORS enabled for localhost development ports:
  - 5173 (Vite dev)
  - 4173 (Vite preview)
  - 3000 (Production)
