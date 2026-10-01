import json

from sqlalchemy.orm import Session

from app.integrations.n8n import WebhookResult
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate
from app.services.classification_service import ClassificationResult
from app.services.priority_service import PriorityDecision
from app.services.reply_drafting import ReplyDraftResult
from app.services.review_service import ReviewDecision


def create_ticket(
    db: Session,
    payload: TicketCreate,
    classification: ClassificationResult,
    priority: PriorityDecision,
) -> Ticket:
    ticket = Ticket(
        customer_name=payload.customer_name.strip(),
        customer_email=str(payload.customer_email).lower(),
        subject=payload.subject.strip(),
        message=payload.message.strip(),
        category=classification.category,
        urgency=classification.urgency,
        language=classification.language,
        summary=classification.summary,
        classification_confidence=classification.confidence,
        classification_source=classification.source,
        priority=priority.priority,
        sla_hours=priority.sla_hours,
        sla_due_at=priority.sla_due_at,
        priority_reason=priority.reason,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_ticket(db: Session, ticket_id: int) -> Ticket | None:
    return db.get(Ticket, ticket_id)


def save_reply_draft(
    db: Session,
    ticket: Ticket,
    draft: ReplyDraftResult,
) -> Ticket:
    ticket.draft_reply = draft.reply
    ticket.reply_confidence = draft.confidence
    ticket.reply_source = draft.source
    ticket.reply_source_refs = json.dumps(draft.source_refs)
    ticket.needs_human_review = draft.needs_human_review
    ticket.status = "waiting_review"

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def save_review_decision(
    db: Session,
    ticket: Ticket,
    decision: ReviewDecision,
) -> Ticket:
    ticket.status = decision.status
    ticket.approved_reply = decision.approved_reply
    ticket.reviewed_by = decision.reviewed_by
    ticket.review_note = decision.review_note
    ticket.reviewed_at = decision.reviewed_at

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def save_automation_result(
    db: Session,
    ticket: Ticket,
    result: WebhookResult,
) -> Ticket:
    ticket.automation_status = result.status
    ticket.automation_attempts = result.attempts
    ticket.automation_last_error = result.last_error or ""

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket
