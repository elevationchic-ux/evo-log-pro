"""Redis-backed, tenant-scoped realtime event fanout."""
import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisUnavailableError(RuntimeError):
    """Raised when realtime delivery cannot be made durable across processes."""


class ReactiveEventBus:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis = None
        self.pubsub = None
        self._subscriber_task = None
        self._origin = uuid.uuid4().hex
        self.tenant_connections: Dict[int, Dict[str, List[Any]]] = {}
        self.department_connections: Dict[int, Dict[str, Dict[str, List[Any]]]] = {}
        self.internal_listeners: Dict[str, List[Callable]] = {}
        self.event_history: List[dict] = []

    async def start(self):
        if self.redis is not None:
            return
        client = aioredis.from_url(self.redis_url, decode_responses=True)
        try:
            await client.ping()
            pubsub = client.pubsub()
            await pubsub.psubscribe("evo-log:events:tenant:*")
        except Exception as exc:
            await client.aclose()
            raise RedisUnavailableError(f"Redis realtime bus unavailable: {exc}") from exc
        self.redis, self.pubsub = client, pubsub
        self._subscriber_task = asyncio.create_task(self._consume())

    async def stop(self):
        if self._subscriber_task:
            self._subscriber_task.cancel()
            await asyncio.gather(self._subscriber_task, return_exceptions=True)
        if self.pubsub:
            await self.pubsub.close()
        if self.redis:
            await self.redis.aclose()
        self._subscriber_task = self.pubsub = self.redis = None

    async def _ensure_started(self):
        if self.redis is None:
            await self.start()
        try:
            await self.redis.ping()
        except Exception as exc:
            raise RedisUnavailableError(f"Redis realtime bus unavailable: {exc}") from exc

    async def _consume(self):
        try:
            async for message in self.pubsub.listen():
                if message.get("type") not in ("pmessage", "message"):
                    continue
                payload = json.loads(message["data"])
                if payload.get("_origin") == self._origin:
                    continue
                await self._deliver(payload, include_listeners=True)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Redis realtime subscriber stopped")

    async def _deliver(self, payload: dict, include_listeners: bool = True):
        company_id = payload["company_id"]
        recipients = []
        if company_id in self.tenant_connections:
            target_users = payload.get("target_users")
            target_departments = payload.get("target_departments")
            if target_users:
                for uid in target_users:
                    recipients.extend(self.tenant_connections[company_id].get(str(uid), []))
            elif target_departments:
                for dept in target_departments:
                    for conns in self.department_connections.get(company_id, {}).get(dept.lower(), {}).values():
                        recipients.extend(conns)
            else:
                for conns in self.tenant_connections[company_id].values():
                    recipients.extend(conns)
        for conn in set(recipients):
            try:
                await conn.send_json({k: v for k, v in payload.items() if k != "_origin"})
            except Exception:
                logger.debug("Unable to deliver realtime event to socket", exc_info=True)
        if include_listeners:
            for listener in self.internal_listeners.get(payload["type"], []):
                try:
                    result = listener(company_id, payload["data"])
                    if asyncio.iscoroutine(result):
                        asyncio.create_task(result)
                except Exception:
                    logger.exception("Realtime listener failed for %s", payload["type"])

    def subscribe(self, event_type: str, callback: Callable):
        self.internal_listeners.setdefault(event_type, []).append(callback)

    def add_connection(self, company_id, user_id, connection, department=None):
        self.tenant_connections.setdefault(company_id, {}).setdefault(str(user_id), []).append(connection)
        if department:
            self.department_connections.setdefault(company_id, {}).setdefault(department.lower(), {}).setdefault(str(user_id), []).append(connection)

    def remove_connection(self, company_id, user_id, connection, department=None):
        def remove(users):
            conns = users.get(str(user_id), [])
            if connection in conns:
                conns.remove(connection)
            if not conns:
                users.pop(str(user_id), None)
        remove(self.tenant_connections.get(company_id, {}))
        if department:
            remove(self.department_connections.get(company_id, {}).get(department.lower(), {}))

    async def emit_tenant_event(self, company_id, event_type, data, target_departments=None, target_users=None):
        await self._ensure_started()
        payload = {"type": event_type, "company_id": company_id, "data": data,
                   "target_departments": target_departments, "target_users": target_users,
                   "timestamp": datetime.utcnow().isoformat(), "_origin": self._origin}
        try:
            await self.redis.publish(f"evo-log:events:tenant:{company_id}", json.dumps(payload))
        except Exception as exc:
            raise RedisUnavailableError(f"Redis publish failed: {exc}") from exc
        self.event_history.append(payload)
        self.event_history = self.event_history[-1000:]
        await self._deliver(payload, include_listeners=True)

    async def broadcast_event(self, event_type, data, target_users=None):
        await self.emit_tenant_event(data.get("company_id") or 1, event_type, data, target_users=target_users)

    async def broadcast_heartbeat(self):
        for company_id, users in self.tenant_connections.items():
            for connections in users.values():
                for conn in connections:
                    try:
                        await conn.send_json({"type": "heartbeat", "timestamp": datetime.utcnow().isoformat()})
                    except Exception:
                        pass


event_service = ReactiveEventBus()
event_bus = event_service
