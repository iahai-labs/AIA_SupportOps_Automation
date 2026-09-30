from types import SimpleNamespace

from app.services.automation_service import build_support_event


def test_high_priority_recommends_telegram() -> None:
    ticket = SimpleNamespace(
        id=7,
        customer_name="Sarah",
        customer_email="sarah@example.com",
        subject="Critical access issue",
        category="account",
        priority="high",
        status="approved",
        sla_due_at=None,
        approved_reply="Final answer",
        reviewed_by="Support Agent",
        review_note="Verified",
        reviewed_at=None,
    )

    payload = build_support_event(ticket)

    assert payload["event"] == "support.ticket.approved"
    assert payload["notifications"]["telegram_recommended"] is True


def test_normal_priority_does_not_recommend_telegram() -> None:
    ticket = SimpleNamespace(
        id=8,
        customer_name="Alex",
        customer_email="alex@example.com",
        subject="General question",
        category="general",
        priority="normal",
        status="approved",
        sla_due_at=None,
        approved_reply="Final answer",
        reviewed_by="Support Agent",
        review_note="",
        reviewed_at=None,
    )

    payload = build_support_event(ticket)

    assert payload["notifications"]["telegram_recommended"] is False
