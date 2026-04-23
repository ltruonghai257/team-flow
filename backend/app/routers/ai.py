import re
from datetime import datetime, timedelta, timezone
from typing import List

import litellm
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.limiter import limiter
from app.models import AIConversation, AIMessage, Milestone, MilestoneStatus, Project, Task, TaskStatus, User
from app.schemas import AIConversationOut, AIMessageCreate, AIMessageOut, ProjectSummaryRequest, ProjectSummaryResponse, ProjectSummarySections

router = APIRouter(prefix="/api/ai", tags=["ai"])

_INTENT_PATTERNS = [
    r"summarize project\s+(.+?)(?:\?|$)",
    r"project\s+(.+?)\s+summary",
    r"project\s+status\s+(?:for\s+)?(.+?)(?:\?|$)",
    r"how is (?:project )?(.+?)(?:\?|$)",
    r"summarize project",
    r"project status",
]


def _extract_project_name(content: str) -> str | None:
    """Return extracted project name from intent patterns, '' for match without capture, None for no match."""
    for pattern in _INTENT_PATTERNS:
        m = re.search(pattern, content, re.IGNORECASE)
        if m:
            return m.group(1).strip() if m.lastindex else ""
    return None


async def _fetch_project_summary_data(db: AsyncSession, project_id: int) -> dict:
    """Fetch project data for AI summary injection. Reused by endpoint and chat intent."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    seven_days_ago = now - timedelta(days=7)
    forty_eight_hours_later = now + timedelta(hours=48)

    project = await db.get(Project, project_id)
    if not project:
        return {}

    milestones_result = await db.execute(
        select(Milestone).where(Milestone.project_id == project_id)
    )
    milestones = milestones_result.scalars().all()
    total_milestones = len(milestones)
    completed_milestones = sum(1 for m in milestones if m.status == MilestoneStatus.completed)
    active_milestone = next((m.title for m in milestones if m.status == MilestoneStatus.in_progress), None)

    tasks_result = await db.execute(
        select(Task).where(Task.project_id == project_id)
    )
    all_tasks = tasks_result.scalars().all()

    recently_completed = [
        t for t in all_tasks
        if t.completed_at and t.completed_at >= seven_days_ago
    ]
    overdue = [
        t for t in all_tasks
        if t.due_date and t.due_date < now and t.status != TaskStatus.done
    ]
    at_risk = [
        t for t in all_tasks
        if t.due_date and now <= t.due_date <= forty_eight_hours_later and t.status != TaskStatus.done
    ]

    return {
        "project_name": project.name,
        "milestones_total": total_milestones,
        "milestones_completed": completed_milestones,
        "active_milestone": active_milestone,
        "recently_completed": [t.title for t in recently_completed],
        "overdue": [{"title": t.title, "due": t.due_date.strftime("%Y-%m-%d")} for t in overdue],
        "at_risk": [{"title": t.title, "due": t.due_date.strftime("%Y-%m-%d")} for t in at_risk],
    }


def _build_summary_context_block(data: dict) -> str:
    """Build a text block from project summary data for injection into AI context."""
    active = f", active: {data['active_milestone']}" if data.get("active_milestone") else ""
    overdue_str = ", ".join(f"{o['title']} due {o['due']}" for o in data["overdue"][:5])
    at_risk_str = ", ".join(f"{a['title']} due {a['due']}" for a in data["at_risk"][:5])
    recent_str = ", ".join(data["recently_completed"][:5])
    return (
        f"[Project context]\n"
        f"Project: {data['project_name']} | "
        f"Milestones: {data['milestones_completed']}/{data['milestones_total']} complete{active} | "
        f"Overdue tasks: {len(data['overdue'])} ({overdue_str or 'none'}) | "
        f"Completed this week: {len(data['recently_completed'])} tasks ({recent_str or 'none'}) | "
        f"Due within 48h: {at_risk_str or 'none'}"
    )


SYSTEM_PROMPT = """You are a helpful project management assistant. You help users manage their tasks, 
team members, project milestones, and schedules. You can provide insights, suggest priorities, 
help write task descriptions, summarize project status, and answer questions about project management 
best practices. Be concise, practical, and action-oriented."""


@router.get("/conversations", response_model=List[AIConversationOut])
@limiter.limit("30/minute")
async def list_conversations(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(AIConversation)
        .where(AIConversation.user_id == current_user.id)
        .options(selectinload(AIConversation.messages))
        .order_by(AIConversation.updated_at.desc())
    )
    return result.scalars().all()


@router.post("/conversations", response_model=AIConversationOut, status_code=201)
@limiter.limit("30/minute")
async def create_conversation(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conv = AIConversation(user_id=current_user.id, title="New Conversation")
    db.add(conv)
    await db.flush()
    await db.refresh(conv, ["messages"])
    return conv


@router.get("/conversations/{conv_id}", response_model=AIConversationOut)
@limiter.limit("30/minute")
async def get_conversation(
    request: Request,
    conv_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(AIConversation)
        .where(AIConversation.id == conv_id, AIConversation.user_id == current_user.id)
        .options(selectinload(AIConversation.messages))
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.delete("/conversations/{conv_id}", status_code=204)
@limiter.limit("30/minute")
async def delete_conversation(
    request: Request,
    conv_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(AIConversation).where(AIConversation.id == conv_id, AIConversation.user_id == current_user.id)
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await db.delete(conv)
    await db.flush()


@router.post("/conversations/{conv_id}/messages", response_model=AIMessageOut)
@limiter.limit("30/minute")
async def send_message(
    request: Request,
    conv_id: int,
    payload: AIMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(AIConversation)
        .where(AIConversation.id == conv_id, AIConversation.user_id == current_user.id)
        .options(selectinload(AIConversation.messages))
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    user_msg = AIMessage(conversation_id=conv_id, role="user", content=payload.content)
    db.add(user_msg)
    await db.flush()

    # Chat intent routing: detect project summary requests and inject data
    injected_context = ""
    project_name_query = _extract_project_name(payload.content)
    if project_name_query is not None:
        all_projects_result = await db.execute(select(Project))
        all_projects = all_projects_result.scalars().all()
        if project_name_query:
            matches = [p for p in all_projects if project_name_query.lower() in p.name.lower()]
        else:
            matches = all_projects
        if len(matches) == 1:
            summary_data = await _fetch_project_summary_data(db, matches[0].id)
            if summary_data:
                injected_context = _build_summary_context_block(summary_data)
        elif len(matches) == 0:
            names = ", ".join(p.name for p in all_projects[:10])
            injected_context = f"[No project matched '{project_name_query}'. Available: {names}]"
        else:
            names = ", ".join(p.name for p in matches)
            injected_context = f"[Multiple projects matched '{project_name_query}': {names}. Please specify.]"

    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in conv.messages:
        history.append({"role": msg.role, "content": msg.content})
    user_content = f"{injected_context}\n\n{payload.content}" if injected_context else payload.content
    history.append({"role": "user", "content": user_content})

    try:
        response = await litellm.acompletion(
            model=settings.AI_MODEL,
            messages=history,
        )
        ai_content = response.choices[0].message.content
        model_used = response.model
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")

    ai_msg = AIMessage(
        conversation_id=conv_id,
        role="assistant",
        content=ai_content,
        model=model_used,
    )
    db.add(ai_msg)

    if conv.title == "New Conversation" and len(conv.messages) == 0:
        conv.title = payload.content[:60] + ("..." if len(payload.content) > 60 else "")

    await db.flush()
    await db.refresh(ai_msg)
    return ai_msg


@router.post("/project-summary", response_model=ProjectSummaryResponse)
@limiter.limit("30/minute")
async def project_summary(
    request: Request,
    payload: ProjectSummaryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = await _fetch_project_summary_data(db, payload.project_id)
    if not data:
        raise HTTPException(status_code=404, detail="Project not found")

    context_block = _build_summary_context_block(data)
    summary_prompt = (
        "You are a project status analyst. The user wants a concise project summary. "
        "Write exactly 4 short paragraphs, one for each section: Milestone Progress, Recent Completions, Overdue, At-Risk. "
        "Use only the provided data — do not invent information. Be direct and specific.\n\n"
        f"{context_block}"
    )

    try:
        response = await litellm.acompletion(
            model=settings.AI_MODEL,
            messages=[
                {"role": "system", "content": summary_prompt},
                {"role": "user", "content": f"Summarize project '{data['project_name']}'"},
            ],
            temperature=0.3,
        )
        ai_content = response.choices[0].message.content or ""
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")

    paragraphs = [p.strip() for p in ai_content.strip().split("\n\n") if p.strip()]
    while len(paragraphs) < 4:
        paragraphs.append("No data available.")

    sections = ProjectSummarySections(
        milestone_progress=paragraphs[0],
        recent_completions=paragraphs[1],
        overdue=paragraphs[2],
        at_risk=paragraphs[3],
    )
    return ProjectSummaryResponse(summary=ai_content.strip(), sections=sections)


@router.post("/quick-chat", response_model=AIMessageOut)
@limiter.limit("30/minute")
async def quick_chat(
    request: Request,
    payload: AIMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Single-turn chat without persisting conversation history."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": payload.content},
    ]
    try:
        response = await litellm.acompletion(model=settings.AI_MODEL, messages=messages)
        ai_content = response.choices[0].message.content
        model_used = response.model
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")

    return AIMessageOut(id=0, role="assistant", content=ai_content, model=model_used, created_at=datetime.now(timezone.utc).replace(tzinfo=None))
