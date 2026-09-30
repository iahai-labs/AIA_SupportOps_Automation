from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TicketCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=120)
    customer_email: EmailStr
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=3, max_length=5000)


class TicketClassification(BaseModel):
    category: str
    urgency: str
    language: str
    summary: str
    confidence: float
    source: str


class ReplyDraftRead(BaseModel):
    ticket_id: int
    reply: str
    confidence: float
    source_refs: list[str]
    source: str
    needs_human_review: bool


class TicketReviewRequest(BaseModel):
    reviewed_by: str = Field(min_length=1, max_length=120)
    note: str = Field(default="", max_length=1000)


class TicketApproveRequest(TicketReviewRequest):
    approved_reply: str | None = Field(default=None, max_length=5000)


class TicketReviewRead(BaseModel):
    ticket_id: int
    status: str
    approved_reply: str
    reviewed_by: str
    review_note: str
    reviewed_at: datetime


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    customer_email: EmailStr
    subject: str
    message: str

    category: str
    urgency: str
    language: str
    summary: str
    classification_confidence: float
    classification_source: str

    priority: str
    sla_hours: int
    sla_due_at: datetime | None
    priority_reason: str

    draft_reply: str
    reply_confidence: float
    reply_source: str
    reply_source_refs: str
    needs_human_review: bool

    approved_reply: str
    reviewed_by: str
    review_note: str
    reviewed_at: datetime | None

    status: str
    created_at: datetime
    updated_at: datetime
