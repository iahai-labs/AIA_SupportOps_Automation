from app.repositories.knowledge_repository import create_knowledge_article
from app.schemas.knowledge import KnowledgeArticleCreate
from app.services.knowledge_retrieval import retrieve_knowledge


def seed_articles(db_session) -> None:
    create_knowledge_article(
        db_session,
        KnowledgeArticleCreate(
            title="Resetting your account password",
            content=(
                "If a customer cannot sign in, ask them to use the password reset link. "
                "After resetting, they should retry login in a new browser session."
            ),
            category="account",
            source="support-handbook",
        ),
    )
    create_knowledge_article(
        db_session,
        KnowledgeArticleCreate(
            title="Refund policy",
            content=(
                "Refund requests for duplicate charges should be reviewed by billing "
                "within five business days."
            ),
            category="billing",
            source="billing-policy",
        ),
    )


def test_retrieval_returns_relevant_article(db_session) -> None:
    seed_articles(db_session)

    result = retrieve_knowledge(
        db_session,
        "customer cannot sign in after password reset",
        category="account",
    )

    assert result.matches
    assert result.matches[0].title == "Resetting your account password"
    assert result.matches[0].source == "support-handbook"
    assert result.confidence > 0


def test_retrieval_returns_no_results_when_nothing_matches(db_session) -> None:
    seed_articles(db_session)

    result = retrieve_knowledge(
        db_session,
        "quantum satellite antenna calibration",
        category="unknown",
    )

    assert result.matches == []
    assert result.confidence == 0.0


def test_category_match_can_boost_relevance(db_session) -> None:
    seed_articles(db_session)

    result = retrieve_knowledge(
        db_session,
        "duplicate charge refund",
        category="billing",
    )

    assert result.matches
    assert result.matches[0].category == "billing"
