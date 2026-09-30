from __future__ import annotations

from dataclasses import dataclass

from app.integrations.llm import LLMProvider, OpenAICompatibleProvider
from app.schemas.ticket import TicketCreate

ALLOWED_CATEGORIES = {"billing", "technical", "sales", "account", "general", "unknown"}
ALLOWED_URGENCY = {"low", "normal", "high", "urgent", "unknown"}

SYSTEM_PROMPT = '''
You classify inbound customer support tickets.

Return exactly one JSON object with:
- category
- urgency
- language
- summary
- confidence

Rules:
- category must be one of: billing, technical, sales, account, general, unknown
- urgency must be one of: low, normal, high, urgent, unknown
- language should be a short language code such as en, fa, de, or unknown
- summary must be concise and factual
- confidence must be a number from 0 to 1
- do not invent facts not present in the ticket
'''.strip()


@dataclass(frozen=True)
class ClassificationResult:
    category: str
    urgency: str
    language: str
    summary: str
    confidence: float
    source: str


def _normalize_label(value: object, *, allowed: set[str], default: str) -> str:
    normalized = str(value or "").strip().lower()
    return normalized if normalized in allowed else default


def _safe_confidence(value: object) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, confidence))


def _fallback_classification(payload: TicketCreate) -> ClassificationResult:
    text = f"{payload.subject} {payload.message}".lower()

    # Order matters: account-access language is more specific than generic
    # technical wording such as "issue" or "not working".
    category = "general"
    category_tokens = (
        ("account", ("login", "password", "account", "sign in", "signin", "access")),
        ("billing", ("invoice", "billing", "refund", "payment", "charge")),
        ("sales", ("pricing", "quote", "proposal", "buy", "purchase", "plan")),
        ("technical", ("error", "bug", "broken", "not working", "technical issue", "issue")),
    )
    for candidate, tokens in category_tokens:
        if any(token in text for token in tokens):
            category = candidate
            break

    urgency = "normal"
    if any(token in text for token in ("urgent", "asap", "immediately", "critical")):
        urgency = "urgent"
    elif any(token in text for token in ("today", "soon", "high priority")):
        urgency = "high"

    language = "en" if f"{payload.subject}{payload.message}".isascii() else "unknown"
    summary = payload.message.strip()[:300]

    return ClassificationResult(
        category=category,
        urgency=urgency,
        language=language,
        summary=summary,
        confidence=0.55,
        source="fallback",
    )


def classify_ticket(
    payload: TicketCreate,
    provider: LLMProvider | None = None,
) -> ClassificationResult:
    provider = provider or OpenAICompatibleProvider()

    user_prompt = (
        f"Subject: {payload.subject}\n"
        f"Message: {payload.message}\n"
        f"Customer: {payload.customer_name}"
    )

    try:
        raw = provider.complete_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        return ClassificationResult(
            category=_normalize_label(
                raw.get("category"),
                allowed=ALLOWED_CATEGORIES,
                default="unknown",
            ),
            urgency=_normalize_label(
                raw.get("urgency"),
                allowed=ALLOWED_URGENCY,
                default="unknown",
            ),
            language=str(raw.get("language") or "unknown").strip().lower()[:16],
            summary=str(raw.get("summary") or payload.message).strip()[:500],
            confidence=_safe_confidence(raw.get("confidence")),
            source="ai",
        )
    except Exception:
        return _fallback_classification(payload)
