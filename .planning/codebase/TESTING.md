# Testing

## Frontend
- **Type Checking**: `svelte-check` with TypeScript
- **Command**: `yarn check` (runs `svelte-kit sync && svelte-check`)
- **No explicit test framework** detected in package.json

## Backend
- **No explicit test framework** detected in requirements.txt
- **Type Checking**: Could use mypy/pyright (not configured)

## Recommendations
The project would benefit from:
1. **Frontend**: Vitest or Playwright for component/integration testing
2. **Backend**: pytest with pytest-asyncio for API testing
3. **Type Checking**: Add mypy for Python type validation
4. **E2E Testing**: Playwright for full-stack testing
