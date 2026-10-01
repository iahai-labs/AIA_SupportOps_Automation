from app.db.base import Base
from app.db.session import engine
from app.models import AuditEvent, KnowledgeArticle, Ticket  # noqa: F401


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
