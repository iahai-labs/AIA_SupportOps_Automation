
from app.core.config import settings
from app.integrations.n8n import send_support_webhook
from app.services.knowledge_retrieval import RetrievalResult, RetrievedKnowledge
from app.services.reply_drafting import draft_reply


class ExplodingProvider:
    def complete_json(self, **kwargs):
        raise AssertionError("External AI must not be called in demo-safe mode")


def test_demo_safe_mode_blocks_external_automation(monkeypatch) -> None:
    monkeypatch.setattr(settings, "demo_safe_mode", True)
    monkeypatch.setattr(settings, "demo_allow_external_automation", False)
    monkeypatch.setattr(settings, "n8n_webhook_url", "https://example.invalid/webhook")

    result = send_support_webhook({"event": "test"})

    assert result.status == "skipped"
    assert result.attempts == 0


def test_demo_safe_mode_blocks_external_ai(monkeypatch) -> None:
    monkeypatch.setattr(settings, "demo_safe_mode", True)
    monkeypatch.setattr(settings, "demo_allow_external_ai", False)

    retrieval = RetrievalResult(
        query="password reset",
        confidence=0.8,
        matches=[
            RetrievedKnowledge(
                article_id=1,
                title="Reset password",
                excerpt="Use the password reset link.",
                category="account",
                source="support-handbook",
                score=0.8,
            )
        ],
    )

    result = draft_reply(
        customer_name="Sarah",
        subject="Login problem",
        message="I cannot sign in.",
        retrieval=retrieval,
        provider=ExplodingProvider(),
    )

    assert result.source == "fallback"
    assert "password reset link" in result.reply
