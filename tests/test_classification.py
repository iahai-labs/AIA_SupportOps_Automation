from app.schemas.ticket import TicketCreate
from app.services.classification_service import classify_ticket


class FakeProvider:
    def complete_json(self, *, system_prompt: str, user_prompt: str) -> dict[str, object]:
        assert "classify inbound customer support tickets" in system_prompt.lower()
        assert "Cannot access my account" in user_prompt
        return {
            "category": "account",
            "urgency": "high",
            "language": "en",
            "summary": "Customer cannot access the account after a password reset.",
            "confidence": 0.94,
        }


def test_ai_classification_with_fake_provider() -> None:
    payload = TicketCreate(
        customer_name="Sarah Miller",
        customer_email="sarah@example.com",
        subject="Cannot access my account",
        message="I reset my password but I still cannot sign in.",
    )

    result = classify_ticket(payload, provider=FakeProvider())

    assert result.category == "account"
    assert result.urgency == "high"
    assert result.language == "en"
    assert result.confidence == 0.94
    assert result.source == "ai"


class FailingProvider:
    def complete_json(self, *, system_prompt: str, user_prompt: str) -> dict[str, object]:
        raise RuntimeError("provider unavailable")


def test_classification_falls_back_when_ai_fails() -> None:
    payload = TicketCreate(
        customer_name="Alex Smith",
        customer_email="alex@example.com",
        subject="Billing issue",
        message="I was charged twice and need a refund.",
    )

    result = classify_ticket(payload, provider=FailingProvider())

    assert result.category == "billing"
    assert result.source == "fallback"
    assert 0 <= result.confidence <= 1


def test_account_access_takes_precedence_over_generic_technical_terms() -> None:
    payload = TicketCreate(
        customer_name="Sarah Miller",
        customer_email="sarah@example.com",
        subject="Cannot access my account",
        message="I reset my password but I still cannot sign in.",
    )

    result = classify_ticket(payload, provider=FailingProvider())

    assert result.category == "account"
    assert result.source == "fallback"
