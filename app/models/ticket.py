from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_name: Mapped[str] = mapped_column(String(120))
    customer_email: Mapped[str] = mapped_column(String(320), index=True)
    subject: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)

    category: Mapped[str] = mapped_column(String(32), default="unclassified")
    urgency: Mapped[str] = mapped_column(String(16), default="unknown")
    language: Mapped[str] = mapped_column(String(16), default="unknown")
    summary: Mapped[str] = mapped_column(String(500), default="")
    classification_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    classification_source: Mapped[str] = mapped_column(String(16), default="fallback")

    priority: Mapped[str] = mapped_column(String(16), default="normal")
    sla_hours: Mapped[int] = mapped_column(Integer, default=12)
    sla_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    priority_reason: Mapped[str] = mapped_column(String(500), default="")

    draft_reply: Mapped[str] = mapped_column(Text, default="")
    reply_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    reply_source: Mapped[str] = mapped_column(String(16), default="")
    reply_source_refs: Mapped[str] = mapped_column(Text, default="[]")
    needs_human_review: Mapped[bool] = mapped_column(Boolean, default=True)

    status: Mapped[str] = mapped_column(String(32), default="new")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
