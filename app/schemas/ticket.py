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

    status: str
    created_at: datetime
    updated_at: datetime
