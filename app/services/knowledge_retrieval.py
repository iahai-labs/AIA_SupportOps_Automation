from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.knowledge_article import KnowledgeArticle
from app.repositories.knowledge_repository import list_knowledge_articles

TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


@dataclass(frozen=True)
class RetrievedKnowledge:
    article_id: int
    title: str
    excerpt: str
    category: str
    source: str
    score: float


@dataclass(frozen=True)
class RetrievalResult:
    query: str
    confidence: float
    matches: list[RetrievedKnowledge]


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text) if len(token) > 2}


def _score_article(query_tokens: set[str], article: KnowledgeArticle) -> float:
    if not query_tokens:
        return 0.0

    title_tokens = _tokens(article.title)
    content_tokens = _tokens(article.content)
    category_tokens = _tokens(article.category)

    title_overlap = len(query_tokens & title_tokens)
    content_overlap = len(query_tokens & content_tokens)
    category_overlap = len(query_tokens & category_tokens)

    weighted_hits = (title_overlap * 3) + content_overlap + (category_overlap * 2)
    denominator = max(1, len(query_tokens) * 3)
    return min(1.0, weighted_hits / denominator)


def _excerpt(content: str, *, max_length: int = 280) -> str:
    clean = " ".join(content.split())
    if len(clean) <= max_length:
        return clean
    return f"{clean[:max_length - 1].rstrip()}…"


def retrieve_knowledge(
    db: Session,
    query: str,
    *,
    category: str | None = None,
    limit: int = 3,
    min_score: float = 0.05,
) -> RetrievalResult:
    query_tokens = _tokens(query)
    candidates = list_knowledge_articles(db)

    scored: list[tuple[KnowledgeArticle, float]] = []
    for article in candidates:
        score = _score_article(query_tokens, article)

        if category and category != "unknown" and article.category == category:
            score = min(1.0, score + 0.15)

        if score >= min_score:
            scored.append((article, score))

    scored.sort(key=lambda item: (-item[1], item[0].id))
    top = scored[: max(1, limit)]

    matches = [
        RetrievedKnowledge(
            article_id=article.id,
            title=article.title,
            excerpt=_excerpt(article.content),
            category=article.category,
            source=article.source,
            score=round(score, 4),
        )
        for article, score in top
    ]

    confidence = matches[0].score if matches else 0.0

    return RetrievalResult(
        query=query,
        confidence=confidence,
        matches=matches,
    )
