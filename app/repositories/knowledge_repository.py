from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_article import KnowledgeArticle
from app.schemas.knowledge import KnowledgeArticleCreate


def create_knowledge_article(
    db: Session,
    payload: KnowledgeArticleCreate,
) -> KnowledgeArticle:
    article = KnowledgeArticle(
        title=payload.title.strip(),
        content=payload.content.strip(),
        category=payload.category.strip().lower(),
        source=payload.source.strip(),
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def list_knowledge_articles(db: Session) -> list[KnowledgeArticle]:
    return list(
        db.scalars(
            select(KnowledgeArticle).order_by(KnowledgeArticle.id.asc())
        ).all()
    )
