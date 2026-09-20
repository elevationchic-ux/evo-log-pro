from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
import asyncio
from app.utils.tenant import get_current_tenant_context, TenantContext

router = APIRouter(tags=["Collaboration"], dependencies=[Depends(get_current_tenant_context)])

class CollabMessage(BaseModel):
    room_id: str
    user_id: str
    user_nom: str
    message: str
    type: Optional[str] = "TEXT"  # TEXT, SYSTEM, FILE, MISSION_UPDATE

class Room(BaseModel):
    room_id: str
    nom: str
    module: Optional[str] = "GENERAL"
    participants: Optional[List[str]] = []

# Gestion des rooms de collaboration
_rooms: Dict[str, dict] = {}
_messages: Dict[str, List[dict]] = {}

# Connexions WebSocket par room
_room_connections: Dict[str, List[WebSocket]] = {}

@router.get("/rooms")
def list_rooms():
    raise HTTPException(status_code=501, detail="La persistance de la collaboration n'est pas encore implémentée.")

@router.post("/rooms")
def create_room(data: Room):
    raise HTTPException(status_code=501, detail="La persistance de la collaboration n'est pas encore implémentée.")

@router.get("/rooms/{room_id}")
def get_room(room_id: str):
    raise HTTPException(status_code=501, detail="La persistance de la collaboration n'est pas encore implémentée.")

@router.get("/rooms/{room_id}/messages")
def get_room_messages(room_id: str, limit: int = 50):
    raise HTTPException(status_code=501, detail="La persistance de la collaboration n'est pas encore implémentée.")

@router.post("/rooms/{room_id}/messages")
def send_message(room_id: str, data: CollabMessage):
    raise HTTPException(status_code=501, detail="La persistance de la collaboration n'est pas encore implémentée.")

@router.websocket("/ws/{room_id}")
async def websocket_collaboration(websocket: WebSocket, room_id: str, user_id: Optional[str] = None):
    """WebSocket temps réel pour collaboration par room"""
    await websocket.close(code=1008, reason="La collaboration persistante n'est pas encore implémentée.")
    return

    if room_id not in _room_connections:
        _room_connections[room_id] = []
    _room_connections[room_id].append(websocket)

    try:
        # Notifier les participants
        join_msg = {
            "type": "user_joined",
            "room_id": room_id,
            "user_id": user_id or "anonymous",
            "timestamp": datetime.utcnow().isoformat()
        }
        for ws in _room_connections.get(room_id, []):
            try:
                await ws.send_json(join_msg)
            except Exception:
                pass

        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
                # Broadcaster le message à la room
                broadcast_msg = {
                    "type": "message",
                    "room_id": room_id,
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat()
                }
                for ws in _room_connections.get(room_id, []):
                    try:
                        await ws.send_json(broadcast_msg)
                    except Exception:
                        pass
            except asyncio.TimeoutError:
                await websocket.send_json({
                    "type": "heartbeat",
                    "room_id": room_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
    except WebSocketDisconnect:
        if room_id in _room_connections:
            _room_connections[room_id] = [ws for ws in _room_connections[room_id] if ws != websocket]
