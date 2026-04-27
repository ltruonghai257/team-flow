from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class ChatChannel(Base):
    __tablename__ = "chat_channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    members = relationship(
        "ChatChannelMember", back_populates="channel", cascade="all, delete-orphan"
    )
    messages = relationship(
        "ChatMessage", back_populates="channel", cascade="all, delete-orphan"
    )


class ChatChannelMember(Base):
    __tablename__ = "chat_channel_members"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(
        Integer, ForeignKey("chat_channels.id"), nullable=False, index=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    joined_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    channel = relationship("ChatChannel", back_populates="members")


class ChatConversation(Base):
    """Direct message conversation between two users."""

    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_a_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user_b_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    last_message_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        index=True,
    )

    messages = relationship(
        "ChatMessage", back_populates="conversation", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    channel_id = Column(
        Integer, ForeignKey("chat_channels.id"), nullable=True, index=True
    )
    conversation_id = Column(
        Integer, ForeignKey("chat_conversations.id"), nullable=True, index=True
    )
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        index=True,
    )

    channel = relationship("ChatChannel", back_populates="messages")
    conversation = relationship("ChatConversation", back_populates="messages")


class UserPresence(Base):
    __tablename__ = "user_presence"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    is_online = Column(Boolean, default=False, nullable=False)
    custom_status = Column(String, nullable=True)
    last_seen = Column(
        DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
