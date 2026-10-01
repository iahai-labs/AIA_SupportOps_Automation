from dataclasses import dataclass

from app.models.ticket import Ticket


@dataclass(frozen=True)
class RetryDecision:
    allowed: bool
    reason: str


def can_retry_automation(ticket: Ticket) -> RetryDecision:
    if ticket.status != "approved":
        return RetryDecision(False, "Only approved tickets can retry automation")
    if ticket.automation_status == "sent":
        return RetryDecision(False, "Automation has already been sent")
    if ticket.automation_status not in {"failed", "skipped"}:
        return RetryDecision(False, "Automation is not in a retryable state")
    return RetryDecision(True, "Automation can be retried")
