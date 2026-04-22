# Coding Conventions

## Frontend (TypeScript/Svelte)
- **Language Level**: TypeScript with strict mode
- **tsconfig**: Strict mode enabled, JS type checking enabled
- **Linting**: ESLint (implied by SvelteKit)
- **Formatting**: Prettier (via SvelteKit)
- **Style**: TailwindCSS for styling
- **Component Style**: Svelte 5 runes (`$state`, `$derived`)
- **Imports**: Absolute imports via `$lib` alias

### Scripts
```json
{
  "dev": "vite dev",
  "build": "vite build",
  "preview": "vite preview",
  "check": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json"
}
```

## Backend (Python)
- **Framework**: FastAPI with async/await
- **Type Hints**: Full type annotation usage
- **Validation**: Pydantic v2 for request/response models
- **Database**: Async SQLAlchemy 2.0+ patterns
- **Error Handling**: HTTPException with proper status codes

### Dependencies
- fastapi >= 0.115.0
- sqlalchemy >= 2.0.36
- pydantic >= 2.10.0
- pydantic-settings >= 2.6.0
- python-jose for JWT
- bcrypt for password hashing

## General
- **Environment**: Configuration via `.env` files
- **Secrets**: Never commit secrets (`.env` in `.gitignore`)
- **API Design**: RESTful with proper HTTP methods and status codes
