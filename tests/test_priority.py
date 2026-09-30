from datetime import UTC, datetime

from app.services.classification_service import ClassificationResult
from app.services.priority_service import decide_priority

NOW = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)


def make_classification(*, category: str, urgency: str) -> ClassificationResult:
    return ClassificationResult(
        category=category,
        urgency=urgency,
        language="en",
        summary="Example",
        confidence=0.9,
        source="ai",
    )


def test_urgent_ticket_gets_one_hour_sla() -> None:
    result = decide_priority(
        make_classification(category="technical", urgency="urgent"),
        now=NOW,
    )

    assert result.priority == "urgent"
    assert result.sla_hours == 1
    assert result.sla_due_at == datetime(2026, 9, 30, 13, 0, tzinfo=UTC)
    assert "urgent" in result.reason.lower()


def test_high_ticket_gets_four_hour_sla() -> None:
    result = decide_priority(
        make_classification(category="billing", urgency="high"),
        now=NOW,
    )

    assert result.priority == "high"
    assert result.sla_hours == 4


def test_account_ticket_without_high_urgency_gets_eight_hour_sla() -> None:
    result = decide_priority(
        make_classification(category="account", urgency="normal"),
        now=NOW,
    )

    assert result.priority == "normal"
    assert result.sla_hours == 8
    assert "account" in result.reason.lower()


def test_technical_ticket_without_high_urgency_gets_six_hour_sla() -> None:
    result = decide_priority(
        make_classification(category="technical", urgency="normal"),
        now=NOW,
    )

    assert result.priority == "normal"
    assert result.sla_hours == 6


def test_low_urgency_overrides_category_default() -> None:
    result = decide_priority(
        make_classification(category="billing", urgency="low"),
        now=NOW,
    )

    assert result.priority == "low"
    assert result.sla_hours == 24


def test_general_ticket_uses_default_sla() -> None:
    result = decide_priority(
        make_classification(category="general", urgency="normal"),
        now=NOW,
    )

    assert result.priority == "normal"
    assert result.sla_hours == 12
