import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


def record_audit_event(
    db: Session,
    *,
    ticket_id: int,
    event_type: str,
    actor: str = "system",
    details: dict[str, object] | None = None,
) -> AuditEvent:
    event = AuditEvent(
        ticket_id=ticket_id,
        event_type=event_type,
        actor=actor,
        details=json.dumps(details or {}, sort_keys=True),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_ticket_audit_events(db: Session, ticket_id: int) -> list[AuditEvent]:
    return list(
        db.scalars(
            select(AuditEvent)
            .where(AuditEvent.ticket_id == ticket_id)
            .order_by(AuditEvent.id.asc())
        ).all()
    )
