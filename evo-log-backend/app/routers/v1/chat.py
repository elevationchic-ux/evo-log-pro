"""
Enterprise Chat & Collaboration Router with Multi-Tenant Isolation
Features:
1. Global Enterprise Forum: Public channel within the company where all posts display the sender's official role.
2. Direct 1-to-1 Messaging: Private communication between any two employees of the same company (searchable by name or role).
3. Thematic Operational Channels: Salons métiers (#acconage-quai, #transport-corridors, #douane-transit, #atelier-gmao, #general-annonces).
4. Custom Meeting Rooms: Salons de réunion entre certains employés avec sélection des participants.
5. WebRTC Video Call Engine: Visioconférence intégrée P2P (caméra, micro, partage d'écran) avec signalisation temps réel.
6. Company User Directory: Search colleagues by full name, username, or official enterprise role.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import time
import base64
import json
import binascii

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Role
from app.models.chat import EnterpriseChatMessage, ChatMeetingRoom, ChatRoomMember
from app.services.outbox_service import enqueue_event
from app.services.events.outbox_delivery import deliver_outbox_event
from app.core.config import settings
from app.services.realtime_store import RedisSignalingStore
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security_scheme = HTTPBearer(auto_error=True)


_SIGNALING = RedisSignalingStore(settings.REDIS_URL)


def get_current_chat_user(current_user: User = Depends(get_current_user)) -> User:
    """Require a centrally authenticated user with an active tenant."""
    if not current_user.is_superuser and current_user.company_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utilisateur sans tenant actif.",
        )
    return current_user

# ─── Pydantic Schemas ───
class SendMessageSchema(BaseModel):
    content: str
    recipient_id: Optional[int] = None


class SendRoomMessageSchema(BaseModel):
    content: str


class CreateMeetingRoomSchema(BaseModel):
    name: str
    topic: Optional[str] = ""
    is_private: Optional[bool] = False
    participant_ids: Optional[List[int]] = []


def _get_accessible_room(db: Session, room_identifier: str, current_user: User) -> ChatMeetingRoom:
    room_id = int(room_identifier) if room_identifier.isdigit() else -1
    room = db.query(ChatMeetingRoom).filter(
        or_(ChatMeetingRoom.room_uuid == room_identifier, ChatMeetingRoom.id == room_id)
    ).first()
    if not room:
        raise HTTPException(status_code=404, detail="Salon ou canal introuvable.")
    if not current_user.is_superuser and room.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Salon hors de votre entreprise.")
    if room.is_private:
        member = db.query(ChatRoomMember).filter(
            ChatRoomMember.room_id == room.id,
            ChatRoomMember.user_id == current_user.id,
        ).first()
        if not member:
            raise HTTPException(status_code=403, detail="Vous n'êtes pas membre de ce salon privé.")
    return room


class ChatMessageOut(BaseModel):
    id: int
    company_id: Optional[int]
    sender_id: int
    recipient_id: Optional[int]
    room_id: Optional[int] = None
    channel_type: str
    content: str
    sender_name: str
    sender_role: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChatColleagueOut(BaseModel):
    id: int
    username: str
    full_name: str
    email: str
    role_code: str
    role_title: str
    company_id: Optional[int]
    is_online: bool = True


class MeetingRoomMemberOut(BaseModel):
    id: int
    username: str
    full_name: str
    role_title: str


class MeetingRoomOut(BaseModel):
    id: int
    room_uuid: str
    name: str
    topic: Optional[str]
    channel_type: str
    is_private: bool
    active_call: bool
    created_by_id: Optional[int]
    created_by_name: str
    created_at: datetime
    members_count: int
    members: List[MeetingRoomMemberOut]


def _decode_message_cursor(cursor: Optional[str]) -> Optional[int]:
    if not cursor:
        return None
    try:
        value = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
        return int(value["id"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError, binascii.Error):
        raise HTTPException(status_code=400, detail="Curseur de pagination invalide.")


def _encode_message_cursor(message_id: int) -> str:
    return base64.urlsafe_b64encode(json.dumps({"id": message_id}).encode()).decode()


class WebRTCSignalIn(BaseModel):
    room_uuid: str
    target_user_id: Optional[int] = None
    signal_type: str  # "offer", "answer", "ice-candidate", "call-start", "call-end", "user-joined", "user-left"
    payload: Dict[str, Any] = {}


# ─── Helper Functions ───
def get_user_official_role_title(user: User) -> str:
    """Extract human-readable official role title from user's assigned role."""
    if not user:
        return "Collaborateur Entreprise"
    if user.is_superuser:
        return "Super Administrateur Plateforme SaaS CADC"
    if user.roles:
        role = user.roles[0]
        if role.description:
            return role.description.split(" - ")[0]
        return role.name
    return "Collaborateur Entreprise"


def ensure_default_thematic_channels(db: Session, company_id: Optional[int], creator_id: int):
    """Auto-seeds the 5 core thematic operational channels if missing"""
    thematic_channels = [
        ("thematic-acconage", "#acconage-quai", "Cadences portiques STS, escales navires en cours, rotations équipes dockers", "thematic"),
        ("thematic-transport", "#transport-corridors", "Alertes trafic routier, état corridors Douala-Bangui / Douala-N'Djamena", "thematic"),
        ("thematic-douane", "#douane-transit", "Dégagement DUM, validation des BAE, scanning PAD & litiges déclarations", "thematic"),
        ("thematic-gmao", "#atelier-gmao", "Urgences pannes mécaniques, maintenance chariots cavaliers et tracteurs portuaires", "thematic"),
        ("thematic-annonces", "#general-annonces", "Communications officielles, sécurité QHSE et notes de service Direction Générale", "thematic"),
    ]

    for room_uuid, name, topic, ctype in thematic_channels:
        exists = db.query(ChatMeetingRoom).filter(ChatMeetingRoom.room_uuid == room_uuid).first()
        if not exists:
            room = ChatMeetingRoom(
                room_uuid=room_uuid,
                name=name,
                topic=topic,
                channel_type=ctype,
                is_private=False,
                company_id=company_id,
                created_by_id=creator_id
            )
            db.add(room)
    try:
        db.commit()
    except Exception:
        db.rollback()


# ─── Endpoints : Annuaire & Profils ───

@router.get("/directory", response_model=List[ChatColleagueOut])
def get_company_directory(
    q: Optional[str] = Query(None, description="Search query by name, username, or role"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_chat_user)
):
    """
    Search colleagues in the same company by Name or by Official Role.
    Multi-tenant: users only see colleagues from their own company (unless SuperAdmin).
    """
    query = db.query(User).filter(User.is_active == True)

    if not current_user.is_superuser and current_user.company_id is not None:
        query = query.filter(User.company_id == current_user.company_id)

    if q and q.strip():
        search_term = f"%{q.strip().lower()}%"
        query = query.outerjoin(User.roles).filter(
            or_(
                User.full_name.ilike(search_term),
                User.username.ilike(search_term),
                User.email.ilike(search_term),
                Role.name.ilike(search_term),
                Role.description.ilike(search_term)
            )
        )

    users = query.limit(50).all()
    results = []
    for u in users:
        role_code = u.roles[0].name if u.roles else ("SUPER_ADMIN" if u.is_superuser else "USER")
        results.append(ChatColleagueOut(
            id=u.id,
            username=u.username,
            full_name=u.full_name or u.username,
            email=u.email,
            role_code=role_code,
            role_title=get_user_official_role_title(u),
            company_id=u.company_id,
            is_online=True
        ))
    return results


# ─── Endpoints : Grand Forum d'Entreprise ───

@router.get("/forum", response_model=List[ChatMessageOut])
def get_forum_messages(
    response: Response,
    limit: int = Query(50, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_chat_user)
):
    """Get recent enterprise forum messages."""
    query = db.query(EnterpriseChatMessage).filter(
        EnterpriseChatMessage.channel_type == "forum"
    )

    if not current_user.is_superuser and current_user.company_id is not None:
        query = query.filter(EnterpriseChatMessage.company_id == current_user.company_id)

    cursor_id = _decode_message_cursor(cursor)
    if cursor_id is not None:
        query = query.filter(EnterpriseChatMessage.id < cursor_id)
    messages = query.order_by(
        EnterpriseChatMessage.created_at.desc(), EnterpriseChatMessage.id.desc()
    ).limit(limit + 1).all()
    has_more = len(messages) > limit
    messages = messages[:limit]
    messages.reverse()
    response.headers["X-Has-More"] = str(has_more).lower()
    if messages and has_more:
        response.headers["X-Next-Cursor"] = _encode_message_cursor(messages[-1].id)

    return [
        ChatMessageOut(
            id=m.id,
            company_id=m.company_id,
            sender_id=m.sender_id,
            recipient_id=m.recipient_id,
            room_id=m.room_id,
            channel_type=m.channel_type,
            content=m.content,
            sender_name=m.sender_name_snapshot or (m.sender.full_name if m.sender else "Utilisateur"),
            sender_role=m.sender_role_snapshot or (get_user_official_role_title(m.sender) if m.sender else "Collaborateur"),
            is_read=m.is_read,
            created_at=m.created_at or datetime.utcnow()
        )
        for m in messages
    ]


@router.post("/forum", response_model=ChatMessageOut)
async def post_forum_message(
    payload: SendMessageSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_chat_user)
):
    """Publish a message on the Grand Forum d'Entreprise."""
    if not payload.content or not payload.content.strip():
        raise HTTPException(status_code=400, detail="Le message ne peut pas être vide.")

    role_title = get_user_official_role_title(current_user)
    msg = EnterpriseChatMessage(
        company_id=current_user.company_id,
        sender_id=current_user.id,
        recipient_id=None,
        room_id=None,
        channel_type="forum",
        content=payload.content.strip(),
        sender_name_snapshot=current_user.full_name or current_user.username,
        sender_role_snapshot=role_title,
        is_read=False
    )
    db.add(msg)
    db.flush()
    outbox_evt = enqueue_event(
        db,
        event_type="chat.message.created",
        aggregate_type="chat_message",
        aggregate_id=str(msg.id),
        payload={"company_id": current_user.company_id, "message_id": msg.id, "room_id": msg.room_id, "sender_id": msg.sender_id},
    )
    db.commit()
    db.refresh(msg)
    # Diffusion temps reel immediate ; en cas d'echec l'evenement reste en
    # outbox et sera rejoue par le pump (ou le worker Celery).
    await deliver_outbox_event(db, outbox_evt)

    return ChatMessageOut(
        id=msg.id,
        company_id=msg.company_id,
        sender_id=msg.sender_id,
        recipient_id=msg.recipient_id,
        room_id=msg.room_id,
        channel_type=msg.channel_type,
        content=msg.content,
        sender_name=msg.sender_name_snapshot,
        sender_role=msg.sender_role_snapshot,
        is_read=msg.is_read,
        created_at=msg.created_at or datetime.utcnow()
    )


# ─── Endpoints : Messages Directs 1-à-1 ───

@router.get("/direct/{colleague_id}", response_model=List[ChatMessageOut])
def get_direct_messages(
    colleague_id: int,
    response: Response,
    limit: int = Query(50, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_chat_user)
):
    """Retrieve 1-to-1 private conversation history between current user and a colleague."""
    colleague = db.query(User).filter(User.id == colleague_id).first()
    if not colleague:
        raise HTTPException(status_code=404, detail="Collègue introuvable.")

    if not current_user.is_superuser and colleague.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Communication inter-entreprises non autorisée.")

    message_query = db.query(EnterpriseChatMessage).filter(
        EnterpriseChatMessage.company_id == current_user.company_id,
        EnterpriseChatMessage.channel_type == "direct",
        or_(
            and_(EnterpriseChatMessage.sender_id == current_user.id, EnterpriseChatMessage.recipient_id == colleague_id),
            and_(EnterpriseChatMessage.sender_id == colleague_id, EnterpriseChatMessage.recipient_id == current_user.id)
        )
    )
    cursor_id = _decode_message_cursor(cursor)
    if cursor_id is not None:
        message_query = message_query.filter(EnterpriseChatMessage.id < cursor_id)
    messages = message_query.order_by(
        EnterpriseChatMessage.created_at.desc(), EnterpriseChatMessage.id.desc()
    ).limit(limit + 1).all()
    has_more = len(messages) > limit
    messages = messages[:limit]
    messages.reverse()
    response.headers["X-Has-More"] = str(has_more).lower()
    if messages and has_more:
        response.headers["X-Next-Cursor"] = _encode_message_cursor(messages[-1].id)

    for m in messages:
        if m.recipient_id == current_user.id and not m.is_read:
            m.is_read = True
    db.commit()

    return [
        ChatMessageOut(
            id=m.id,
            company_id=m.company_id,
            sender_id=m.sender_id,
            recipient_id=m.recipient_id,
            room_id=m.room_id,
            channel_type=m.channel_type,
            content=m.content,
            sender_name=m.sender_name_snapshot or (m.sender.full_name if m.sender else "Utilisateur"),
            sender_role=m.sender_role_snapshot or (get_user_official_role_title(m.sender) if m.sender else "Collaborateur"),
            is_read=m.is_read,
            created_at=m.created_at or datetime.utcnow()
        )
        for m in messages
    ]


@router.post("/direct", response_model=ChatMessageOut)
async def send_direct_message(
    payload: SendMessageSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_chat_user)
):
    """Send a direct 1-to-1 message to a specific colleague in the company."""
    if not payload.recipient_id:
        raise HTTPException(status_code=400, detail="Identifiant du destinataire requis.")
    if not payload.content or not payload.content.strip():
        raise HTTPException(status_code=400, detail="Le message ne peut pas être vide.")

    recipient = db.query(User).filter(User.id == payload.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Destinataire introuvable.")

    if not current_user.is_superuser and recipient.company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Communication restreinte aux collaborateurs de votre entreprise.")

    msg = EnterpriseChatMessage(
        company_id=current_user.company_id,
        sender_id=current_user.id,
        recipient_id=recipient.id,
        room_id=None,
        channel_type="direct",
        content=payload.content.strip(),
        sender_name_snapshot=current_user.full_name or current_user.username,
        sender_role_snapshot=get_user_official_role_title(current_user),
        is_read=False
    )
    db.add(msg)
    db.flush()
    outbox_evt = enqueue_event(
        db,
        event_type="chat.message.created",
        aggregate_type="chat_message",
        aggregate_id=str(msg.id),
        payload={
            "company_id": current_user.company_id,
            "message_id": msg.id,
            "recipient_id": msg.recipient_id,
            "sender_id": msg.sender_id,
            # un DM n'est diffuse qu'a ses deux interlocuteurs (pas tout le tenant)
            "_target_users": [current_user.id, recipient.id],
        },
    )
    db.commit()
    db.refresh(msg)
    # Diffusion temps reel immediate vers les deux interlocuteurs ; fallback pump.
    await deliver_outbox_event(db, outbox_evt)

    return ChatMessageOut(
        id=msg.id,
        company_id=msg.company_id,
        sender_id=msg.sender_id,
        recipient_id=msg.recipient_id,
        room_id=msg.room_id,
        channel_type=msg.channel_type,
        content=msg.content,
        sender_name=msg.sender_name_snapshot,
        sender_role=msg.sender_role_snapshot,
        is_read=msg.is_read,
        created_at=msg.created_at or datetime.utcnow()
    )


# ─── Endpoints : Salons Métiers & Salons de Meeting ───

@router.get("/rooms", response_model=List[MeetingRoomOut])
def get_user_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_chat_user)
):
    """
    Get all rooms accessible to the user:
    - Thematic channels (public for company)
    - Meeting rooms created by user or where user is an invited member
    """
    ensure_default_thematic_channels(db, current_user.company_id, current_user.id)

    # Find rooms where:
    # 1. channel_type == "thematic"
    # 2. or created_by_id == current_user.id
    # 3. or user is in members
    user_member_room_ids = [
        rm.room_id for rm in db.query(ChatRoomMember.room_id).filter(ChatRoomMember.user_id == current_user.id).all()
    ]

    query = db.query(ChatMeetingRoom).filter(
        or_(
            ChatMeetingRoom.channel_type == "thematic",
            ChatMeetingRoom.created_by_id == current_user.id,
            ChatMeetingRoom.id.in_(user_member_room_ids),
            ChatMeetingRoom.is_private == False
        )
    )

    if not current_user.is_superuser and current_user.company_id is not None:
        query = query.filter(
            or_(ChatMeetingRoom.company_id == current_user.company_id, ChatMeetingRoom.company_id.is_(None))
        )

    rooms = query.order_by(ChatMeetingRoom.created_at.asc()).all()

    out = []
    for r in rooms:
        creator_name = r.created_by.full_name if r.created_by else "Système EVO-LOG"
        active_call = _SIGNALING.get_call(current_user.company_id, r.room_uuid) is not None

        members_list = []
        for m in r.members:
            if m.user:
                members_list.append(MeetingRoomMemberOut(
                    id=m.user.id,
                    username=m.user.username,
                    full_name=m.user.full_name or m.user.username,
                    role_title=get_user_official_role_title(m.user)
                ))

        out.append(MeetingRoomOut(
            id=r.id,
            room_uuid=r.room_uuid,
            name=r.name,
            topic=r.topic or "",
            channel_type=r.channel_type or "meeting",
            is_private=bool(r.is_private),
            active_call=active_call,
            created_by_id=r.created_by_id,
            created_by_name=creator_name,
            created_at=r.created_at or datetime.utcnow(),
            members_count=len(r.members),
            members=members_list
        ))
    return out


@router.post("/rooms", response_model=MeetingRoomOut, status_code=status.HTTP_201_CREATED)
def create_meeting_room(
    payload: CreateMeetingRoomSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_chat_user)
):
    """
    Create a new meeting room and invite specific employees.
    """
    if not payload.name or not payload.name.strip():
        raise HTTPException(status_code=400, detail="Le nom du salon est obligatoire.")

    room_uuid = f"meet-{uuid.uuid4().hex[:10]}"
    room = ChatMeetingRoom(
        room_uuid=room_uuid,
        name=payload.name.strip(),
        topic=payload.topic.strip() if payload.topic else "Réunion d'équipe opérationnelle",
        channel_type="meeting",
        is_private=bool(payload.is_private),
        company_id=current_user.company_id,
        created_by_id=current_user.id
    )
    db.add(room)
    db.flush()

    # Add creator as creator member
    creator_member = ChatRoomMember(
        room_id=room.id,
        user_id=current_user.id,
        role="creator"
    )
    db.add(creator_member)

    # Add invited participants
    unique_ids = set(payload.participant_ids or [])
    unique_ids.discard(current_user.id)
    for p_id in unique_ids:
        u = db.query(User).filter(User.id == p_id, User.is_active.is_(True)).first()
        if not u:
            raise HTTPException(status_code=404, detail=f"Participant introuvable: {p_id}")
        if not current_user.is_superuser and u.company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Tous les participants doivent appartenir à votre entreprise.")
        db.add(ChatRoomMember(room_id=room.id, user_id=u.id, role="member"))

    # Add initial system welcoming message
    welcome_msg = EnterpriseChatMessage(
        company_id=current_user.company_id,
        sender_id=current_user.id,
        room_id=room.id,
        channel_type="room",
        content=f"🤝 Salon de réunion « {room.name} » ouvert par {current_user.full_name or current_user.username}. Ordre du jour : {room.topic}",
        sender_name_snapshot=current_user.full_name or current_user.username,
        sender_role_snapshot=get_user_official_role_title(current_user),
        is_read=True
    )
    db.add(welcome_msg)

    db.commit()
    db.refresh(room)

    members_list = [
        MeetingRoomMemberOut(
            id=m.user.id,
            username=m.user.username,
            full_name=m.user.full_name or m.user.username,
            role_title=get_user_official_role_title(m.user)
        )
        for m in room.members if m.user
    ]

    return MeetingRoomOut(
        id=room.id,
        room_uuid=room.room_uuid,
        name=room.name,
        topic=room.topic,
        channel_type=room.channel_type,
        is_private=room.is_private,
        active_call=False,
        created_by_id=room.created_by_id,
        created_by_name=current_user.full_name or current_user.username,
        created_at=room.created_at or datetime.utcnow(),
        members_count=len(room.members),
        members=members_list
    )


@router.get("/rooms/{room_identifier}/messages", response_model=List[ChatMessageOut])
def get_room_messages(
    room_identifier: str,
    response: Response,
    limit: int = Query(50, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_chat_user)
):
    """Get all messages in a specific room or thematic channel."""
    # Find room by uuid or id
    room = _get_accessible_room(db, room_identifier, current_user)

    message_query = db.query(EnterpriseChatMessage).filter(
        EnterpriseChatMessage.room_id == room.id
    )
    cursor_id = _decode_message_cursor(cursor)
    if cursor_id is not None:
        message_query = message_query.filter(EnterpriseChatMessage.id < cursor_id)
    messages = message_query.order_by(
        EnterpriseChatMessage.created_at.desc(), EnterpriseChatMessage.id.desc()
    ).limit(limit + 1).all()
    has_more = len(messages) > limit
    messages = messages[:limit]
    messages.reverse()
    response.headers["X-Has-More"] = str(has_more).lower()
    if messages and has_more:
        response.headers["X-Next-Cursor"] = _encode_message_cursor(messages[-1].id)

    return [
        ChatMessageOut(
            id=m.id,
            company_id=m.company_id,
            sender_id=m.sender_id,
            recipient_id=m.recipient_id,
            room_id=m.room_id,
            channel_type=m.channel_type,
            content=m.content,
            sender_name=m.sender_name_snapshot or (m.sender.full_name if m.sender else "Utilisateur"),
            sender_role=m.sender_role_snapshot or (get_user_official_role_title(m.sender) if m.sender else "Collaborateur"),
            is_read=m.is_read,
            created_at=m.created_at or datetime.utcnow()
        )
        for m in messages
    ]


@router.post("/rooms/{room_identifier}/messages", response_model=ChatMessageOut)
async def send_room_message(
    room_identifier: str,
    payload: SendRoomMessageSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_chat_user)
):
    """Post a message inside a room or thematic channel."""
    if not payload.content or not payload.content.strip():
        raise HTTPException(status_code=400, detail="Le message ne peut pas être vide.")

    room = _get_accessible_room(db, room_identifier, current_user)

    msg = EnterpriseChatMessage(
        company_id=current_user.company_id,
        sender_id=current_user.id,
        recipient_id=None,
        room_id=room.id,
        channel_type="room",
        content=payload.content.strip(),
        sender_name_snapshot=current_user.full_name or current_user.username,
        sender_role_snapshot=get_user_official_role_title(current_user),
        is_read=False
    )
    db.add(msg)
    db.flush()
    # Salon prive : diffusion restreinte aux membres. Canal thematique public :
    # tout le tenant (metadata de message, jamais le contenu sur le wire).
    target_users = None
    if room.is_private:
        target_users = [
            m.user_id
            for m in db.query(ChatRoomMember.user_id).filter(
                ChatRoomMember.room_id == room.id
            ).all()
        ] or [current_user.id]
    outbox_evt = enqueue_event(
        db,
        event_type="chat.message.created",
        aggregate_type="chat_message",
        aggregate_id=str(msg.id),
        payload={
            "company_id": current_user.company_id,
            "message_id": msg.id,
            "room_id": msg.room_id,
            "room_uuid": room.room_uuid,
            "sender_id": msg.sender_id,
            "_target_users": target_users,
        },
    )
    db.commit()
    db.refresh(msg)
    # Diffusion temps reel immediate ; en cas d'echec l'evenement reste en
    # outbox et sera rejoue par le pump (ou le worker Celery).
    await deliver_outbox_event(db, outbox_evt)

    return ChatMessageOut(
        id=msg.id,
        company_id=msg.company_id,
        sender_id=msg.sender_id,
        recipient_id=msg.recipient_id,
        room_id=msg.room_id,
        channel_type=msg.channel_type,
        content=msg.content,
        sender_name=msg.sender_name_snapshot,
        sender_role=msg.sender_role_snapshot,
        is_read=msg.is_read,
        created_at=msg.created_at or datetime.utcnow()
    )


# ─── Endpoints : Signalisation WebRTC & Appels Vidéo ───

@router.get("/webrtc/config")
def get_webrtc_configuration():
    """Returns free public STUN servers for WebRTC peer-to-peer connection establishment."""
    return {
        "iceServers": [
            {"urls": "stun:stun.l.google.com:19302"},
            {"urls": "stun:stun1.l.google.com:19302"},
            {"urls": "stun:stun2.l.google.com:19302"},
            {"urls": "stun:stun3.l.google.com:19302"},
            {"urls": "stun:stun4.l.google.com:19302"}
        ]
    }


@router.post("/call/signal")
def dispatch_webrtc_signal(
    signal: WebRTCSignalIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_chat_user)
):
    """
    Relays WebRTC signals (offer, answer, ICE candidates, call-start, call-end)
    between peers in a room or direct call.
    """
    room_uuid = signal.room_uuid
    signal_type = signal.signal_type
    now = time.time()
    room = _get_accessible_room(db, room_uuid, current_user)
    if signal.target_user_id is not None:
        target = db.query(User).filter(
            User.id == signal.target_user_id,
            User.is_active.is_(True),
        ).first()
        if not target:
            raise HTTPException(status_code=404, detail="Destinataire introuvable.")
        target_member = db.query(ChatRoomMember).filter(
            ChatRoomMember.room_id == room.id,
            ChatRoomMember.user_id == target.id,
        ).first()
        if not target_member and target.id != room.created_by_id:
            raise HTTPException(status_code=403, detail="Destinataire non membre du salon.")

    envelope = {
        "id": f"sig-{uuid.uuid4().hex[:8]}",
        "room_uuid": room_uuid,
        "sender_id": current_user.id,
        "sender_name": current_user.full_name or current_user.username,
        "sender_role": get_user_official_role_title(current_user),
        "target_user_id": signal.target_user_id,
        "signal_type": signal_type,
        "payload": signal.payload,
        "timestamp": now
    }

    call_state = _SIGNALING.fetch(current_user.company_id, room_uuid, current_user.id, 0)[0]
    if signal_type == "call-start":
        call_state = {
            "started_at": now,
            "initiator_id": current_user.id,
            "initiator_name": current_user.full_name or current_user.username,
            "participants": {
                str(current_user.id): {
                    "joined_at": now,
                    "name": current_user.full_name or current_user.username
                }
            }
        }
        _SIGNALING.set_call(current_user.company_id, room_uuid, call_state)
    elif signal_type == "user-joined":
        if call_state is None:
            call_state = {
                "started_at": now,
                "initiator_id": current_user.id,
                "initiator_name": current_user.full_name or current_user.username,
                "participants": {}
            }
        call_state["participants"][str(current_user.id)] = {
            "joined_at": now,
            "name": current_user.full_name or current_user.username
        }
        _SIGNALING.set_call(current_user.company_id, room_uuid, call_state)
    elif signal_type == "call-end":
        _SIGNALING.end_call(current_user.company_id, room_uuid)

    _SIGNALING.dispatch(
        current_user.company_id,
        room_uuid,
        envelope,
        signal.target_user_id,
    )

    return {"status": "dispatched", "signal_id": envelope["id"]}


@router.get("/call/signals/{room_uuid}")
def fetch_pending_signals(
    room_uuid: str,
    since: Optional[float] = Query(0.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_chat_user)
):
    """
    Fetch pending WebRTC signals intended for the current user or broadcast in the room.
    """
    room = _get_accessible_room(db, room_uuid, current_user)
    call_state, results = _SIGNALING.fetch(
        current_user.company_id, room_uuid, current_user.id, since
    )
    return {
        "room_uuid": room_uuid,
        "is_active": call_state is not None,
        "call_info": call_state,
        "signals": results
    }


@router.get("/call/status/{room_uuid}")
def get_call_status(
    room_uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_chat_user)
):
    """Returns whether there is an ongoing video call in this room."""
    _get_accessible_room(db, room_uuid, current_user)
    call_state = _SIGNALING.get_call(current_user.company_id, room_uuid)
    return {
        "room_uuid": room_uuid,
        "active": call_state is not None,
        "details": call_state
    }


# ============ LIAISON CONTEXTUELLE CHAT -> DOSSIER MÉTIER ============
@router.post("/contextual-pin")
def epingler_discussion_dossier(
    payload: dict,
    current_user: User = Depends(get_current_chat_user),
):
    """Pinning requires a persisted business-entity integration."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Contextual dossier pinning is not configured.",
    )


# ============ PUSH-TO-TALK WEBRTC TALKIE-WALKIE VIRTUEL ============
@router.post("/webrtc/push-to-talk")
def session_push_to_talk():
    """Push-to-talk requires a configured signaling provider."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Push-to-talk signaling provider is not configured.",
    )


# ============ PASSERELLE SMS D'URGENCE CHAUFFEURS HORS-DATA ============
@router.post("/sms-gateway/send-urgent")
def envoyer_sms_urgent_chauffeur():
    """SMS delivery requires a configured telecom provider."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Urgent SMS provider is not configured.",
    )
