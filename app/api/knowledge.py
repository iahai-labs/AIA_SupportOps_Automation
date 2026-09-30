from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.repositories.knowledge_repository import create_knowledge_article
from app.schemas.knowledge import KnowledgeArticleCreate, KnowledgeArticleRead

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post(
    "",
    response_model=KnowledgeArticleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge_article_endpoint(
    payload: KnowledgeArticleCreate,
    db: Session = Depends(get_db),
) -> KnowledgeArticleRead:
    return create_knowledge_article(db, payload)
