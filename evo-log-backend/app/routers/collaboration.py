from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
import asyncio

router = APIRouter(tags=["Collaboration"])

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
_rooms: Dict[str, dict] = {
    "transport-dispatch": {
        "room_id": "transport-dispatch",
        "nom": "Dispatch Transport",
        "module": "TRANSPORT",
        "participants": ["dispatcher-001", "chauffeur-001", "chauffeur-002"],
        "created_at": datetime.utcnow().isoformat()
    },
    "magasin-wms": {
        "room_id": "magasin-wms",
        "nom": "Opérations WMS MAG3",
        "module": "MAGASIN",
        "participants": ["magasinier-001", "chef-magasin-001"],
        "created_at": datetime.utcnow().isoformat()
    },
    "global-ops": {
        "room_id": "global-ops",
        "nom": "Opérations Globales Port Douala",
        "module": "GENERAL",
        "participants": ["admin-001", "dispatcher-001", "chef-magasin-001"],
        "created_at": datetime.utcnow().isoformat()
    }
}

_messages: Dict[str, List[dict]] = {
    "transport-dispatch": [
        {"id": 1, "user_id": "dispatcher-001", "user_nom": "Marie NGUEMA", "message": "Mission OT-2026-00401 confirmée. MVONDO Jean-Marc prend le départ à 06h00.", "type": "MISSION_UPDATE", "timestamp": datetime.utcnow().isoformat()},
        {"id": 2, "user_id": "chauffeur-001", "user_nom": "Jean-Marc MVONDO", "message": "Chargement terminé. En route pour N'Djamena. ETA 16 août à 14h00.", "type": "TEXT", "timestamp": datetime.utcnow().isoformat()},
    ],
    "global-ops": [
        {"id": 1, "user_id": "admin-001", "user_nom": "Administrateur", "message": "Bienvenue dans le centre opérationnel EVO-LOG Port de Douala.", "type": "SYSTEM", "timestamp": datetime.utcnow().isoformat()},
    ]
}

# Connexions WebSocket par room
_room_connections: Dict[str, List[WebSocket]] = {}

@router.get("/rooms")
def list_rooms():
    return {"total": len(_rooms), "rooms": list(_rooms.values())}

@router.post("/rooms")
def create_room(data: Room):
    room = {**data.dict(), "created_at": datetime.utcnow().isoformat()}
    _rooms[data.room_id] = room
    _messages[data.room_id] = []
    return room

@router.get("/rooms/{room_id}")
def get_room(room_id: str):
    room = _rooms.get(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room non trouvée")
    return room

@router.get("/rooms/{room_id}/messages")
def get_room_messages(room_id: str, limit: int = 50):
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room non trouvée")
    msgs = _messages.get(room_id, [])
    return {"room_id": room_id, "total": len(msgs), "messages": msgs[-limit:]}

@router.post("/rooms/{room_id}/messages")
def send_message(room_id: str, data: CollabMessage):
    if room_id not in _rooms:
        raise HTTPException(status_code=404, detail="Room non trouvée")
    if room_id not in _messages:
        _messages[room_id] = []
    msg_id = len(_messages[room_id]) + 1
    msg = {
        "id": msg_id,
        "user_id": data.user_id,
        "user_nom": data.user_nom,
        "message": data.message,
        "type": data.type,
        "timestamp": datetime.utcnow().isoformat()
    }
    _messages[room_id].append(msg)
    return msg

@router.websocket("/ws/{room_id}")
async def websocket_collaboration(websocket: WebSocket, room_id: str, user_id: Optional[str] = None):
    """WebSocket temps réel pour collaboration par room"""
    await websocket.accept()

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
