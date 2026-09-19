"""
Chat, Meeting Rooms, and Enterprise Forum models for real-time collaboration with multi-tenant isolation.
Supports:
1. Global Enterprise Forum: company-wide public channel where all posts display the sender's official role.
2. Direct 1-to-1 Messaging: private communication between any two employees of the same company (searchable by name or role).
3. Thematic Operational Channels: dedicated channels (#acconage-quai, #transport-corridors, #douane-transit, #atelier-gmao, #general-annonces).
4. Dynamic Meeting Rooms: custom conference rooms between specific colleagues with WebRTC video call capabilities.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ChatMeetingRoom(Base):
    """
    Meeting room / operational salon for group discussions and WebRTC video calls.
    Can be a public channel or a private restricted meeting room between specific employees.
    """
    __tablename__ = "chat_meeting_rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_uuid = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    topic = Column(Text, nullable=True)
    channel_type = Column(String(50), default="meeting")  # "thematic", "meeting", "department"
    is_private = Column(Boolean, default=False)
    active_call = Column(Boolean, default=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    members = relationship("ChatRoomMember", back_populates="room", cascade="all, delete-orphan")
    messages = relationship("EnterpriseChatMessage", back_populates="room", cascade="all, delete-orphan")


class ChatRoomMember(Base):
    """
    Membership in a meeting room with role (admin, member, invited).
    """
    __tablename__ = "chat_room_members"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_meeting_rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(30), default="member")  # "creator", "member", "guest"
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    room = relationship("ChatMeetingRoom", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])


class EnterpriseChatMessage(Base):
    """
    Unified chat message model for enterprise forum, meeting rooms, and direct 1-to-1 messaging.
    Strictly isolated by company_id (multi-tenant).
    """
    __tablename__ = "enterprise_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # None for forum/room messages
    room_id = Column(Integer, ForeignKey("chat_meeting_rooms.id", ondelete="CASCADE"), nullable=True, index=True)
    channel_type = Column(String(20), default="forum", index=True)  # "forum", "direct", "room", "thematic"
    content = Column(Text, nullable=False)
    sender_name_snapshot = Column(String(150), nullable=True)
    sender_role_snapshot = Column(String(100), nullable=True)  # Official role in company
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
    room = relationship("ChatMeetingRoom", back_populates="messages")
