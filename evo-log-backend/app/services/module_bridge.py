"""Cross-module event transport for ERP data propagation."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.services.events.event_service import event_service


class ModuleDataBridge:
    """Reliable, tenant-aware event bridge between modules."""

    def __init__(self):
        self.messages: List[Dict[str, Any]] = []

    def _message(self, **kwargs) -> Dict[str, Any]:
        payload = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }
        self.messages.append(payload)
        return payload

    async def dispatch_async(
        self,
        source_module: str,
        target_module: str,
        payload: Dict[str, Any],
        *,
        company_id: Optional[int] = None,
        department_id: Optional[int] = None,
        initiated_by: Optional[int] = None,
        correlation_id: Optional[str] = None,
        target_users: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if not source_module or not target_module:
            raise ValueError("source_module and target_module are required")

        message = self._message(
            source_module=source_module,
            target_module=target_module,
            payload=payload,
            company_id=company_id,
            department_id=department_id,
            initiated_by=initiated_by,
            correlation_id=correlation_id or str(uuid.uuid4()),
        )

        await event_service.broadcast_event(
            "module.transfer",
            message,
            target_users=target_users,
            company_id=company_id,
            department_id=department_id,
        )
        return message

    def dispatch(
        self,
        source_module: str,
        target_module: str,
        payload: Dict[str, Any],
        **kwargs,
    ) -> Dict[str, Any]:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return self._message(
                source_module=source_module,
                target_module=target_module,
                payload=payload,
                **kwargs,
            )

        loop.create_task(
            self.dispatch_async(
                source_module=source_module,
                target_module=target_module,
                payload=payload,
                **kwargs,
            )
        )
        return self._message(
            source_module=source_module,
            target_module=target_module,
            payload=payload,
            **kwargs,
        )

    def history(self, *, company_id: Optional[int] = None, target_module: Optional[str] = None) -> List[Dict[str, Any]]:
        history = self.messages
        if company_id is not None:
            history = [item for item in history if item.get("company_id") == company_id]
        if target_module is not None:
            history = [item for item in history if item.get("target_module") == target_module]
        return history[-50:]


module_bridge = ModuleDataBridge()
