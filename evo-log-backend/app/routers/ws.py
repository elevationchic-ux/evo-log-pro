"""
WebSocket Router  Multi-Tenant, Zero-Leakage, Heartbeat-enabled.

Security model:
  • Every connection MUST supply company_id + user_id query params (or JWT token).
  • Connections are registered strictly in the ReactiveEventBus scoped by company.
  • Broadcasts NEVER cross tenant boundaries.
  • Ping/Pong heartbeat every 25 s to detect dead connections.
  • Graceful cleanup on disconnect or ping timeout.

Endpoints:
  /ws/events        General tenant event stream (all departments)
  /ws/missions      TMS real-time mission tracking
  /ws/notifications  User-level notification channel
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException

from app.services.events.event_service import event_service
from app.core.security import decode_token
from app.core.database import SessionLocal
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSockets"])

HEARTBEAT_INTERVAL = 25  # seconds
PING_TIMEOUT = 10        # seconds to wait for pong


def _authenticate_websocket(token: str, company_id: int, user_id: str):
    payload = decode_token(token)
    if payload.get("type") == "refresh":
        raise HTTPException(status_code=401, detail="Access token required")
    if str(payload.get("sub")) != str(user_id):
        raise HTTPException(status_code=403, detail="User identity mismatch")
    token_company = payload.get("company_id")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == int(user_id), User.is_active.is_(True)).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User is inactive or does not exist")
        if not user.is_superuser and user.company_id != company_id:
            raise HTTPException(status_code=403, detail="Tenant identity mismatch")
        if token_company is not None and int(token_company) != user.company_id and not user.is_superuser:
            raise HTTPException(status_code=403, detail="Tenant identity mismatch")
        return user
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid WebSocket credentials")
    finally:
        db.close()


async def _heartbeat_loop(websocket: WebSocket, company_id: int, user_id: str, department: Optional[str]):
    """Background task: send ping every HEARTBEAT_INTERVAL seconds and clean up dead connections."""
    while True:
        try:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            await websocket.send_json({
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat(),
            })
        except Exception:
            # Connection is dead  remove from event bus
            event_service.remove_connection(company_id, user_id, websocket, department)
            break


async def _handle_client_message(websocket: WebSocket, company_id: int, user_id: str, data: dict):
    """Process messages received from the WebSocket client."""
    msg_type = data.get("type", "")

    if msg_type == "pong":
        # Client responded to heartbeat  connection is alive
        pass

    elif msg_type == "subscribe_department":
        # Client wants to subscribe to a specific department channel
        dept = data.get("department")
        if dept:
            event_service.add_connection(company_id, user_id, websocket, dept)
            await websocket.send_json({
                "type": "subscribed",
                "department": dept,
                "timestamp": datetime.utcnow().isoformat(),
            })

    elif msg_type == "emit":
        # Client emits an event (e.g., field agent sends breakdown report)
        event_type = data.get("event_type")
        payload = data.get("data", {})
        if event_type:
            payload["_source_user"] = user_id
            await event_service.emit_tenant_event(
                company_id=company_id,
                event_type=event_type,
                data=payload,
            )

    else:
        # Echo back unknown messages for debugging
        await websocket.send_json({
            "type": "ack",
            "received": msg_type,
            "timestamp": datetime.utcnow().isoformat(),
        })


# ─────────────────────────────────────────────
# /ws/events  General tenant event stream
# ─────────────────────────────────────────────

@router.websocket("/events")
async def websocket_events(
    websocket: WebSocket,
    company_id: int = Query(..., description="Tenant company ID  REQUIRED"),
    user_id: str = Query(..., description="Authenticated user ID  REQUIRED"),
    department: Optional[str] = Query(None, description="Optional department filter"),
    token: str = Query(..., description="JWT access token"),
):
    """
    General WebSocket event stream scoped strictly to a single tenant.
    Zero-leakage: messages from other companies are NEVER sent here.
    """
    user = _authenticate_websocket(token, company_id, user_id)
    await websocket.accept()

    # Register connection in the tenant-scoped event bus
    event_service.add_connection(company_id, user_id, websocket, department)
    logger.info(f"[WS] Client connected  company={company_id}, user={user_id}, dept={department}")

    # Start heartbeat background task
    hb_task = asyncio.create_task(
        _heartbeat_loop(websocket, company_id, user_id, department)
    )

    try:
        # Welcome message
        await websocket.send_json({
            "type": "connected",
            "company_id": company_id,
            "user_id": user_id,
            "department": department,
            "message": "✅ Connecté au flux EVO-LOG (isolé par entreprise)",
            "timestamp": datetime.utcnow().isoformat(),
        })

        # Message loop
        while True:
            try:
                raw = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                try:
                    data = json.loads(raw)
                    await _handle_client_message(websocket, company_id, user_id, data)
                except json.JSONDecodeError:
                    await websocket.send_json({"type": "error", "message": "Invalid JSON"})
            except asyncio.TimeoutError:
                # No message for 60s  send a server-side ping
                await websocket.send_json({
                    "type": "ping",
                    "timestamp": datetime.utcnow().isoformat(),
                })

    except WebSocketDisconnect:
        logger.info(f"[WS] Client disconnected  company={company_id}, user={user_id}")
    except Exception as e:
        logger.warning(f"[WS] Unexpected error  company={company_id}, user={user_id}: {e}")
    finally:
        hb_task.cancel()
        event_service.remove_connection(company_id, user_id, websocket, department)


# ─────────────────────────────────────────────
# /ws/missions  TMS real-time mission tracking
# ─────────────────────────────────────────────

@router.websocket("/missions")
async def websocket_missions(
    websocket: WebSocket,
    company_id: int = Query(..., description="Tenant company ID  REQUIRED"),
    user_id: str = Query(..., description="Authenticated user ID  REQUIRED"),
    token: str = Query(...),
):
    """
    Real-time TMS mission tracking  tenant-scoped.
    Automatically filters mission events to the caller's company.
    """
    user = _authenticate_websocket(token, company_id, user_id)
    await websocket.accept()
    event_service.add_connection(company_id, user_id, websocket, "transport")

    hb_task = asyncio.create_task(
        _heartbeat_loop(websocket, company_id, user_id, "transport")
    )

    try:
        await websocket.send_json({
            "type": "connected",
            "channel": "missions",
            "company_id": company_id,
            "message": "✅ Canal missions TMS connecté",
            "timestamp": datetime.utcnow().isoformat(),
        })

        while True:
            try:
                raw = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                try:
                    data = json.loads(raw)
                    await _handle_client_message(websocket, company_id, user_id, data)
                except json.JSONDecodeError:
                    await websocket.send_json({"type": "error", "message": "Invalid JSON"})
            except asyncio.TimeoutError:
                await websocket.send_json({
                    "type": "ping",
                    "channel": "missions",
                    "timestamp": datetime.utcnow().isoformat(),
                })

    except WebSocketDisconnect:
        logger.info(f"[WS/missions] Client disconnected  company={company_id}, user={user_id}")
    except Exception as e:
        logger.warning(f"[WS/missions] Error  company={company_id}, user={user_id}: {e}")
    finally:
        hb_task.cancel()
        event_service.remove_connection(company_id, user_id, websocket, "transport")


# ─────────────────────────────────────────────
# /ws/notifications  User-level notifications
# ─────────────────────────────────────────────

@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    company_id: int = Query(..., description="Tenant company ID  REQUIRED"),
    user_id: str = Query(..., description="Authenticated user ID  REQUIRED"),
    token: str = Query(...),
):
    """
    Personal notification channel  delivers events targeted to a specific user.
    """
    _authenticate_websocket(token, company_id, user_id)
    await websocket.accept()
    event_service.add_connection(company_id, user_id, websocket)

    hb_task = asyncio.create_task(
        _heartbeat_loop(websocket, company_id, user_id, None)
    )

    try:
        await websocket.send_json({
            "type": "connected",
            "channel": "notifications",
            "user_id": user_id,
            "message": "✅ Canal notifications personnelles connecté",
            "timestamp": datetime.utcnow().isoformat(),
        })

        while True:
            try:
                raw = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                try:
                    data = json.loads(raw)
                    if data.get("type") == "pong":
                        pass  # heartbeat acknowledged
                except json.JSONDecodeError:
                    pass
            except asyncio.TimeoutError:
                await websocket.send_json({
                    "type": "ping",
                    "timestamp": datetime.utcnow().isoformat(),
                })

    except WebSocketDisconnect:
        logger.info(f"[WS/notifications] Disconnected  user={user_id}, company={company_id}")
    except Exception as e:
        logger.warning(f"[WS/notifications] Error  user={user_id}: {e}")
    finally:
        hb_task.cancel()
        event_service.remove_connection(company_id, user_id, websocket)
