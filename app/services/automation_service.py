from app.integrations.n8n import WebhookResult, send_support_webhook
from app.models.ticket import Ticket


def build_support_event(ticket: Ticket) -> dict[str, object]:
    return {
        "event": "support.ticket.approved",
        "ticket": {
            "id": ticket.id,
            "customer_name": ticket.customer_name,
            "customer_email": ticket.customer_email,
            "subject": ticket.subject,
            "category": ticket.category,
            "priority": ticket.priority,
            "status": ticket.status,
            "sla_due_at": ticket.sla_due_at.isoformat() if ticket.sla_due_at else None,
            "approved_reply": ticket.approved_reply,
        },
        "review": {
            "reviewed_by": ticket.reviewed_by,
            "review_note": ticket.review_note,
            "reviewed_at": ticket.reviewed_at.isoformat() if ticket.reviewed_at else None,
        },
        "notifications": {
            "telegram_recommended": ticket.priority in {"urgent", "high"},
            "email_recommended": True,
        },
    }


def dispatch_approved_ticket(ticket: Ticket) -> WebhookResult:
    return send_support_webhook(build_support_event(ticket))
