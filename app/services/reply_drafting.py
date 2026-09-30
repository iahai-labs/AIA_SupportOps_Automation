from __future__ import annotations

from dataclasses import dataclass

from app.integrations.llm import LLMProvider, OpenAICompatibleProvider
from app.services.knowledge_retrieval import RetrievalResult

SYSTEM_PROMPT = """
You draft customer support replies using only the provided support knowledge.

Return exactly one JSON object with:
- reply
- confidence

Rules:
- never invent policy, technical facts, timelines, refunds, guarantees, or account actions
- use only facts supported by the supplied knowledge context
- if the context is insufficient, explicitly say the issue needs human review
- keep the tone professional, concise, and helpful
- confidence must be a number from 0 to 1
""".strip()


@dataclass(frozen=True)
class ReplyDraftResult:
    reply: str
    confidence: float
    source_refs: list[str]
    source: str
    needs_human_review: bool


def _safe_confidence(value: object) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, confidence))


def _source_refs(retrieval: RetrievalResult) -> list[str]:
    return [f"{match.title} ({match.source})" for match in retrieval.matches]


def _fallback_reply(
    *,
    customer_name: str,
    retrieval: RetrievalResult,
) -> ReplyDraftResult:
    refs = _source_refs(retrieval)

    if not retrieval.matches:
        return ReplyDraftResult(
            reply=(
                f"Hi {customer_name},\n\n"
                "Thanks for contacting support. I do not have enough verified knowledge "
                "to give you a reliable answer yet. Your request should be reviewed by "
                "a support specialist before a response is sent.\n\n"
                "Best regards,\nSupport Team"
            ),
            confidence=0.2,
            source_refs=[],
            source="fallback",
            needs_human_review=True,
        )

    best = retrieval.matches[0]
    return ReplyDraftResult(
        reply=(
            f"Hi {customer_name},\n\n"
            "Thanks for contacting support. Based on our support documentation:\n\n"
            f"{best.excerpt}\n\n"
            "If this does not resolve the issue, a support specialist should review "
            "the case before any further action is taken.\n\n"
            "Best regards,\nSupport Team"
        ),
        confidence=min(0.75, max(0.35, retrieval.confidence)),
        source_refs=refs,
        source="fallback",
        needs_human_review=retrieval.confidence < 0.45,
    )


def draft_reply(
    *,
    customer_name: str,
    subject: str,
    message: str,
    retrieval: RetrievalResult,
    provider: LLMProvider | None = None,
) -> ReplyDraftResult:
    if not retrieval.matches:
        return _fallback_reply(
            customer_name=customer_name,
            retrieval=retrieval,
        )

    provider = provider or OpenAICompatibleProvider()

    context_blocks = []
    for index, match in enumerate(retrieval.matches, start=1):
        context_blocks.append(
            f"[Source {index}]\n"
            f"Title: {match.title}\n"
            f"Origin: {match.source}\n"
            f"Content: {match.excerpt}"
        )

    user_prompt = (
        f"Customer: {customer_name}\n"
        f"Subject: {subject}\n"
        f"Message: {message}\n\n"
        "Verified support knowledge:\n"
        + "\n\n".join(context_blocks)
    )

    try:
        raw = provider.complete_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
        reply = str(raw.get("reply") or "").strip()
        if not reply:
            raise ValueError("AI reply is empty")

        confidence = _safe_confidence(raw.get("confidence"))
        confidence = min(confidence, max(0.0, retrieval.confidence))

        return ReplyDraftResult(
            reply=reply[:5000],
            confidence=confidence,
            source_refs=_source_refs(retrieval),
            source="ai",
            needs_human_review=confidence < 0.45,
        )
    except Exception:
        return _fallback_reply(
            customer_name=customer_name,
            retrieval=retrieval,
        )
