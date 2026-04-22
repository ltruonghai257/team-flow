# Concerns & Issues

## Security
- **Secret Key**: Default `SECRET_KEY` in config.py is "change-me-in-production" - must be changed
- **Cookie Security**: `COOKIE_SECURE` defaults to `True` which may cause issues in local dev (cookies won't work over HTTP)
- **CORS**: Currently allows all methods/headers (`allow_methods=["*"]`, `allow_headers=["*"]`) - consider tightening

## Code Quality
- **No tests**: Project lacks test coverage
- **No type checking for Python**: No mypy or pyright configured
- **No linting config**: ESLint config not visible

## Configuration
- **Hardcoded credentials**: Database password "password" in docker-compose.yml
- **Environment variables**: Some required vars have empty defaults (API keys)

## Technical Debt
- **No migration setup**: Uses `Base.metadata.create_all()` in lifespan - fine for dev but not production
- **No WebSocket authentication flow**: Custom `get_user_from_cookie` suggests WebSocket auth challenges

## Missing Features
- **No rate limiting**: API endpoints unprotected
- **No input sanitization**: Beyond Pydantic validation
- **No API versioning**: All endpoints under `/api/*`

## Development Experience
- **Notification polling**: Uses polling instead of WebSocket push for notifications
- **No hot reload config visible**: Backend may not have auto-reload configured
