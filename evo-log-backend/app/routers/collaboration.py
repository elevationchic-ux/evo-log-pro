"""Authenticated, company-scoped collaboration rooms."""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.core.database import SessionLocal
from app.core.security import authenticate_websocket, get_current_user

router = APIRouter(tags=["Collaboration"])


class CollabMessage(BaseModel):
    room_id: str
    message: str
    type: str = "TEXT"


class Room(BaseModel):
    room_id: str
    nom: str
    module: str = "GENERAL"
    participants: List[str] = Field(default_factory=list)


_rooms: Dict[str, dict] = {}
_messages: Dict[str, List[dict]] = {}
_room_connections: Dict[str, List[WebSocket]] = {}


def _room_for_user(room_id: str, user) -> dict:
    room = _rooms.get(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room non trouvée")
    if not user.is_superuser and (
        room.get("company_id") != user.company_id
        or str(user.id) not in room.get("participants", [])
    ):
        raise HTTPException(status_code=403, detail="Room access denied")
    return room


@router.get("/rooms")
def list_rooms(current_user=Depends(get_current_user)):
    rooms = [
        room for room in _rooms.values()
        if current_user.is_superuser
        or (
            room.get("company_id") == current_user.company_id
            and str(current_user.id) in room.get("participants", [])
        )
    ]
    return {"total": len(rooms), "rooms": rooms}


@router.post("/rooms")
def create_room(data: Room, current_user=Depends(get_current_user)):
    if current_user.company_id is None and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Active company is required")
    participants = set(data.participants)
    participants.add(str(current_user.id))
    room = {
        **data.model_dump(),
        "participants": sorted(participants),
        "company_id": current_user.company_id,
        "created_at": datetime.utcnow().isoformat(),
    }
    _rooms[data.room_id] = room
    _messages[data.room_id] = []
    return room


@router.get("/rooms/{room_id}")
def get_room(room_id: str, current_user=Depends(get_current_user)):
    return _room_for_user(room_id, current_user)


@router.get("/rooms/{room_id}/messages")
def get_room_messages(room_id: str, limit: int = 50, current_user=Depends(get_current_user)):
    _room_for_user(room_id, current_user)
    messages = _messages.get(room_id, [])
    return {"room_id": room_id, "total": len(messages), "messages": messages[-max(1, min(limit, 100)):]}


@router.post("/rooms/{room_id}/messages")
def send_message(room_id: str, data: CollabMessage, current_user=Depends(get_current_user)):
    _room_for_user(room_id, current_user)
    messages = _messages.setdefault(room_id, [])
    message = {
        "id": len(messages) + 1,
        "user_id": str(current_user.id),
        "user_nom": current_user.full_name or current_user.username,
        "message": data.message,
        "type": data.type,
        "timestamp": datetime.utcnow().isoformat(),
    }
    messages.append(message)
    return message


@router.websocket("/ws/{room_id}")
async def websocket_collaboration(websocket: WebSocket, room_id: str):
    db = SessionLocal()
    try:
        try:
            user = authenticate_websocket(websocket, db)
            _room_for_user(room_id, user)
        except HTTPException:
            await websocket.close(code=1008)
            return
        await websocket.accept()
        connections = _room_connections.setdefault(room_id, [])
        connections.append(websocket)
        try:
            while True:
                try:
                    data = await asyncio.wait_for(websocket.receive_json(), timeout=30)
                    await websocket.send_json({
                        "type": "message",
                        "room_id": room_id,
                        "data": data,
                        "user_id": str(user.id),
                    })
                except asyncio.TimeoutError:
                    await websocket.send_json({
                        "type": "heartbeat",
                        "room_id": room_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    })
        except WebSocketDisconnect:
            pass
        finally:
            connections.remove(websocket)
    finally:
        db.close()
