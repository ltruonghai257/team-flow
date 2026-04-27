from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChatChannelOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageOut(BaseModel):
    id: int
    sender_id: int
    sender_name: Optional[str] = None
    channel_id: Optional[int]
    conversation_id: Optional[int]
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatConversationOut(BaseModel):
    id: int
    other_user_id: int
    other_user_name: Optional[str] = None
    last_message: Optional[str] = None
    last_message_at: datetime

    model_config = {"from_attributes": True}
