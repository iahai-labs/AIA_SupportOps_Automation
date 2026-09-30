from types import SimpleNamespace

import pytest

from app.services.review_service import approve_ticket, reject_ticket


def waiting_ticket(draft_reply: str = "Draft response"):
    return SimpleNamespace(status="waiting_review", draft_reply=draft_reply)


def test_approve_uses_existing_draft_by_default() -> None:
    decision = approve_ticket(
        waiting_ticket(),
        reviewed_by="Support Agent",
        note="Looks good.",
    )

    assert decision.status == "approved"
    assert decision.approved_reply == "Draft response"
    assert decision.reviewed_by == "Support Agent"


def test_approve_can_replace_draft() -> None:
    decision = approve_ticket(
        waiting_ticket(),
        reviewed_by="Support Agent",
        approved_reply="Edited final response",
    )

    assert decision.approved_reply == "Edited final response"


def test_reject_marks_ticket_rejected() -> None:
    decision = reject_ticket(
        waiting_ticket(),
        reviewed_by="Support Lead",
        note="Needs more investigation.",
    )

    assert decision.status == "rejected"
    assert decision.approved_reply == ""
    assert decision.review_note == "Needs more investigation."


def test_review_rejects_invalid_ticket_state() -> None:
    ticket = SimpleNamespace(status="new", draft_reply="")

    with pytest.raises(ValueError):
        approve_ticket(ticket, reviewed_by="Support Agent")

    with pytest.raises(ValueError):
        reject_ticket(ticket, reviewed_by="Support Agent")
