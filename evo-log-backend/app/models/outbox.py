"""Transactional outbox persistence model."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from sqlalchemy import DateTime, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OutboxEvent(Base):
    """An event committed with its business transaction before delivery."""

    __tablename__ = "outbox_events"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "event_type",
            "aggregate_type",
            "aggregate_id",
            "dedupe_key",
            name="uq_outbox_event_dedupe",
        ),
        Index("ix_outbox_events_delivery", "status", "available_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    event_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    company_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(120), nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(80), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(160), nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    dedupe_key: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
