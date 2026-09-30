import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.repositories.ticket_repository import (
    create_ticket,
    get_ticket,
    save_reply_draft,
    save_review_decision,
)
from app.schemas.knowledge import KnowledgeMatch, KnowledgeRetrievalResult
from app.schemas.ticket import (
    ReplyDraftRead,
    TicketApproveRequest,
    TicketCreate,
    TicketRead,
    TicketReviewRead,
    TicketReviewRequest,
)
from app.services.classification_service import classify_ticket
from app.services.knowledge_retrieval import retrieve_knowledge
from app.services.priority_service import decide_priority
from app.services.reply_drafting import draft_reply
from app.services.review_service import approve_ticket, reject_ticket

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


@router.post("/{ticket_id}/draft", response_model=ReplyDraftRead)
def create_reply_draft_endpoint(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> ReplyDraftRead:
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    retrieval = retrieve_knowledge(
        db,
        f"{ticket.subject} {ticket.message}",
        category=ticket.category,
    )
    draft = draft_reply(
        customer_name=ticket.customer_name,
        subject=ticket.subject,
        message=ticket.message,
        retrieval=retrieval,
    )
    saved = save_reply_draft(db, ticket, draft)

    return ReplyDraftRead(
        ticket_id=saved.id,
        reply=saved.draft_reply,
        confidence=saved.reply_confidence,
        source_refs=json.loads(saved.reply_source_refs),
        source=saved.reply_source,
        needs_human_review=saved.needs_human_review,
    )


@router.post("/{ticket_id}/approve", response_model=TicketReviewRead)
def approve_ticket_endpoint(
    ticket_id: int,
    payload: TicketApproveRequest,
    db: Session = Depends(get_db),
) -> TicketReviewRead:
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    try:
        decision = approve_ticket(
            ticket,
            reviewed_by=payload.reviewed_by,
            note=payload.note,
            approved_reply=payload.approved_reply,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    saved = save_review_decision(db, ticket, decision)

    return TicketReviewRead(
        ticket_id=saved.id,
        status=saved.status,
        approved_reply=saved.approved_reply,
        reviewed_by=saved.reviewed_by,
        review_note=saved.review_note,
        reviewed_at=saved.reviewed_at,
    )


@router.post("/{ticket_id}/reject", response_model=TicketReviewRead)
def reject_ticket_endpoint(
    ticket_id: int,
    payload: TicketReviewRequest,
    db: Session = Depends(get_db),
) -> TicketReviewRead:
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    try:
        decision = reject_ticket(
            ticket,
            reviewed_by=payload.reviewed_by,
            note=payload.note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    saved = save_review_decision(db, ticket, decision)

    return TicketReviewRead(
        ticket_id=saved.id,
        status=saved.status,
        approved_reply=saved.approved_reply,
        reviewed_by=saved.reviewed_by,
        review_note=saved.review_note,
        reviewed_at=saved.reviewed_at,
    )
