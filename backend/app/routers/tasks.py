import json
import re
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.utils.ai_client import acompletion
from app.utils.auth import get_current_user, get_sub_team
from app.core.config import settings
from app.db.database import get_db
from app.core.limiter import limiter
from app.models import (
    CustomStatus,
    Project,
    StatusSet,
    StatusSetScope,
    StatusTransition,
    SubTeam,
    Task,
    TaskPriority,
    TaskStatus,
    TaskType,
    User,
)
from app.schemas import (
    AiBreakdownRequest,
    AiBreakdownResponse,
    AiBreakdownSubtask,
    AiParseRequest,
    AiParseResponse,
    BlockedStatusTransitionDetail,
    TaskCreate,
    TaskOut,
    TaskUpdate,
)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


async def _resolve_custom_status(
    db: AsyncSession,
    custom_status_id: Optional[int],
    legacy_status: Optional[TaskStatus],
    project_id: Optional[int],
    sub_team_id: Optional[int],
) -> Optional[int]:
    """Resolve custom_status_id from explicit ID or legacy status mapping."""
    if custom_status_id is not None:
        result = await db.execute(
            select(CustomStatus).where(CustomStatus.id == custom_status_id)
        )
        cs = result.scalar_one_or_none()
        if not cs:
            raise HTTPException(status_code=400, detail="Invalid custom_status_id")
        return custom_status_id

    if legacy_status is not None:
        eff_project_id = project_id
        eff_sub_team_id = sub_team_id
        if eff_project_id:
            proj_set = await db.execute(
                select(StatusSet).options(selectinload(StatusSet.statuses)).where(
                    StatusSet.scope == StatusSetScope.project,
                    StatusSet.project_id == eff_project_id,
                )
            )
            project_set = proj_set.scalar_one_or_none()
            if project_set:
                for s in project_set.statuses:
                    if not s.is_archived and (
                        s.legacy_status == legacy_status or s.slug == legacy_status.value
                    ):
                        return s.id
        if eff_sub_team_id:
            default_result = await db.execute(
                select(StatusSet).options(selectinload(StatusSet.statuses)).where(
                    StatusSet.scope == StatusSetScope.sub_team_default,
                    StatusSet.sub_team_id == eff_sub_team_id,
                )
            )
            default_set = default_result.scalar_one_or_none()
            if default_set:
                for s in default_set.statuses:
                    if not s.is_archived and (
                        s.legacy_status == legacy_status or s.slug == legacy_status.value
                    ):
                        return s.id
        fallback_result = await db.execute(
            select(StatusSet).options(selectinload(StatusSet.statuses)).where(
                StatusSet.scope == StatusSetScope.sub_team_default,
                StatusSet.sub_team_id.is_(None),
            )
        )
        fallback_set = fallback_result.scalar_one_or_none()
        if fallback_set:
            for s in fallback_set.statuses:
                if not s.is_archived and (
                    s.legacy_status == legacy_status or s.slug == legacy_status.value
                ):
                    return s.id

    return None


async def _get_effective_status_set(
    db: AsyncSession,
    project_id: Optional[int],
    sub_team_id: Optional[int],
) -> Optional[StatusSet]:
    if project_id:
        result = await db.execute(
            select(StatusSet)
            .options(selectinload(StatusSet.statuses))
            .where(
                StatusSet.scope == StatusSetScope.project,
                StatusSet.project_id == project_id,
            )
        )
        status_set = result.scalar_one_or_none()
        if status_set:
            return status_set

    if sub_team_id:
        result = await db.execute(
            select(StatusSet)
            .options(selectinload(StatusSet.statuses))
            .where(
                StatusSet.scope == StatusSetScope.sub_team_default,
                StatusSet.sub_team_id == sub_team_id,
            )
        )
        status_set = result.scalar_one_or_none()
        if status_set:
            return status_set

    result = await db.execute(
        select(StatusSet)
        .options(selectinload(StatusSet.statuses))
        .where(
            StatusSet.scope == StatusSetScope.sub_team_default,
            StatusSet.sub_team_id.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def _resolve_effective_status_id_for_task(
    db: AsyncSession,
    *,
    explicit_custom_status_id: Optional[int],
    legacy_status: Optional[TaskStatus],
    project_id: Optional[int],
    sub_team_id: Optional[int],
) -> Optional[int]:
    return await _resolve_custom_status(
        db,
        explicit_custom_status_id,
        legacy_status,
        project_id,
        sub_team_id,
    )


async def _enforce_status_transition(
    db: AsyncSession,
    task: Task,
    *,
    explicit_custom_status_id: Optional[int],
    legacy_status: TaskStatus,
    target_project_id: Optional[int],
    sub_team_id: Optional[int],
) -> Optional[int]:
    current_status_id = await _resolve_effective_status_id_for_task(
        db,
        explicit_custom_status_id=task.custom_status_id,
        legacy_status=task.status,
        project_id=task.project_id,
        sub_team_id=sub_team_id,
    )
    target_status_id = await _resolve_effective_status_id_for_task(
        db,
        explicit_custom_status_id=explicit_custom_status_id,
        legacy_status=legacy_status,
        project_id=target_project_id,
        sub_team_id=sub_team_id,
    )

    if current_status_id is None or target_status_id is None:
        return target_status_id
    if current_status_id == target_status_id:
        return target_status_id

    target_status_result = await db.execute(
        select(CustomStatus).where(CustomStatus.id == target_status_id)
    )
    target_status = target_status_result.scalar_one_or_none()
    if not target_status:
        raise HTTPException(status_code=400, detail="Invalid target status")

    effective_status_set = await _get_effective_status_set(
        db,
        target_project_id,
        sub_team_id,
    )
    if not effective_status_set:
        return target_status_id

    transitions_result = await db.execute(
        select(StatusTransition).where(
            StatusTransition.status_set_id == effective_status_set.id
        )
    )
    transitions = transitions_result.scalars().all()
    if not transitions:
        return target_status_id

    allowed_status_ids = [
        transition.to_status_id
        for transition in transitions
        if transition.from_status_id == current_status_id
    ]
    if target_status_id in allowed_status_ids:
        return target_status_id

    current_status_result = await db.execute(
        select(CustomStatus).where(CustomStatus.id == current_status_id)
    )
    current_status = current_status_result.scalar_one_or_none()
    detail = BlockedStatusTransitionDetail(
        code="status_transition_blocked",
        message="This workflow does not allow moving the task to the selected status.",
        status_set_id=effective_status_set.id,
        current_status_id=current_status_id,
        current_status_name=current_status.name if current_status else task.status.value,
        target_status_id=target_status_id,
        target_status_name=target_status.name,
        allowed_status_ids=allowed_status_ids,
    )
    raise HTTPException(status_code=422, detail=detail.model_dump())

_AI_BREAKDOWN_SYSTEM_PROMPT = """You are a task breakdown assistant. The user describes a feature or work item.
Decompose it into 3–8 concrete subtasks. Respond with ONLY a valid JSON array (no markdown, no prose):
[{"title":"...", "priority":"low|medium|high|critical", "type":"feature|bug|task|improvement (default task)", "estimated_hours": integer, "description":"1-2 sentences"}]
Return between 3 and 8 items. No code fences. No explanations."""

_AI_PARSE_SYSTEM_PROMPT = """You are a task extraction assistant. The user will describe a task in natural language.
Extract the task fields and respond with ONLY a valid JSON object (no markdown, no prose) matching this schema:
{
  "title": "string (required, concise)",
  "description": "string or null (longer details if given)",
  "priority": "low|medium|high|critical (default medium)",
  "type": "feature|bug|task|improvement (default task)",
  "status": "todo|in_progress|review|done|blocked (default todo)",
  "due_date": "ISO 8601 date string (YYYY-MM-DD) or null",
  "estimated_hours": "integer or null",
  "tags": "comma-separated string or null",
  "assignee_name": "string or null (the person's name if mentioned)"
}
Today's date for relative date computation: {today}.
Respond with JSON only. No code fences, no explanations."""


def _coerce_ai_parse(data: dict) -> AiParseResponse:
    """Normalize a raw dict into AiParseResponse, dropping invalid enum values."""
    valid_status = {s.value for s in TaskStatus}
    valid_priority = {p.value for p in TaskPriority}
    valid_type = {t.value for t in TaskType}

    out: dict = {}
    if data.get("title"):
        out["title"] = str(data["title"])[:200]
    if data.get("description"):
        out["description"] = str(data["description"])
    status = data.get("status")
    if isinstance(status, str) and status in valid_status:
        out["status"] = status
    priority = data.get("priority")
    if isinstance(priority, str) and priority in valid_priority:
        out["priority"] = priority
    task_type = data.get("type")
    if isinstance(task_type, str) and task_type in valid_type:
        out["type"] = task_type
    due = data.get("due_date")
    if due:
        try:
            # Accept YYYY-MM-DD or ISO datetime
            out["due_date"] = datetime.fromisoformat(str(due).replace("Z", "+00:00"))
        except ValueError:
            try:
                out["due_date"] = datetime.strptime(str(due), "%Y-%m-%d")
            except ValueError:
                pass
    hours = data.get("estimated_hours")
    if isinstance(hours, (int, float)):
        out["estimated_hours"] = int(hours)
    if data.get("tags"):
        out["tags"] = str(data["tags"])
    if data.get("assignee_name"):
        out["assignee_name"] = str(data["assignee_name"])
    return AiParseResponse(**out)


@router.get("/", response_model=List[TaskOut])
async def list_tasks(
    project_id: Optional[int] = None,
    milestone_id: Optional[int] = None,
    sprint_id: Optional[int] = None,
    unassigned: bool = False,
    assignee_id: Optional[int] = None,
    status: Optional[TaskStatus] = None,
    types: Optional[str] = None,
    my_tasks: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    query = select(Task).options(selectinload(Task.assignee), selectinload(Task.custom_status))

    # Apply sub-team filter (admin may have None = all teams)
    if sub_team:
        query = query.join(Project, Task.project_id == Project.id).where(
            Project.sub_team_id == sub_team.id
        )
    if project_id:
        query = query.where(Task.project_id == project_id)
    if milestone_id:
        query = query.where(Task.milestone_id == milestone_id)
    if sprint_id:
        query = query.where(Task.sprint_id == sprint_id)
    if unassigned:
        query = query.where(Task.sprint_id == None)
    if assignee_id:
        query = query.where(Task.assignee_id == assignee_id)
    if status:
        query = query.where(Task.status == status)
    if types:
        type_values = []
        for raw_type in [t.strip() for t in types.split(",") if t.strip()]:
            try:
                type_values.append(TaskType(raw_type))
            except ValueError:
                raise HTTPException(status_code=422, detail="Invalid task type filter")
        if type_values:
            query = query.where(Task.type.in_(type_values))
    if my_tasks:
        query = query.where(Task.assignee_id == current_user.id)
    query = query.order_by(Task.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=TaskOut, status_code=201)
async def create_task(
    payload: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    task_data = payload.model_dump()
    sub_team_id = sub_team.id if sub_team else None
    resolved_cs_id = await _resolve_custom_status(
        db,
        task_data.get("custom_status_id"),
        task_data.get("status"),
        task_data.get("project_id"),
        sub_team_id,
    )
    if resolved_cs_id is None and task_data.get("status") is None:
        resolved_cs_id = await _resolve_custom_status(
            db, None, TaskStatus.todo, task_data.get("project_id"), sub_team_id
        )
    task_data["custom_status_id"] = resolved_cs_id
    task = Task(**task_data, creator_id=current_user.id)
    db.add(task)
    await db.flush()
    await db.refresh(task, ["assignee", "custom_status"])
    return task


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.assignee), selectinload(Task.custom_status))
        .where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
    sub_team: Optional[SubTeam] = Depends(get_sub_team),
):
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.assignee), selectinload(Task.custom_status))
        .where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = payload.model_dump(exclude_unset=True)

    requested_custom_status_id = update_data.pop("custom_status_id", None)
    sub_team_id = sub_team.id if sub_team else None
    target_project_id = update_data.get("project_id", task.project_id)
    target_legacy_status = update_data.get("status", task.status)
    should_enforce_transition = (
        requested_custom_status_id is not None
        or "status" in update_data
        or (
            "project_id" in update_data
            and update_data["project_id"] != task.project_id
        )
    )

    resolved_cs_id = task.custom_status_id
    if should_enforce_transition:
        resolved_cs_id = await _enforce_status_transition(
            db,
            task,
            explicit_custom_status_id=requested_custom_status_id,
            legacy_status=target_legacy_status,
            target_project_id=target_project_id,
            sub_team_id=sub_team_id,
        )

    if requested_custom_status_id is not None or "status" in update_data or "project_id" in update_data:
        if resolved_cs_id is not None:
            old_is_done = task.custom_status.is_done if task.custom_status else False
            new_cs_result = await db.execute(
                select(CustomStatus).where(CustomStatus.id == resolved_cs_id)
            )
            new_cs = new_cs_result.scalar_one_or_none()
            new_is_done = new_cs.is_done if new_cs else False

            if not old_is_done and new_is_done:
                if not update_data.get("completed_at"):
                    update_data["completed_at"] = datetime.now(timezone.utc).replace(tzinfo=None)
            elif old_is_done and not new_is_done:
                update_data["completed_at"] = None

            update_data["custom_status_id"] = resolved_cs_id

    for field, value in update_data.items():
        setattr(task, field, value)
    task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.flush()
    await db.refresh(task, ["assignee", "custom_status"])
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.flush()


def _coerce_ai_breakdown(raw: list) -> list[AiBreakdownSubtask]:
    """Normalize a raw list into AiBreakdownSubtask items, dropping invalid entries."""
    valid_priority = {p.value for p in TaskPriority}
    valid_type = {t.value for t in TaskType}
    result = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()[:200]
        if not title:
            continue
        priority = item.get("priority", "medium")
        if not isinstance(priority, str) or priority not in valid_priority:
            priority = "medium"
        task_type = item.get("type", "task")
        if not isinstance(task_type, str) or task_type not in valid_type:
            task_type = "task"
        hours = item.get("estimated_hours", 0)
        if not isinstance(hours, (int, float)) or hours < 0:
            hours = 0
        description = str(item.get("description", ""))[:500]
        result.append(
            AiBreakdownSubtask(
                title=title,
                priority=priority,
                type=task_type,
                estimated_hours=int(hours),
                description=description,
            )
        )
    return result[:8]


@router.post("/ai-breakdown", response_model=AiBreakdownResponse)
@limiter.limit("30/minute")
async def ai_breakdown(
    request: Request,
    payload: AiBreakdownRequest,
    _: User = Depends(get_current_user),
):
    try:
        response = await acompletion(
            model=settings.AI_MODEL,
            messages=[
                {"role": "system", "content": _AI_BREAKDOWN_SYSTEM_PROMPT},
                {"role": "user", "content": payload.description},
            ],
            temperature=0.4,
        )
        content = response.choices[0].message.content or ""
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")

    content = content.strip()
    fence_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", content, re.DOTALL)
    if fence_match:
        content = fence_match.group(1)
    else:
        arr_match = re.search(r"\[.*\]", content, re.DOTALL)
        if arr_match:
            content = arr_match.group(0)

    try:
        data = json.loads(content)
        if not isinstance(data, list):
            raise ValueError("Expected JSON array")
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(
            status_code=502, detail="AI did not return a valid JSON array"
        )

    subtasks = _coerce_ai_breakdown(data)
    if not subtasks:
        raise HTTPException(status_code=502, detail="AI returned no valid subtasks")
    return AiBreakdownResponse(subtasks=subtasks)


@router.post("/ai-parse", response_model=AiParseResponse)
async def ai_parse_task(
    payload: AiParseRequest,
    _: User = Depends(get_current_user),
):
    mode = payload.mode.lower()
    if mode not in ("nlp", "json"):
        raise HTTPException(status_code=422, detail="mode must be 'nlp' or 'json'")

    if mode == "json":
        try:
            data = json.loads(payload.input)
            if not isinstance(data, dict):
                raise ValueError("Root must be a JSON object")
        except (ValueError, json.JSONDecodeError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
        return _coerce_ai_parse(data)

    # NLP mode — call LiteLLM
    model = payload.model or settings.AI_MODEL
    prompt = _AI_PARSE_SYSTEM_PROMPT.replace(
        "{today}", datetime.now(timezone.utc).strftime("%Y-%m-%d")
    )
    try:
        response = await acompletion(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": payload.input},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or ""
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")

    # Strip code fences if the model wrapped JSON in them
    content = content.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
    if fence_match:
        content = fence_match.group(1)
    else:
        obj_match = re.search(r"\{.*\}", content, re.DOTALL)
        if obj_match:
            content = obj_match.group(0)

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="AI did not return valid JSON")

    return _coerce_ai_parse(data)
