import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.repositories.audit_repository import list_ticket_audit_events, record_audit_event
from app.repositories.ticket_repository import (
    create_ticket,
    get_ticket,
    save_automation_result,
    save_reply_draft,
    save_review_decision,
)
from app.schemas.audit import AuditEventRead
from app.schemas.knowledge import KnowledgeMatch, KnowledgeRetrievalResult
from app.schemas.ticket import (
    AutomationRetryRead,
    ReplyDraftRead,
    TicketApproveRequest,
    TicketCreate,
    TicketRead,
    TicketReviewRead,
    TicketReviewRequest,
)
from app.services.automation_service import dispatch_approved_ticket
from app.services.classification_service import classify_ticket
from app.services.knowledge_retrieval import retrieve_knowledge
from app.services.priority_service import decide_priority
from app.services.reliability_service import can_retry_automation
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
    ticket = create_ticket(db, payload, classification, priority)

    record_audit_event(
        db,
        ticket_id=ticket.id,
        event_type="ticket.created",
        details={
            "category": ticket.category,
            "priority": ticket.priority,
            "classification_source": ticket.classification_source,
        },
    )
    return ticket


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket_endpoint(ticket_id: int, db: Session = Depends(get_db)) -> TicketRead:
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.get("/{ticket_id}/audit", response_model=list[AuditEventRead])
def get_ticket_audit_endpoint(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> list[AuditEventRead]:
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return list_ticket_audit_events(db, ticket_id)


@router.get("/{ticket_id}/knowledge", response_model=KnowledgeRetrievalResult)
def get_ticket_knowledge_endpoint(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> KnowledgeRetrievalResult:
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    result = retrieve_knowledge(
        db,
        f"{ticket.subject} {ticket.message}",
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

    record_audit_event(
        db,
        ticket_id=saved.id,
        event_type="reply.drafted",
        details={
            "source": saved.reply_source,
            "confidence": saved.reply_confidence,
            "needs_human_review": saved.needs_human_review,
        },
    )

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
    record_audit_event(
        db,
        ticket_id=saved.id,
        event_type="review.approved",
        actor=saved.reviewed_by,
        details={"note": saved.review_note},
    )

    automation = dispatch_approved_ticket(saved)
    saved = save_automation_result(db, saved, automation)
    record_audit_event(
        db,
        ticket_id=saved.id,
        event_type=f"automation.{saved.automation_status}",
        details={
            "attempts": saved.automation_attempts,
            "last_error": saved.automation_last_error,
        },
    )

    return TicketReviewRead(
        ticket_id=saved.id,
        status=saved.status,
        approved_reply=saved.approved_reply,
        reviewed_by=saved.reviewed_by,
        review_note=saved.review_note,
        reviewed_at=saved.reviewed_at,
        automation_status=saved.automation_status,
        automation_attempts=saved.automation_attempts,
        automation_last_error=saved.automation_last_error,
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
    record_audit_event(
        db,
        ticket_id=saved.id,
        event_type="review.rejected",
        actor=saved.reviewed_by,
        details={"note": saved.review_note},
    )

    return TicketReviewRead(
        ticket_id=saved.id,
        status=saved.status,
        approved_reply=saved.approved_reply,
        reviewed_by=saved.reviewed_by,
        review_note=saved.review_note,
        reviewed_at=saved.reviewed_at,
        automation_status=saved.automation_status,
        automation_attempts=saved.automation_attempts,
        automation_last_error=saved.automation_last_error,
    )


@router.post("/{ticket_id}/automation/retry", response_model=AutomationRetryRead)
def retry_automation_endpoint(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> AutomationRetryRead:
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    decision = can_retry_automation(ticket)
    if not decision.allowed:
        raise HTTPException(status_code=409, detail=decision.reason)

    previous_attempts = ticket.automation_attempts
    result = dispatch_approved_ticket(ticket)
    result = type(result)(
        status=result.status,
        attempts=previous_attempts + result.attempts,
        last_error=result.last_error,
    )
    saved = save_automation_result(db, ticket, result)

    record_audit_event(
        db,
        ticket_id=saved.id,
        event_type=f"automation.retry.{saved.automation_status}",
        details={
            "attempts": saved.automation_attempts,
            "last_error": saved.automation_last_error,
        },
    )

    return AutomationRetryRead(
        ticket_id=saved.id,
        automation_status=saved.automation_status,
        automation_attempts=saved.automation_attempts,
        automation_last_error=saved.automation_last_error,
    )
