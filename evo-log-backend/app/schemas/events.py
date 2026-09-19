"""Typed contracts for events persisted in the transactional outbox."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventEnvelope(BaseModel):
    """Stable, tenant-scoped event contract shared by producers and consumers."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID = Field(default_factory=uuid4)
    event_type: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9][a-z0-9_.-]*$")
    company_id: int = Field(gt=0)
    aggregate_type: str = Field(min_length=1, max_length=80)
    aggregate_id: str = Field(min_length=1, max_length=160)
    payload: Dict[str, Any]
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    dedupe_key: Optional[str] = Field(default=None, max_length=200)

    @field_validator("occurred_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("occurred_at must include a timezone")
        return value.astimezone(timezone.utc)
