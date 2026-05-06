# Functional Design Specification: TeamFlow Core System

**Version:** 1.0
**Date:** 2026-05-07
**Status:** Draft

## 1. Overview

TeamFlow is a private team task management platform designed for supervisors who need real control over their team's work. This document describes the core system architecture and functional requirements.

### 1.1 Purpose

Provide a comprehensive task management solution that:
- Enables supervisors to monitor team workload and performance
- Allows team members to track their work efficiently
- Offers real-time collaboration features
- Provides role-based visibility and access control
- Integrates AI for intelligent task management

### 1.2 Scope

This specification covers:
- Core system architecture
- Data models and relationships
- API design
- Authentication and authorization
- Real-time features
- Deployment architecture

### 1.3 Target Users

- **Supervisors:** Primary users who create projects, assign tasks, monitor team performance
- **Team Members (5-15 people):** Update task status, create tasks, collaborate
- **Managers:** Organization-wide visibility and cross-team management
- **Assistant Managers:** Shared supervision responsibilities

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                    (SvelteKit 5 + Bun)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Tasks   │  │ Projects │  │  Board   │  │ Schedule │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/WebSocket
                              │
┌─────────────────────────────────────────────────────────────┐
│                         Backend                             │
│                   (FastAPI + Python 3.13)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Auth    │  │   API    │  │ Services │  │  Models  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ SQLAlchemy (asyncpg)
                              │
┌─────────────────────────────────────────────────────────────┐
│                      PostgreSQL 16                          │
│       (Users, Tasks, Projects, Milestones, etc.)            │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

**Frontend:**
- SvelteKit 5 - Web framework
- Bun - JavaScript runtime and package manager
- TailwindCSS - Styling
- TypeScript - Type safety
- Playwright - E2E testing

**Backend:**
- FastAPI - Web framework
- Python 3.13 - Runtime
- SQLAlchemy 2.0 - ORM
- asyncpg - Async PostgreSQL driver
- Alembic - Database migrations
- Pydantic - Data validation
- LiteLLM - AI integration

**Infrastructure:**
- Azure Web App Service - Hosting
- Azure PostgreSQL - Database
- Azure Container Registry - Docker registry
- GitLab CI/CD - Continuous integration

### 2.3 Data Flow

1. **User Action** → Frontend Component
2. **API Call** → FastAPI Route Handler
3. **Business Logic** → Service Layer
4. **Database Operation** → SQLAlchemy Model
5. **Response** → Pydantic Schema → JSON
6. **Frontend Update** → Svelte Component

## 3. Core Data Models

### 3.1 User Model

```python
class User:
    id: int (PK)
    email: str (unique)
    username: str (unique)
    full_name: str
    hashed_password: str
    role: UserRole (member, supervisor, assistant_manager, manager)
    sub_team_id: int (FK to SubTeam)
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

**Relationships:**
- One-to-many with Task (as assignee)
- One-to-many with Task (as creator)
- Many-to-one with SubTeam
- One-to-many with StandupPost
- One-to-many with KnowledgeSession

### 3.2 Task Model

```python
class Task:
    id: int (PK)
    title: str
    description: str (optional)
    status: TaskStatus (todo, in_progress, review, done, blocked)
    priority: TaskPriority (low, medium, high, critical)
    type: TaskType (feature, bug, task, improvement)
    assignee_id: int (FK to User)
    creator_id: int (FK to User)
    project_id: int (FK to Project)
    milestone_id: int (FK to Milestone, optional)
    sprint_id: int (FK to Sprint, optional)
    custom_status_id: int (FK to CustomStatus, optional)
    due_date: date (optional)
    estimated_hours: int (optional)
    completed_at: datetime (optional)
    created_at: datetime
    updated_at: datetime
```

**Relationships:**
- Many-to-one with User (assignee)
- Many-to-one with User (creator)
- Many-to-one with Project
- Many-to-one with Milestone
- Many-to-one with Sprint
- Many-to-one with CustomStatus

### 3.3 Project Model

```python
class Project:
    id: int (PK)
    name: str
    description: str (optional)
    color: str
    sub_team_id: int (FK to SubTeam)
    created_at: datetime
    updated_at: datetime
```

**Relationships:**
- One-to-many with Task
- One-to-many with Milestone
- Many-to-one with SubTeam

### 3.4 Milestone Model

```python
class Milestone:
    id: int (PK)
    title: str
    description: str (optional)
    status: MilestoneStatus (planned, in_progress, completed)
    project_id: int (FK to Project)
    start_date: date
    due_date: date
    completed_at: datetime (optional)
    created_at: datetime
    updated_at: datetime
```

**Relationships:**
- Many-to-one with Project
- One-to-many with Task
- One-to-many with Sprint

### 3.5 SubTeam Model

```python
class SubTeam:
    id: int (PK)
    name: str
    supervisor_id: int (FK to User)
    created_at: datetime
    updated_at: datetime
```

**Relationships:**
- Many-to-one with User (supervisor)
- One-to-many with User (members)
- One-to-many with Project

## 4. API Design

### 4.1 RESTful Conventions

- Base URL: `/api/`
- Resource naming: Plural nouns (e.g., `/api/tasks/`)
- HTTP verbs: GET, POST, PATCH, DELETE
- Response format: JSON
- Error format: `{"detail": "error message"}`

### 4.2 Authentication

**JWT Cookie-based Authentication:**
- User logs in with email/password
- Server issues JWT token as HTTP-only cookie
- Token includes user ID and role
- Token expiration: 7 days (configurable)
- Refresh token: Not implemented (re-login required)

**Protected Endpoints:**
```python
@router.get("/api/tasks/")
async def list_tasks(
    current_user: User = Depends(get_current_user)
):
    # current_user is injected from JWT token
```

### 4.3 Rate Limiting

- Default: 30 requests per minute per user
- Configured per route
- Implemented using slowapi

### 4.4 Key Endpoints

**Tasks:**
- `GET /api/tasks/` - List tasks with filters
- `POST /api/tasks/` - Create task
- `GET /api/tasks/{id}` - Get task details
- `PATCH /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `POST /api/tasks/ai-parse` - AI task parsing
- `POST /api/tasks/ai-breakdown` - AI task breakdown

**Projects:**
- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}` - Get project details
- `PATCH /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

**Milestones:**
- `GET /api/milestones/` - List milestones
- `POST /api/milestones/` - Create milestone
- `GET /api/milestones/{id}` - Get milestone details
- `PATCH /api/milestones/{id}` - Update milestone
- `DELETE /api/milestones/{id}` - Delete milestone

**Dashboard:**
- `GET /api/dashboard/` - Get dashboard data (role-scoped)

**Performance:**
- `GET /api/performance/` - Get team KPI metrics

## 5. Real-Time Features

### 5.1 WebSocket Chat

**Endpoints:**
- `/ws/chat/{channel_id}` - Channel chat
- `/ws/dm/{user_id}` - Direct messaging

**Features:**
- Real-time message delivery
- Presence indicators (online/offline)
- Message history
- Typing indicators (future)

### 5.2 Real-Time Updates

**Notifications:**
- Task assignment notifications
- Due date reminders
- Status change notifications
- @mention notifications (future)

**Implementation:**
- Server-Sent Events (SSE) for notifications
- WebSocket for chat
- Polling fallback (not implemented)

## 6. AI Integration

### 6.1 LiteLLM Integration

**Supported Providers:**
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Ollama (local models)
- Google (Gemini)
- Other LiteLLM-supported providers

### 6.2 AI Features

**Task Parsing:**
- Natural language → task fields
- Extracts title, description, priority, due date
- Configurable via AI_MODEL environment variable

**Task Breakdown:**
- Feature description → subtasks
- Generates 3-8 subtasks
- Includes priority and estimated hours

**Project Summary:**
- Generates project status summary
- Identifies risks and blockers
- Suggests next actions

### 6.3 AI Configuration

```env
AI_MODEL=gpt-4o
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-...
```

## 7. Security

### 7.1 Authentication

- Password hashing with bcrypt
- JWT token validation
- HTTP-only cookie for token storage
- Session management via JWT

### 7.2 Authorization

Role-based access control (RBAC):
- **Manager:** Full access to all resources
- **Supervisor:** Access to own sub-team and supervised teams
- **Assistant Manager:** Same as supervisor
- **Member:** Access to own tasks and sub-team resources

### 7.3 Data Validation

- Pydantic schemas for request validation
- SQL injection prevention via SQLAlchemy
- XSS prevention via input sanitization
- CSRF protection via same-site cookies

### 7.4 Rate Limiting

- Per-user rate limits
- Per-endpoint configuration
- Configured via slowapi

## 8. Deployment Architecture

### 8.1 Container Architecture

```
┌─────────────────────────────────────┐
│         Docker Container            │
│                                     │
│  ┌──────────┐                       │
│  │   nginx  │ → Port 80 (public)   │
│  └────┬─────┘                       │
│       │                             │
│  ┌────▼─────┐                       │
│  │ uvicorn  │ → Port 8000 (internal)│
│  └──────────┘                       │
│       │                             │
│  ┌────▼─────┐                       │
│  │  FastAPI │                       │
│  └──────────┘                       │
└─────────────────────────────────────┘
```

### 8.2 Azure Deployment

**Components:**
- Azure App Service (B1, Linux)
- Azure Container Registry
- Azure Database for PostgreSQL (Flexible Server, B1ms)
- Azure Resource Group

**Deployment Pipeline:**
1. Push to main branch
2. GitLab CI builds Docker image via ACR
3. Pipeline updates App Service container image
4. Application restarts with new image

### 8.3 Environment Configuration

**Required Environment Variables:**
```env
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=64-char-hex
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-app.azurewebsites.net
AI_MODEL=gpt-4o
OPENAI_API_KEY=...
WEBSITES_PORT=80
```

## 9. Performance Considerations

### 9.1 Database Optimization

- Indexes on frequently queried columns
- Async database operations
- Connection pooling via SQLAlchemy
- Query optimization with joins

### 9.2 Frontend Optimization

- Lazy loading for large lists
- Pagination for task lists
- Code splitting via SvelteKit
- Static asset optimization via Bun

### 9.3 Caching Strategy

- No caching implemented (future enhancement)
- Consider Redis for session caching
- Consider CDN for static assets

## 10. Monitoring and Logging

### 10.1 Logging

- Structured logging with Python logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Logs to stdout (captured by Azure App Service)

### 10.2 Error Tracking

- HTTP error responses with status codes
- Error details in response body (development only)
- Sentry integration (future)

### 10.3 Performance Monitoring

- Response time tracking (future)
- Database query performance (future)
- Frontend performance metrics (future)

## 11. Future Enhancements

### 11.1 Planned Features

- Native mobile apps (iOS/Android)
- Multi-tenant SaaS mode
- Public API with webhooks
- Enhanced notification system
- Advanced reporting and analytics
- Integration with external tools (Jira, GitHub)

### 11.2 Technical Debt

- Add comprehensive test coverage
- Implement caching layer
- Add API documentation (OpenAPI/Swagger)
- Improve error handling and validation
- Add performance monitoring
- Implement backup and disaster recovery
