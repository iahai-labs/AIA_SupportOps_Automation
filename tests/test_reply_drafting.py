from app.services.knowledge_retrieval import RetrievalResult, RetrievedKnowledge
from app.services.reply_drafting import draft_reply


class FakeProvider:
    def complete_json(self, *, system_prompt: str, user_prompt: str) -> dict[str, object]:
        assert "using only the provided support knowledge" in system_prompt.lower()
        assert "Resetting your account password" in user_prompt
        return {
            "reply": (
                "Hi Sarah,\n\nPlease use the password reset link and then retry "
                "sign in in a new browser session.\n\nBest regards,\nSupport Team"
            ),
            "confidence": 0.9,
        }


class FailingProvider:
    def complete_json(self, *, system_prompt: str, user_prompt: str) -> dict[str, object]:
        raise RuntimeError("provider unavailable")


def sample_retrieval() -> RetrievalResult:
    return RetrievalResult(
        query="cannot sign in after password reset",
        confidence=0.8,
        matches=[
            RetrievedKnowledge(
                article_id=1,
                title="Resetting your account password",
                excerpt="Use the password reset link, then retry login in a new browser session.",
                category="account",
                source="support-handbook",
                score=0.8,
            )
        ],
    )


def test_grounded_ai_reply_uses_source_refs() -> None:
    result = draft_reply(
        customer_name="Sarah",
        subject="Cannot access account",
        message="I reset my password but still cannot sign in.",
        retrieval=sample_retrieval(),
        provider=FakeProvider(),
    )

    assert result.source == "ai"
    assert result.source_refs == ["Resetting your account password (support-handbook)"]
    assert result.confidence == 0.8
    assert result.needs_human_review is False


def test_ai_failure_uses_grounded_fallback() -> None:
    result = draft_reply(
        customer_name="Sarah",
        subject="Cannot access account",
        message="I reset my password but still cannot sign in.",
        retrieval=sample_retrieval(),
        provider=FailingProvider(),
    )

    assert result.source == "fallback"
    assert "password reset link" in result.reply
    assert result.source_refs


def test_no_knowledge_requires_human_review() -> None:
    result = draft_reply(
        customer_name="Alex",
        subject="Unknown issue",
        message="Something unusual happened.",
        retrieval=RetrievalResult(
            query="unknown issue",
            confidence=0.0,
            matches=[],
        ),
        provider=FakeProvider(),
    )

    assert result.source == "fallback"
    assert result.confidence == 0.2
    assert result.source_refs == []
    assert result.needs_human_review is True
    assert "support specialist" in result.reply.lower()
