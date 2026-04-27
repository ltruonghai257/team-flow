import asyncio
from collections import defaultdict
from typing import Any, Dict, Set

from fastapi import WebSocket


class ConnectionManager:
    """Tracks active WebSocket connections per user_id.

    Each user MAY have multiple concurrent connections (multi-device).
    """

    def __init__(self) -> None:
        self._connections: Dict[int, Set[WebSocket]] = defaultdict(set)
        # Channel subscriptions in memory: channel_id -> set of user_ids currently subscribed
        self._channel_subs: Dict[int, Set[int]] = defaultdict(set)
        # Per-connection cancel events for in-flight assistant generations
        self._cancel_events: Dict[WebSocket, asyncio.Event] = {}
        # Per-connection in-memory assistant chat history (role/content list)
        self._assistant_history: Dict[WebSocket, list] = {}
        self._lock = asyncio.Lock()

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[user_id].add(websocket)
            self._cancel_events[websocket] = asyncio.Event()
            self._assistant_history[websocket] = []

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.get(user_id, set()).discard(websocket)
            if user_id in self._connections and not self._connections[user_id]:
                del self._connections[user_id]
            self._cancel_events.pop(websocket, None)
            self._assistant_history.pop(websocket, None)
            for subs in self._channel_subs.values():
                subs.discard(user_id)

    def is_user_online(self, user_id: int) -> bool:
        return user_id in self._connections and len(self._connections[user_id]) > 0

    def online_users(self) -> Set[int]:
        return set(self._connections.keys())

    async def send_to_user(self, user_id: int, message: dict) -> None:
        """Send a message to all active connections for a user. Silently drops if offline."""
        sockets = list(self._connections.get(user_id, set()))
        for ws in sockets:
            try:
                await ws.send_json(message)
            except Exception:
                # Connection broken; will be cleaned up on disconnect
                pass

    async def send_to_socket(self, websocket: WebSocket, message: dict) -> None:
        try:
            await websocket.send_json(message)
        except Exception:
            pass

    async def broadcast_to_users(self, user_ids: Set[int], message: dict, exclude_user: int | None = None) -> None:
        for uid in user_ids:
            if uid == exclude_user:
                continue
            await self.send_to_user(uid, message)

    # ── Channel subscription tracking ────────────────────────────────────────
    def subscribe_channel(self, channel_id: int, user_id: int) -> None:
        self._channel_subs[channel_id].add(user_id)

    def unsubscribe_channel(self, channel_id: int, user_id: int) -> None:
        self._channel_subs.get(channel_id, set()).discard(user_id)

    def channel_subscribers(self, channel_id: int) -> Set[int]:
        return set(self._channel_subs.get(channel_id, set()))

    # ── Assistant generation control ─────────────────────────────────────────
    def cancel_event(self, websocket: WebSocket) -> asyncio.Event:
        return self._cancel_events.setdefault(websocket, asyncio.Event())

    def reset_cancel(self, websocket: WebSocket) -> None:
        ev = self._cancel_events.get(websocket)
        if ev:
            ev.clear()

    def assistant_history(self, websocket: WebSocket) -> list:
        return self._assistant_history.setdefault(websocket, [])

    def reset_assistant_history(self, websocket: WebSocket) -> None:
        self._assistant_history[websocket] = []


manager = ConnectionManager()
