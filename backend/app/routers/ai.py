from typing import List

import litellm
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import AIConversation, AIMessage, Task, Milestone, User
from app.schemas import AIConversationOut, AIMessageCreate, AIMessageOut

router = APIRouter(prefix="/api/ai", tags=["ai"])

SYSTEM_PROMPT = """You are a helpful project management assistant. You help users manage their tasks, 
team members, project milestones, and schedules. You can provide insights, suggest priorities, 
help write task descriptions, summarize project status, and answer questions about project management 
best practices. Be concise, practical, and action-oriented."""


@router.get("/conversations", response_model=List[AIConversationOut])
async def list_conversations(
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
async def create_conversation(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conv = AIConversation(user_id=current_user.id, title="New Conversation")
    db.add(conv)
    await db.flush()
    await db.refresh(conv, ["messages"])
    return conv


@router.get("/conversations/{conv_id}", response_model=AIConversationOut)
async def get_conversation(
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
async def delete_conversation(
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
async def send_message(
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

    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in conv.messages:
        history.append({"role": msg.role, "content": msg.content})
    history.append({"role": "user", "content": payload.content})

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


@router.post("/quick-chat", response_model=AIMessageOut)
async def quick_chat(
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

    return AIMessageOut(id=0, role="assistant", content=ai_content, model=model_used, created_at=__import__("datetime").datetime.utcnow())
