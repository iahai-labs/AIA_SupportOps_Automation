from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.models.ticket import Ticket


@dataclass(frozen=True)
class ReviewDecision:
    status: str
    approved_reply: str
    reviewed_by: str
    review_note: str
    reviewed_at: datetime


def approve_ticket(
    ticket: Ticket,
    *,
    reviewed_by: str,
    note: str = "",
    approved_reply: str | None = None,
) -> ReviewDecision:
    if ticket.status != "waiting_review":
        raise ValueError("Only tickets waiting for review can be approved")

    final_reply = (approved_reply or ticket.draft_reply).strip()
    if not final_reply:
        raise ValueError("An approved reply is required")

    return ReviewDecision(
        status="approved",
        approved_reply=final_reply,
        reviewed_by=reviewed_by.strip(),
        review_note=note.strip(),
        reviewed_at=datetime.now(UTC),
    )


def reject_ticket(
    ticket: Ticket,
    *,
    reviewed_by: str,
    note: str = "",
) -> ReviewDecision:
    if ticket.status != "waiting_review":
        raise ValueError("Only tickets waiting for review can be rejected")

    return ReviewDecision(
        status="rejected",
        approved_reply="",
        reviewed_by=reviewed_by.strip(),
        review_note=note.strip(),
        reviewed_at=datetime.now(UTC),
    )
