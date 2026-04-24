"""WebSocket endpoint for real-time chat (assistant, channels, DMs, presence)."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_client import acompletion
from app.auth import get_user_from_cookie
from app.config import settings
from app.database import AsyncSessionLocal
from app.models import (
    ChatChannel,
    ChatChannelMember,
    ChatConversation,
    ChatMessage,
    User,
    UserPresence,
)
from app.websocket.manager import manager

router = APIRouter(tags=["websocket"])

ASSISTANT_SYSTEM_PROMPT = (
    "You are a helpful project management assistant. Be concise and action-oriented."
)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


async def _send_error(ws: WebSocket, message: str, code: str | None = None) -> None:
    await manager.send_to_socket(ws, {"type": "error", "message": message, "code": code})


async def _set_presence(db: AsyncSession, user_id: int, is_online: bool, custom: str | None | object = ...) -> None:
    result = await db.execute(select(UserPresence).where(UserPresence.user_id == user_id))
    pres = result.scalar_one_or_none()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if pres is None:
        pres = UserPresence(user_id=user_id, is_online=is_online, last_seen=now)
        db.add(pres)
    else:
        pres.is_online = is_online
        pres.last_seen = now
    if custom is not ...:
        pres.custom_status = custom  # type: ignore[assignment]
    await db.commit()


async def _broadcast_presence(user_id: int, is_online: bool, custom_status: str | None) -> None:
    """Broadcast a presence update to all currently-online users."""
    payload = {
        "type": "presence_update",
        "user_id": user_id,
        "is_online": is_online,
        "custom_status": custom_status,
        "timestamp": _iso(datetime.now(timezone.utc).replace(tzinfo=None)),
    }
    for uid in manager.online_users():
        if uid == user_id:
            continue
        await manager.send_to_user(uid, payload)


async def _send_initial_presence(ws: WebSocket, db: AsyncSession) -> None:
    result = await db.execute(select(UserPresence))
    rows = result.scalars().all()
    online = manager.online_users()
    items = []
    for p in rows:
        items.append({
            "user_id": p.user_id,
            "is_online": p.user_id in online,
            "custom_status": p.custom_status,
            "last_seen": _iso(p.last_seen) if p.last_seen else None,
        })
    await manager.send_to_socket(ws, {"type": "presence_initial", "users": items})


# ── Handlers ────────────────────────────────────────────────────────────────

async def handle_heartbeat(ws: WebSocket, user: User, db: AsyncSession, msg: dict) -> None:
    await manager.send_to_socket(ws, {"type": "heartbeat_ack", "timestamp": _iso(datetime.now(timezone.utc).replace(tzinfo=None))})


# Channel handlers ----------------------------------------------------------

async def handle_channel_join(ws: WebSocket, user: User, db: AsyncSession, msg: dict) -> None:
    channel_id = msg.get("channel_id")
    if not isinstance(channel_id, int):
        return await _send_error(ws, "channel_id required (int)")

    result = await db.execute(select(ChatChannel).where(ChatChannel.id == channel_id))
    channel = result.scalar_one_or_none()
    if not channel:
        return await _send_error(ws, "Channel not found")

    # Add membership if not already a member
    mem_q = await db.execute(
        select(ChatChannelMember).where(
            ChatChannelMember.channel_id == channel_id,
            ChatChannelMember.user_id == user.id,
        )
    )
    if mem_q.scalar_one_or_none() is None:
        db.add(ChatChannelMember(channel_id=channel_id, user_id=user.id))
        await db.commit()

    manager.subscribe_channel(channel_id, user.id)

    await manager.send_to_socket(ws, {
        "type": "channel_joined",
        "channel_id": channel_id,
        "name": channel.name,
    })

    # Send last 50 messages
    hist_q = await db.execute(
        select(ChatMessage, User.full_name)
        .join(User, User.id == ChatMessage.sender_id)
        .where(ChatMessage.channel_id == channel_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(50)
    )
    rows = list(hist_q.all())
    rows.reverse()
    history = [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "sender_name": name,
            "channel_id": m.channel_id,
            "content": m.content,
            "created_at": _iso(m.created_at),
        }
        for m, name in rows
    ]
    await manager.send_to_socket(ws, {
        "type": "channel_history",
        "channel_id": channel_id,
        "messages": history,
    })


async def handle_channel_leave(ws: WebSocket, user: User, db: AsyncSession, msg: dict) -> None:
    channel_id = msg.get("channel_id")
    if not isinstance(channel_id, int):
        return await _send_error(ws, "channel_id required (int)")
    manager.unsubscribe_channel(channel_id, user.id)
    await manager.send_to_socket(ws, {"type": "channel_left", "channel_id": channel_id})


async def handle_channel_message(ws: WebSocket, user: User, db: AsyncSession, msg: dict) -> None:
    channel_id = msg.get("channel_id")
    content = (msg.get("content") or "").strip()
    if not isinstance(channel_id, int) or not content:
        return await _send_error(ws, "channel_id and non-empty content required")

    mem_q = await db.execute(
        select(ChatChannelMember).where(
            ChatChannelMember.channel_id == channel_id,
            ChatChannelMember.user_id == user.id,
        )
    )
    if mem_q.scalar_one_or_none() is None:
        return await _send_error(ws, "Not a member of this channel")

    message = ChatMessage(sender_id=user.id, channel_id=channel_id, content=content)
    db.add(message)
    await db.commit()
    await db.refresh(message)

    payload = {
        "type": "channel_message",
        "id": message.id,
        "channel_id": channel_id,
        "sender_id": user.id,
        "sender_name": user.full_name,
        "content": content,
        "created_at": _iso(message.created_at),
    }
    # Broadcast to all subscribers currently in the channel
    for uid in manager.channel_subscribers(channel_id):
        await manager.send_to_user(uid, payload)


async def handle_channel_members(ws: WebSocket, user: User, db: AsyncSession, msg: dict) -> None:
    channel_id = msg.get("channel_id")
    if not isinstance(channel_id, int):
        return await _send_error(ws, "channel_id required (int)")
    q = await db.execute(
        select(User.id, User.full_name, User.username)
        .join(ChatChannelMember, ChatChannelMember.user_id == User.id)
        .where(ChatChannelMember.channel_id == channel_id)
    )
    online = manager.online_users()
    members = [
        {"user_id": uid, "full_name": name, "username": uname, "is_online": uid in online}
        for uid, name, uname in q.all()
    ]
    await manager.send_to_socket(ws, {
        "type": "channel_member_list",
        "channel_id": channel_id,
        "members": members,
    })


# DM handlers --------------------------------------------------------------

async def _get_or_create_conversation(db: AsyncSession, a: int, b: int) -> ChatConversation:
    lo, hi = (a, b) if a <= b else (b, a)
    q = await db.execute(
        select(ChatConversation).where(
            ChatConversation.user_a_id == lo,
            ChatConversation.user_b_id == hi,
        )
    )
    conv = q.scalar_one_or_none()
    if conv is None:
        conv = ChatConversation(user_a_id=lo, user_b_id=hi)
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
    return conv


async def handle_dm_start(ws: WebSocket, user: User, db: AsyncSession, msg: dict) -> None:
    recipient_id = msg.get("recipient_id")
    if not isinstance(recipient_id, int) or recipient_id == user.id:
        return await _send_error(ws, "Valid recipient_id required")
    rq = await db.execute(select(User).where(User.id == recipient_id))
    if rq.scalar_one_or_none() is None:
        return await _send_error(ws, "User not found")
    conv = await _get_or_create_conversation(db, user.id, recipient_id)
    await manager.send_to_socket(ws, {
        "type": "dm_conversation",
        "conversation_id": conv.id,
        "other_user_id": recipient_id,
    })


async def handle_dm_message(ws: WebSocket, user: User, db: AsyncSession, msg: dict) -> None:
    recipient_id = msg.get("recipient_id")
    content = (msg.get("content") or "").strip()
    if not isinstance(recipient_id, int) or not content:
        return await _send_error(ws, "recipient_id and non-empty content required")

    rq = await db.execute(select(User).where(User.id == recipient_id))
    if rq.scalar_one_or_none() is None:
        return await _send_error(ws, "User not found")

    conv = await _get_or_create_conversation(db, user.id, recipient_id)
    message = ChatMessage(sender_id=user.id, conversation_id=conv.id, content=content)
    db.add(message)
    conv.last_message_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.commit()
    await db.refresh(message)

    payload = {
        "type": "dm_message",
        "id": message.id,
        "conversation_id": conv.id,
        "sender_id": user.id,
        "sender_name": user.full_name,
        "recipient_id": recipient_id,
        "content": content,
        "created_at": _iso(message.created_at),
    }
    await manager.send_to_user(recipient_id, payload)
    await manager.send_to_socket(ws, {**payload, "type": "dm_sent"})


async def handle_dm_history(ws: WebSocket, user: User, db: AsyncSession, msg: dict) -> None:
    other_id = msg.get("other_user_id")
    if not isinstance(other_id, int):
        return await _send_error(ws, "other_user_id required (int)")
    conv = await _get_or_create_conversation(db, user.id, other_id)
    q = await db.execute(
        select(ChatMessage, User.full_name)
        .join(User, User.id == ChatMessage.sender_id)
        .where(ChatMessage.conversation_id == conv.id)
        .order_by(ChatMessage.created_at.asc())
        .limit(100)
    )
    messages = [
        {
            "id": m.id,
            "conversation_id": m.conversation_id,
            "sender_id": m.sender_id,
            "sender_name": name,
            "content": m.content,
            "created_at": _iso(m.created_at),
        }
        for m, name in q.all()
    ]
    await manager.send_to_socket(ws, {
        "type": "dm_history",
        "conversation_id": conv.id,
        "other_user_id": other_id,
        "messages": messages,
    })


async def handle_dm_conversations(ws: WebSocket, user: User, db: AsyncSession, msg: dict) -> None:
    q = await db.execute(
        select(ChatConversation)
        .where(or_(ChatConversation.user_a_id == user.id, ChatConversation.user_b_id == user.id))
        .order_by(ChatConversation.last_message_at.desc())
    )
    convs = q.scalars().all()
    items = []
    for c in convs:
        other_id = c.user_b_id if c.user_a_id == user.id else c.user_a_id
        oq = await db.execute(select(User).where(User.id == other_id))
        other = oq.scalar_one_or_none()
        lq = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.conversation_id == c.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(1)
        )
        last = lq.scalar_one_or_none()
        items.append({
            "conversation_id": c.id,
            "other_user_id": other_id,
            "other_user_name": other.full_name if other else "",
            "last_message": last.content if last else None,
            "last_message_at": _iso(c.last_message_at),
        })
    await manager.send_to_socket(ws, {"type": "dm_conversation_list", "conversations": items})


# Presence handlers --------------------------------------------------------

async def handle_presence_query(ws: WebSocket, user: User, db: AsyncSession, msg: dict) -> None:
    target = msg.get("user_id")
    if not isinstance(target, int):
        return await _send_error(ws, "user_id required (int)")
    pq = await db.execute(select(UserPresence).where(UserPresence.user_id == target))
    p = pq.scalar_one_or_none()
    online = manager.is_user_online(target)
    await manager.send_to_socket(ws, {
        "type": "presence_status",
        "user_id": target,
        "is_online": online,
        "custom_status": p.custom_status if p else None,
        "last_seen": _iso(p.last_seen) if p and p.last_seen else None,
    })


async def handle_presence_query_batch(ws: WebSocket, user: User, db: AsyncSession, msg: dict) -> None:
    ids = msg.get("user_ids") or []
    if not isinstance(ids, list):
        return await _send_error(ws, "user_ids must be array of ints")
    pq = await db.execute(select(UserPresence).where(UserPresence.user_id.in_(ids)))
    pres_map = {p.user_id: p for p in pq.scalars().all()}
    online = manager.online_users()
    items = []
    for uid in ids:
        p = pres_map.get(uid)
        items.append({
            "user_id": uid,
            "is_online": uid in online,
            "custom_status": p.custom_status if p else None,
            "last_seen": _iso(p.last_seen) if p and p.last_seen else None,
        })
    await manager.send_to_socket(ws, {"type": "presence_batch", "users": items})


async def handle_presence_status_set(ws: WebSocket, user: User, db: AsyncSession, msg: dict) -> None:
    status_text = (msg.get("status") or "").strip() or None
    await _set_presence(db, user.id, is_online=True, custom=status_text)
    await _broadcast_presence(user.id, True, status_text)


async def handle_presence_status_clear(ws: WebSocket, user: User, db: AsyncSession, msg: dict) -> None:
    await _set_presence(db, user.id, is_online=True, custom=None)
    await _broadcast_presence(user.id, True, None)


# Assistant handlers -------------------------------------------------------

async def handle_assistant_message(ws: WebSocket, user: User, db: AsyncSession, msg: dict) -> None:
    content = (msg.get("content") or "").strip()
    if not content:
        return await _send_error(ws, "Message cannot be empty")

    history = manager.assistant_history(ws)
    history.append({"role": "user", "content": content})
    full_messages = [{"role": "system", "content": ASSISTANT_SYSTEM_PROMPT}] + history

    cancel_ev = manager.cancel_event(ws)
    cancel_ev.clear()

    chunk_index = 0
    accumulated = ""
    try:
        response = await acompletion(
            model=settings.AI_MODEL,
            messages=full_messages,
            stream=True,
        )
        async for chunk in response:  # type: ignore[union-attr]
            if cancel_ev.is_set():
                await manager.send_to_socket(ws, {"type": "assistant_cancelled"})
                history.pop()  # remove the user message we appended; cancellation = unsent
                return
            try:
                delta = chunk.choices[0].delta.content or ""
            except Exception:
                delta = ""
            if not delta:
                continue
            accumulated += delta
            await manager.send_to_socket(ws, {
                "type": "assistant_chunk",
                "chunk_index": chunk_index,
                "content": delta,
            })
            chunk_index += 1
        history.append({"role": "assistant", "content": accumulated})
        await manager.send_to_socket(ws, {
            "type": "assistant_done",
            "content": accumulated,
        })
    except Exception as e:
        history.pop()
        await _send_error(ws, f"Assistant error: {e}", code="assistant_error")


async def handle_assistant_cancel(ws: WebSocket, user: User, db: AsyncSession, msg: dict) -> None:
    manager.cancel_event(ws).set()


async def handle_assistant_reset(ws: WebSocket, user: User, db: AsyncSession, msg: dict) -> None:
    manager.reset_assistant_history(ws)
    await manager.send_to_socket(ws, {"type": "assistant_reset_ack"})


# Dispatch table -----------------------------------------------------------

HANDLERS = {
    "heartbeat": handle_heartbeat,
    "channel_join": handle_channel_join,
    "channel_leave": handle_channel_leave,
    "channel_message": handle_channel_message,
    "channel_members": handle_channel_members,
    "dm_start": handle_dm_start,
    "dm_message": handle_dm_message,
    "dm_history": handle_dm_history,
    "dm_conversations": handle_dm_conversations,
    "presence_query": handle_presence_query,
    "presence_query_batch": handle_presence_query_batch,
    "presence_status_set": handle_presence_status_set,
    "presence_status_clear": handle_presence_status_clear,
    "assistant_message": handle_assistant_message,
    "assistant_cancel": handle_assistant_cancel,
    "assistant_reset": handle_assistant_reset,
}


@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket) -> None:
    # Authenticate via cookie before accepting
    token = websocket.cookies.get("access_token")
    async with AsyncSessionLocal() as db:
        user = await get_user_from_cookie(token, db)
    if user is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(user.id, websocket)

    # Mark online + broadcast + send initial presence list
    async with AsyncSessionLocal() as db:
        await _set_presence(db, user.id, is_online=True)
        await _send_initial_presence(websocket, db)
    await _broadcast_presence(user.id, True, None)

    last_activity = asyncio.get_event_loop().time()

    async def idle_watchdog():
        nonlocal last_activity
        while True:
            await asyncio.sleep(10)
            if asyncio.get_event_loop().time() - last_activity > 60:
                try:
                    await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
                except Exception:
                    pass
                return

    watchdog_task = asyncio.create_task(idle_watchdog())

    try:
        while True:
            try:
                raw = await websocket.receive_text()
            except WebSocketDisconnect:
                break
            last_activity = asyncio.get_event_loop().time()

            try:
                import json
                msg = json.loads(raw)
            except Exception:
                await _send_error(websocket, "Invalid JSON")
                continue

            mtype = msg.get("type")
            handler = HANDLERS.get(mtype)
            if handler is None:
                await _send_error(websocket, f"Unknown message type: {mtype}")
                continue

            async with AsyncSessionLocal() as db:
                try:
                    await handler(websocket, user, db, msg)
                except Exception as e:
                    await _send_error(websocket, f"Handler error: {e}")
    finally:
        watchdog_task.cancel()
        await manager.disconnect(user.id, websocket)
        if not manager.is_user_online(user.id):
            async with AsyncSessionLocal() as db:
                await _set_presence(db, user.id, is_online=False)
            await _broadcast_presence(user.id, False, None)
