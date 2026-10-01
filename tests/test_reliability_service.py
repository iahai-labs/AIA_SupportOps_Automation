from types import SimpleNamespace

from app.services.reliability_service import can_retry_automation


def test_failed_automation_can_retry() -> None:
    ticket = SimpleNamespace(status="approved", automation_status="failed")
    result = can_retry_automation(ticket)
    assert result.allowed is True


def test_skipped_automation_can_retry() -> None:
    ticket = SimpleNamespace(status="approved", automation_status="skipped")
    result = can_retry_automation(ticket)
    assert result.allowed is True


def test_sent_automation_is_blocked() -> None:
    ticket = SimpleNamespace(status="approved", automation_status="sent")
    result = can_retry_automation(ticket)
    assert result.allowed is False
    assert "already been sent" in result.reason


def test_nonapproved_ticket_cannot_retry() -> None:
    ticket = SimpleNamespace(status="rejected", automation_status="failed")
    result = can_retry_automation(ticket)
    assert result.allowed is False
