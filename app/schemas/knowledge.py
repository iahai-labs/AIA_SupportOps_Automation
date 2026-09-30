from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeArticleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=10, max_length=20_000)
    category: str = Field(default="general", min_length=1, max_length=32)
    source: str = Field(default="internal", min_length=1, max_length=255)


class KnowledgeArticleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    category: str
    source: str
    created_at: datetime
    updated_at: datetime


class KnowledgeMatch(BaseModel):
    article_id: int
    title: str
    excerpt: str
    category: str
    source: str
    score: float


class KnowledgeRetrievalResult(BaseModel):
    query: str
    confidence: float
    matches: list[KnowledgeMatch]
