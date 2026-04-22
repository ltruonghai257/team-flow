# Architecture

## Overview
TeamFlow is a full-stack task management application with AI assistance. It follows a traditional client-server architecture with a FastAPI backend and SvelteKit frontend.

## Backend Architecture
- **Pattern**: Router-based API organization
- **Database**: Async SQLAlchemy with connection pooling
- **Authentication**: Dependency injection via FastAPI Depends
- **State Management**: Request-scoped sessions with automatic commit/rollback

### API Routers
- `/api/auth` - Authentication (register, login, logout, me)
- `/api/users` - User management
- `/api/projects` - Project CRUD
- `/api/milestones` - Milestone management
- `/api/tasks` - Task management with AI parsing
- `/api/schedules` - Schedule/calendar events
- `/api/notifications` - Notification management
- `/api/ai` - AI chat and conversations
- `/api/dashboard` - Dashboard data
- `/api/chat` - Chat functionality
- `/ws` - WebSocket for real-time

### Data Flow
1. Request arrives at FastAPI router
2. Dependency injection provides authenticated user and DB session
3. Router processes request, interacts with models
4. Response serialized via Pydantic schemas
5. Session auto-commits on success, auto-rollbacks on error

## Frontend Architecture
- **Pattern**: SvelteKit file-based routing
- **State Management**: Svelte stores (writable, derived)
- **API Client**: Centralized in `$lib/api.ts`
- **Authentication**: Cookie-based with store synchronization

### Key Stores
- `authStore` - User authentication state
- `notificationStore` - Real-time notifications with polling

### Routes
- `/` - Dashboard
- `/projects` - Project list
- `/tasks` - Task management
- `/milestones` - Milestone tracking
- `/team` - Team management
- `/schedule` - Calendar/scheduler
- `/ai` - AI Assistant
- `/login`, `/register` - Auth pages
