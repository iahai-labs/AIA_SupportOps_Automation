from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.repositories.ticket_repository import create_ticket, get_ticket
from app.schemas.knowledge import KnowledgeMatch, KnowledgeRetrievalResult
from app.schemas.ticket import TicketCreate, TicketRead
from app.services.classification_service import classify_ticket
from app.services.knowledge_retrieval import retrieve_knowledge
from app.services.priority_service import decide_priority

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket_endpoint(
    payload: TicketCreate,
    db: Session = Depends(get_db),
) -> TicketRead:
    classification = classify_ticket(payload)
    priority = decide_priority(classification)
    return create_ticket(db, payload, classification, priority)


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket_endpoint(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> TicketRead:
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.get("/{ticket_id}/knowledge", response_model=KnowledgeRetrievalResult)
def get_ticket_knowledge_endpoint(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> KnowledgeRetrievalResult:
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    query = f"{ticket.subject} {ticket.message}"
    result = retrieve_knowledge(
        db,
        query,
        category=ticket.category,
    )

    return KnowledgeRetrievalResult(
        query=result.query,
        confidence=result.confidence,
        matches=[
            KnowledgeMatch(
                article_id=match.article_id,
                title=match.title,
                excerpt=match.excerpt,
                category=match.category,
                source=match.source,
                score=match.score,
            )
            for match in result.matches
        ],
    )
