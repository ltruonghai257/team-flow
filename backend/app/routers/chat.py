"""REST helpers for chat: list/create channels."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.auth import get_current_user
from app.db.database import get_db
from app.models import ChatChannel, ChatChannelMember, User
from app.schemas import ChatChannelOut

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChannelCreate(BaseModel):
    name: str
    description: Optional[str] = None


@router.get("/channels", response_model=List[ChatChannelOut])
async def list_channels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(select(ChatChannel).order_by(ChatChannel.created_at.asc()))
    return res.scalars().all()


@router.post("/channels", response_model=ChatChannelOut, status_code=201)
async def create_channel(
    payload: ChannelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = await db.execute(select(ChatChannel).where(ChatChannel.name == payload.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Channel name already exists")
    ch = ChatChannel(name=payload.name, description=payload.description, created_by=current_user.id)
    db.add(ch)
    await db.flush()
    db.add(ChatChannelMember(channel_id=ch.id, user_id=current_user.id))
    await db.flush()
    await db.refresh(ch)
    return ch


@router.get("/channels/my", response_model=List[ChatChannelOut])
async def my_channels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(
        select(ChatChannel)
        .join(ChatChannelMember, ChatChannelMember.channel_id == ChatChannel.id)
        .where(ChatChannelMember.user_id == current_user.id)
        .order_by(ChatChannel.created_at.asc())
    )
    return res.scalars().all()
