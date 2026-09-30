from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.services.classification_service import ClassificationResult


@dataclass(frozen=True)
class PriorityDecision:
    priority: str
    sla_hours: int
    sla_due_at: datetime
    reason: str


def decide_priority(
    classification: ClassificationResult,
    *,
    now: datetime | None = None,
) -> PriorityDecision:
    now = now or datetime.now(UTC)

    if classification.urgency == "urgent":
        priority = "urgent"
        sla_hours = 1
        reason = "Urgency classified as urgent; immediate response SLA applied."
    elif classification.urgency == "high":
        priority = "high"
        sla_hours = 4
        reason = "Urgency classified as high; accelerated response SLA applied."
    elif classification.urgency == "low":
        priority = "low"
        sla_hours = 24
        reason = "Urgency classified as low; standard low-priority SLA applied."
    elif classification.category in {"billing", "account"}:
        priority = "normal"
        sla_hours = 8
        reason = (
            f"{classification.category.title()} tickets receive an 8-hour response SLA "
            "when no higher urgency signal is present."
        )
    elif classification.category == "technical":
        priority = "normal"
        sla_hours = 6
        reason = (
            "Technical tickets receive a 6-hour response SLA when no higher urgency "
            "signal is present."
        )
    else:
        priority = "normal"
        sla_hours = 12
        reason = "Default support SLA applied because no higher-priority rule matched."

    return PriorityDecision(
        priority=priority,
        sla_hours=sla_hours,
        sla_due_at=now + timedelta(hours=sla_hours),
        reason=reason,
    )
