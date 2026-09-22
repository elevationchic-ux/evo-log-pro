from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
import asyncio
import json
import redis
from app.utils.tenant import get_current_tenant_context, TenantContext
from app.core.config import settings

router = APIRouter(tags=["Collaboration"], dependencies=[Depends(get_current_tenant_context)])

# Redis Pub/Sub for real-time multi-tenant collaboration
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
pubsub = redis_client.pubsub()

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

# WebSocket connections per room (for in-memory fallback)
_room_connections: Dict[str, List[WebSocket]] = {}

def get_room_key(tenant_id: int, room_id: str) -> str:
    """Generate tenant-isolated room key."""
    return f"collab:tenant:{tenant_id}:room:{room_id}"

def get_message_channel(tenant_id: int, room_id: str) -> str:
    """Generate Redis Pub/Sub channel for room messages."""
    return f"collab:tenant:{tenant_id}:messages:{room_id}"

@router.get("/rooms")
def list_rooms(context: TenantContext = Depends(get_current_tenant_context)):
    """List all collaboration rooms for the tenant."""
    try:
        pattern = f"collab:tenant:{context.organization_id}:room:*"
        room_keys = redis_client.keys(pattern)
        rooms = []
        for key in room_keys:
            room_data = redis_client.get(key)
            if room_data:
                rooms.append(json.loads(room_data))
        return {"rooms": rooms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des rooms: {str(e)}")

@router.post("/rooms")
def create_room(data: Room, context: TenantContext = Depends(get_current_tenant_context)):
    """Create a new collaboration room."""
    try:
        room_key = get_room_key(context.organization_id, data.room_id)
        room_data = {
            "room_id": data.room_id,
            "nom": data.nom,
            "module": data.module,
            "participants": data.participants or [],
            "created_at": datetime.utcnow().isoformat(),
            "tenant_id": context.organization_id
        }
        redis_client.setex(room_key, 86400, json.dumps(room_data))  # 24h TTL
        return {"room": room_data, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la room: {str(e)}")

@router.get("/rooms/{room_id}")
def get_room(room_id: str, context: TenantContext = Depends(get_current_tenant_context)):
    """Get a specific room."""
    try:
        room_key = get_room_key(context.organization_id, room_id)
        room_data = redis_client.get(room_key)
        if not room_data:
            raise HTTPException(status_code=404, detail="Room non trouvée")
        return {"room": json.loads(room_data)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la room: {str(e)}")

@router.get("/rooms/{room_id}/messages")
def get_room_messages(room_id: str, limit: int = 50, context: TenantContext = Depends(get_current_tenant_context)):
    """Get message history for a room."""
    try:
        messages_key = f"collab:tenant:{context.organization_id}:messages:{room_id}"
        messages = redis_client.lrange(messages_key, -limit, -1)
        return {"messages": [json.loads(m) for m in messages] if messages else []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des messages: {str(e)}")

@router.post("/rooms/{room_id}/messages")
def send_message(room_id: str, data: CollabMessage, context: TenantContext = Depends(get_current_tenant_context)):
    """Send a message to a room (via Redis Pub/Sub)."""
    try:
        message = {
            "room_id": room_id,
            "user_id": data.user_id,
            "user_nom": data.user_nom,
            "message": data.message,
            "type": data.type,
            "timestamp": datetime.utcnow().isoformat(),
            "tenant_id": context.organization_id
        }
        
        # Store in Redis list for history
        messages_key = f"collab:tenant:{context.organization_id}:messages:{room_id}"
        redis_client.lpush(messages_key, json.dumps(message))
        redis_client.ltrim(messages_key, 0, 1000)  # Keep last 1000 messages
        
        # Publish to Pub/Sub for real-time delivery
        channel = get_message_channel(context.organization_id, room_id)
        redis_client.publish(channel, json.dumps(message))
        
        return {"message": message, "status": "sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi du message: {str(e)}")

@router.websocket("/ws/{room_id}")
async def websocket_collaboration(websocket: WebSocket, room_id: str, user_id: Optional[str] = None):
    """WebSocket temps réel pour collaboration par room avec Redis Pub/Sub."""
    await websocket.accept()
    
    # Store connection for fallback
    if room_id not in _room_connections:
        _room_connections[room_id] = []
    _room_connections[room_id].append(websocket)
    
    # Subscribe to Redis Pub/Sub channel
    channel = f"collab:messages:{room_id}"  # Simplified for demo
    pubsub.subscribe(channel)
    
    try:
        while True:
            # Check for Redis messages with timeout
            message = pubsub.get_message(timeout=1.0)
            if message:
                await websocket.send_json(message["data"])
            
            # Also handle direct WebSocket messages
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)
                # Echo back or process
                await websocket.send_json({"type": "echo", "data": data})
            except asyncio.TimeoutError:
                pass
    except WebSocketDisconnect:
        if room_id in _room_connections:
            _room_connections[room_id] = [ws for ws in _room_connections[room_id] if ws != websocket]
    finally:
        pubsub.unsubscribe(channel)
